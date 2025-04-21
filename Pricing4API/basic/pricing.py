# Pricing4API/basic/pricing.py

from typing import List, Union, Optional
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from matplotlib.colors import to_rgba
from Pricing4API.ancillary.time_unit import TimeDuration, TimeUnit
from Pricing4API.utils import parse_time_string_to_duration, select_best_time_unit
from Pricing4API.basic.plan_and_demand import Plan
from Pricing4API.basic.bounded_rate import BoundedRate, Quota, Rate
from Pricing4API.basic.compare_curves import (
    compare_bounded_rates_capacity,
    update_legend_names
)


class Pricing:
    def __init__(self, plans: List[Plan]):
        # Guardamos copia de los planes "base" antes de inyectar pseudocuotas
        self.base_plans = plans[:]

        # *** Guardamos los bounded_rates ORIGINALES para no‐overage ***
        self._original_brs = {}
        for plan in self.base_plans:
            br = plan.bounded_rate
            quotas = None if br.quota is None else br.quota.copy()
            self._original_brs[plan] = BoundedRate(br.rate, quotas, br.max_active_time)

        # ahora sí, preparamos pseudocuotas sobre los br originales
        self.plans = plans
        self._inject_overage_quotas()

    def _inject_overage_quotas(self):
        """
        Para cada plan, reemplaza su última cuota real por una pseudocuota:
          - si existe un plan siguiente: 4× la última cuota de ese siguiente plan
          - si no (último plan): 6× su propia última cuota
        y almacena la real en plan.max_included_quota.
        """
        sorted_plans = sorted(
            self.plans,
            key=lambda p: p.bounded_rate.limits[-1].consumption_unit
        )
        for idx, plan in enumerate(sorted_plans):
            br = plan.bounded_rate
            real = br.limits[-1]
            plan.max_included_quota = real.consumption_unit

            if idx < len(sorted_plans) - 1:
                next_units = sorted_plans[idx + 1].bounded_rate.limits[-1].consumption_unit
                fict = next_units * 4
            else:
                fict = real.consumption_unit * 6

            br.limits[-1] = Quota(fict, real.consumption_period)

    def _compute_default_interval(self) -> TimeDuration:
        max_ms = 0
        for p in self.plans:
            br = p.bounded_rate
            ms = br.limits[-1].consumption_period.to_milliseconds()
            if br.max_active_time:
                ms = max(ms, br.max_active_time.to_milliseconds())
            max_ms = max(max_ms, ms)
        return select_best_time_unit(max_ms)

    def show_capacity(
        self,
        time_interval: Union[str, TimeDuration, None] = None,
        *,
        return_fig: bool = False
    ):
        if time_interval is None:
            time_interval = self._compute_default_interval()
        elif isinstance(time_interval, str):
            time_interval = parse_time_string_to_duration(time_interval)

        fig = compare_bounded_rates_capacity(
            bounded_rates=[p.bounded_rate for p in self.plans],
            time_interval=time_interval,
            return_fig=True
        )
        update_legend_names(fig, [p.name for p in self.plans])

        if return_fig:
            return fig
        fig.show()

    def show_capacity_and_cost_no_overage(
        self,
        time_interval: Union[str, TimeDuration, None] = None,
        *,
        return_fig: bool = False
    ):
        """
        Pinta:
          - Izq: curvas de capacidad SOLO de los planes base (sin overage), sólidas y con relleno.
          - Der: coste vs requests, líneas horizontales al coste base de cada plan.
        """
        if time_interval is None:
            time_interval = self._compute_default_interval()
        elif isinstance(time_interval, str):
            time_interval = parse_time_string_to_duration(time_interval)

        palette = ["green", "purple", "blue", "orange", "red", "teal"]
        colors = palette[: len(self.base_plans)]

        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Capacity Curves", "Flat Cost"),
            column_widths=[0.6, 0.4]
        )

        # — Capacity (solo originales) con fill bajo la curva —
        for idx, plan in enumerate(self.base_plans):
            col = colors[idx]
            orig_br = self._original_brs[plan]
            pts = orig_br.show_available_capacity_curve(time_interval, debug=True)
            times, caps = zip(*pts)
            xs = [t / time_interval.unit.to_milliseconds() for t in times]

            rgba = to_rgba(col)
            fillcolor = f"rgba({int(rgba[0]*255)},{int(rgba[1]*255)},{int(rgba[2]*255)},0.3)"

            fig.add_trace(
                go.Scatter(
                    x=xs, y=caps,
                    mode="lines",
                    line=dict(color=col, dash="solid", width=2),
                    fill="tozeroy",
                    fillcolor=fillcolor,
                    name=plan.name,
                    showlegend=True
                ),
                row=1, col=1
            )

        fig.update_xaxes(title_text=f"Time ({time_interval.unit.value})", row=1, col=1)
        fig.update_yaxes(title_text="Capacity",                    row=1, col=1)

        # — Flat Cost — (horizontales al coste base)
        for idx, plan in enumerate(self.base_plans):
            col = colors[idx]
            orig_br = self._original_brs[plan]
            cap_max = int(orig_br.capacity_at(time_interval))
            xs = [0, cap_max]
            ys = [plan.cost, plan.cost]

            fig.add_trace(
                go.Scatter(
                    x=xs, y=ys,
                    mode="lines",
                    line=dict(color=col, dash="solid", width=3),
                    name=f"{plan.name} cost",
                    showlegend=True
                ),
                row=1, col=2
            )

        fig.update_xaxes(title_text="Requests", row=1, col=2)
        fig.update_yaxes(title_text="Cost",     row=1, col=2)

        fig.update_layout(
            template="plotly_white",
            width=1200, height=500,
            legend_title="Plans",
            legend=dict(traceorder="normal")
        )

        if return_fig:
            return fig
        fig.show()

    def show_capacity_and_cost(
        self,
        time_interval: Union[str, TimeDuration, None] = None,
        *,
        desired_demand: Optional[int] = None,
        return_fig: bool = False
    ):
        """
        Igual que antes, pero si se pasa `desired_demand`:
          - Izq: dibuja hline en y = desired_demand y calcula para cada plan
            el tiempo mínimo (usando bounded_rate.min_time) para alcanzarlo.
          - Drch: dibuja vline en x = desired_demand y calcula el coste
            para cada plan en ese número de peticiones.
        """
        if time_interval is None:
            time_interval = self._compute_default_interval()
        elif isinstance(time_interval, str):
            time_interval = parse_time_string_to_duration(time_interval)

        palette = ["green", "purple", "blue", "orange", "red", "teal"]
        colors = palette[: len(self.plans)]

        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Capacity Curves", "Cost vs Requests"),
            column_widths=[0.6, 0.4]
        )

        # — Capacity subplot —
        fig_cap = compare_bounded_rates_capacity(
            bounded_rates=[p.bounded_rate for p in self.plans],
            time_interval=time_interval,
            return_fig=True
        )
        #update_legend_names(fig_cap, ["Plan Mega", "Plan Pro", "Plan Ultra"])
        update_legend_names(fig_cap, [p.name for p in self.plans])

        acc_traces = [tr for tr in fig_cap.data if tr.showlegend]
        for idx, tr in enumerate(acc_traces):
            limit = next(p.max_included_quota for p in self.plans if p.name == tr.legendgroup)
            if any(y > limit for y in tr.y):
                tr.line.dash = "dash"
            tr.line.color = colors[idx]  # Aseguramos que el color sea consistente
            fig.add_trace(tr, row=1, col=1)

        # si se pide desired_demand, trazo horizontal y calculo tiempos
        if desired_demand is not None:
            fig.add_hline(
                y=desired_demand,
                line=dict(color="black", dash="dot"),
                annotation_text=f"Demand={desired_demand}",
                row=1, col=1
            )
            # imprimir tiempos
            for idx, plan in enumerate(self.plans):
                try:
                    t_str = plan.bounded_rate.min_time(desired_demand)
                except Exception:
                    t_str = "no alcanzable"
                print(f"{plan.name}: time to reach {desired_demand} = {t_str}")

        fig.update_xaxes(title_text=fig_cap.layout.xaxis.title.text, row=1, col=1)
        fig.update_yaxes(title_text=fig_cap.layout.yaxis.title.text, row=1, col=1)

        # — Cost subplot —
        for idx, plan in enumerate(self.plans):
            col = colors[idx]
            max_req = int(plan.bounded_rate.capacity_at(time_interval))
            xs = list(range(max_req + 1))
            base = plan.cost
            over = plan.overage_cost or 0
            limit = plan.max_included_quota
            ys = [base + max(0, x - limit) * over for x in xs]

            fig.add_trace(
                go.Scatter(
                    x=xs, y=ys,
                    mode="lines",
                    line=dict(color=col, dash="solid", width=2),
                    name=f"{plan.name} cost"
                ),
                row=1, col=2
            )

        # si se pide desired_demand, trazo vertical y calculo costes
        if desired_demand is not None:
            fig.add_vline(
                x=desired_demand,
                line=dict(color="black", dash="dot"),
                annotation_text=f"Demand={desired_demand}",
                row=1, col=2
            )
            for plan in self.plans:
                cost_at = plan.cost + max(0, desired_demand - plan.max_included_quota) * (plan.overage_cost or 0)
                print(f"{plan.name}: cost at {desired_demand} = {cost_at:.2f}")

        fig.update_xaxes(title_text="Requests", row=1, col=2)
        fig.update_yaxes(title_text="Cost",     row=1, col=2)

        fig.update_layout(
            template="plotly_white",
            width=1200, height=500,
            legend_title="Plans"
        )

        if return_fig:
            return fig
        fig.show()


if __name__ == "__main__":
    # Ejemplo
    br1 = BoundedRate(Rate(10, "1s"), Quota(40000, "1month"))
    plan1 = Plan("Plan Pro", br1, cost=9.95, overage_cost=0.001,
                 max_number_of_subscriptions=1, billing_period="1month")

    br2 = BoundedRate(Rate(10, "1s"), Quota(100000, "1month"))
    plan2 = Plan("Plan Ultra", br2, cost=79.95, overage_cost=0.00085,
                 max_number_of_subscriptions=1, billing_period="1month")
    
    br3 = BoundedRate(Rate(50, "1s"), Quota(300000, "1month"))
    plan3 = Plan("Plan Mega", br3, cost=199.95, overage_cost=0.0005,
                 max_number_of_subscriptions=1, billing_period="1month")

    pricing = Pricing([plan1, plan2, plan3])
    # genera figura y devuelve
    fig = pricing.show_capacity_and_cost("1day", desired_demand=250000, return_fig=True)
    #update_legend_names(fig, ["Plan Mega", "Plan Ultra", "Plan Pro", "Plan Pro Cost", "Plan Ultra Cost", "Plan Mega Cost"])
    fig.show()

