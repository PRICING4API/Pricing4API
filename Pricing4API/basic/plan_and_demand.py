from typing import List, Union
from Pricing4API.ancillary.time_unit import TimeDuration, TimeUnit
from Pricing4API.basic.bounded_rate import BoundedRate, Rate, Quota
from Pricing4API.utils import parse_time_string_to_duration, select_best_time_unit
from Pricing4API.basic.compare_curves import compare_bounded_rates_capacity


class Plan():
    def __init__(self, name, bounded_rate: BoundedRate, cost, overage_cost, max_number_of_subscriptions, billing_period):
        self.name = name
        self.bounded_rate = bounded_rate
        self.cost = cost
        self.overage_cost = overage_cost
        self.max_number_of_subscriptions = max_number_of_subscriptions
        self.billing_period = billing_period

    def show_capacity(self, time_interval: Union[str, TimeDuration]):
        if isinstance(time_interval, str):
            time_interval = parse_time_string_to_duration(time_interval)
        
        return self.bounded_rate.show_capacity(time_interval)

    def consume(self, demand: 'Demand', time_interval: Union[str, TimeDuration]):
        """
        Consumes demand over a specified time interval, comparing bounded rates.

        Args:
            demand (Demand): The demand to consume.
            time_interval (Union[str, TimeDuration]): The time interval for consumption.
        """
        if isinstance(time_interval, str):
            time_interval = parse_time_string_to_duration(time_interval)

        # Compare the bounded rates of the plan and the demand
        compare_bounded_rates_capacity(
            bounded_rates=[self.bounded_rate, demand.bounded_rate],
            time_interval=time_interval
        )
    
    def has_enough_capacity(self, demand: 'Demand') -> bool:
            print("\n=== Análisis de capacidad del plan frente a la demanda ===\n")

            # === 0) Chequeo de velocidad instantánea ===
            plan_rate = self.bounded_rate.rate
            d_rate    = demand.bounded_rate.rate
            v_plan = plan_rate.consumption_unit / plan_rate.consumption_period.to_milliseconds()
            v_dem  = d_rate.consumption_unit    / d_rate.consumption_period.to_milliseconds()
            print(f"- Velocidad plan:  {plan_rate.consumption_unit}/{plan_rate.consumption_period} "
                f"→ {v_plan:.6f} pet/ms")
            print(f"- Velocidad demanda: {d_rate.consumption_unit}/{d_rate.consumption_period} "
                f"→ {v_dem:.6f} pet/ms")
            if v_dem > v_plan:
                print("✘ La demanda es demasiado rápida en el corto plazo (v_dem > v_plan). ¡No cabe!\n")
                return False

            # === 1) Chequeo de cuotas comparadas ===
            plan_quotas   = self.bounded_rate.limits[1:]
            demand_quotas = demand.bounded_rate.limits[1:]
            for q_d in demand_quotas:
                for q_p in plan_quotas:
                    ms_d = q_d.consumption_period.to_milliseconds()
                    ms_p = q_p.consumption_period.to_milliseconds()
                    if ms_d >= ms_p:
                        # escalo cuota demanda a periodo del plan
                        scaled = q_d.consumption_unit * (ms_p / ms_d)
                        if scaled > q_p.consumption_unit:
                            print(f"✘ La cuota de demanda {q_d} equivale a {scaled:.1f} en {q_p.consumption_period}, "
                                f"supera la cuota del plan {q_p}.\n")
                            return False
                    else:
                        # escalo cuota plan a periodo de la demanda
                        scaled = q_p.consumption_unit * (ms_d / ms_p)
                        if q_d.consumption_unit > scaled:
                            print(f"✘ La cuota de demanda {q_d} supera a la cuota del plan {q_p} "
                                f"(equivale el plan a {scaled:.1f} en {q_d.consumption_period}).\n")
                            return False

            # === 2) Horizon y muestreo ===
            plan_q_ms   = plan_quotas[0].consumption_period.to_milliseconds()
            demand_q_ms = demand_quotas[-1].consumption_period.to_milliseconds()
            horizon_ms  = max(plan_q_ms, demand_q_ms)
            td = select_best_time_unit(horizon_ms)
            print(f"- Horizonte de muestreo: {horizon_ms:.0f} ms → {td.value:.2f}{td.unit.value}\n")

            step_ms = plan_rate.consumption_period.to_milliseconds()
            times   = list(range(0, int(td.to_milliseconds())+1, int(step_ms)))
            if times[-1] != td.to_milliseconds():
                times.append(int(td.to_milliseconds()))

            plan_pts   = self.bounded_rate.show_available_capacity_curve(td,   debug=True)
            demand_pts = demand.bounded_rate.show_available_capacity_curve(td, debug=True)

            def value_at(ts, pts):
                last = 0
                for t, c in pts:
                    if t > ts:
                        break
                    last = c
                return last

            max_backlog = 0
            for t in times:
                cp   = value_at(t, plan_pts)
                cd   = value_at(t, demand_pts)
                back = cd - cp
                max_backlog = max(max_backlog, back)


            if max_backlog <= 0:
                print("✔ La demanda jamás supera la capacidad. ¡Encaja sin encolar nada!\n")
                return True

            # === 4) Cálculo del drenaje del backlog ===
            r_p       = v_plan
            periodo_ms= 1 / r_p
            t_drain_ms= max_backlog / r_p
            td_serv   = TimeDuration(periodo_ms, TimeUnit.MILLISECOND)\
                            .to_desired_time_unit(plan_rate.consumption_period.unit)

            print(f"→ Backlog máximo: {max_backlog:.0f} peticiones")
            print(f"→ Plan sirve cada {td_serv.value:.2f}{td_serv.unit.value} "
                f"(v={r_p:.6f} pet/ms)")
            print(f"→ Tiempo para drenar backlog: {t_drain_ms/1000:.2f}s "
                f"(la cuota horaria expira en {plan_q_ms/1000:.0f}s)\n")

            # === 5) Encolado detallado ===
            print(f"Encolado de las {max_backlog:.0f} peticiones excedentes (IDs originales):")
            first_id = 2  # la #1 ya fue servida en t=0
            for i in range(int(max_backlog)):
                pid = first_id + i
                t_i = (i+1) * periodo_ms
                print(f"  · Petición demanda #{pid:>4}: segundo {t_i/1000:6.2f}s")
            last_id = first_id + int(max_backlog) - 1

            # === 6) Vuelta al ritmo del plan y siguiente ventana de demanda ===
            print(f"\n✔ Tras la petición demanda #{last_id}, la cola queda vacía.")
            print("→ A partir de ahí retoma el ritmo MÁXIMO del **plan**:")
            print(f"   {plan_rate.consumption_unit}/{plan_rate.consumption_period}")

            # ¿Cuándo se abre la próxima ventana de demanda?
            dp_ms = d_rate.consumption_period.to_milliseconds()
            # resto hasta el siguiente múltiplo de dp_ms
            rem_ms = dp_ms - (t_drain_ms % dp_ms)
            if rem_ms >= dp_ms:
                rem_ms = 0
            print(f"→ La demanda tiene ventana de {dp_ms/1000:.0f}s; "
                f"faltan {rem_ms/1000:.0f}s para enviar tu siguiente batch "
                f"de {d_rate.consumption_unit} peticiones. "
                "Ten en cuenta que cualquier petición extra que el plan no sirva al vuelo "
                "se volverá a encolar.\n")

            # === 7) Decisión final ===
            if t_drain_ms <= plan_q_ms:
                print("✔ Se drena antes de expirar la cuota horaria. Demanda sostenible.\n")
                return True
            else:
                print("✘ No da tiempo a drenar antes de expirar la cuota horaria. ¡No cabe!\n")
                return False

class Demand():
    def __init__(self, rate: Rate, quota: Union[Quota, List[Quota], None] = None, N = None):
        """
        Initializes a Demand instance, acting as a constructor for BoundedRate.

        Args:
            rate (Rate): The rate object for the demand.
            quota (Union[Quota, List[Quota], None], optional): The quota(s) for the demand. Defaults to None.
        """
        if N is not None:
            self.rate = Rate(rate.consumption_unit * N, rate.consumption_period)
            self.quota = None if quota is None else (quota if isinstance(quota, list) else [quota])
            # Multiply the quota or quotas by N, keeping the same time period
            if self.quota is not None:
                self.quota = [
                    Quota(q.consumption_unit * N, q.consumption_period) for q in self.quota
                ]
        else:
            self.rate = rate
            self.quota = None if quota is None else (quota if isinstance(quota, list) else [quota])
        
        self.bounded_rate = BoundedRate(self.rate) if self.quota is None else BoundedRate(self.rate, self.quota)
            
    def __str__(self):
        return f"Demand(rate={self.rate}, quota={self.quota})"

    def show_capacity(self, time_interval: Union[str, TimeDuration]):
        """
        Shows the capacity curve for the demand.

        Args:
            time_interval (Union[str, TimeDuration]): The time interval for the capacity curve.
        """
        if isinstance(time_interval, str):
            time_interval = parse_time_string_to_duration(time_interval)

        return self.bounded_rate.show_capacity(time_interval)
    
    def multiply_by(self, n: int):
        """
        Multiplies the demand by a given factor, as if it were multiple users.
        
        Args:
            n (int): The factor to multiply the demand by.
            
        Returns:
            Demand: A new Demand instance with the multiplied rate and quota. (Bounded Rate)
        """
        
        if n <= 0:
            raise ValueError("The number of users must be a positive integer.")
        
        return Demand(rate=self.rate, quota=self.quota, N=n)

# Example usage
if __name__ == "__main__":

    # Create a BoundedRate instance for testing
    plan_limits = BoundedRate(Rate(1, "2s"), Quota(1800, "1h"))
    demand_fits = Demand(rate=Rate(100, "1min"), quota=Quota(2000, "1day"))
    # Create a Plan instance
    plan = Plan("Test Plan", plan_limits, cost=100, overage_cost=10, max_number_of_subscriptions=1, billing_period="1 month")

    # Test the consume method
    #plan.consume(demand, "2h")
    
    print(plan.has_enough_capacity(demand_fits))  # Should return True



