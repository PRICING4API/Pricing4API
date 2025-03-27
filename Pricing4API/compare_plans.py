from typing import List
import plotly.graph_objects as go

from Pricing4API.ancillary.limit import Limit
from Pricing4API.ancillary.plans_yaml import create_plan_interactive
from Pricing4API.ancillary.time_unit import TimeDuration, TimeUnit
from Pricing4API.main.plan import Plan
from matplotlib.colors import to_rgba


def compare_plans(plans, time_interval, return_fig=False):
    """
    Compara las curvas de capacidad de una lista de planes.

    Parameters:
        plans (list): Lista de planes a comparar.
        time_interval (TimeDuration): Intervalo de tiempo para generar las curvas.
    """

    predefined_colors = [
        "green", "purple", "brown", "pink", "gray", "olive", "cyan", "magenta", "teal", "lime"
    ]

    if len(plans) > len(predefined_colors):
        raise ValueError("No hay suficientes colores disponibles para todos los planes.")

    fig = go.Figure()

    for plan, color in zip(plans, predefined_colors):
        debug_values = plan.show_available_capacity_curve(
            time_interval, debug=True
        )
        times_ms, capacities = zip(*debug_values)

        original_times = [t / time_interval.unit.to_milliseconds() for t in times_ms]

        rgba_color = f"rgba({','.join(map(str, [int(c * 255) for c in to_rgba(color)[:3]]))},0.2)"

        fig.add_trace(go.Scatter(
            x=original_times,
            y=capacities,
            mode='lines',
            line=dict(color=color, shape='hv', width=1.3),
            fill='tonexty',
            fillcolor=rgba_color,
            name=f"{plan.name} ({color})"
        ))

    fig.update_layout(
        title="Comparison of Capacity Curves",
        xaxis_title=f"Time ({time_interval.unit.value})",
        yaxis_title="Capacity",
        legend_title="Plans",
        template="plotly_white",
        width=1000,
        height=600
    )

    if return_fig:
        return fig

    fig.show()


def compare_instantaneous_capacity_curves(plans, time_interval, return_fig=False):
    """
    Compara las curvas de capacidad instantánea de una lista de planes.

    Parameters:
        plans (list): Lista de planes a comparar.
        time_interval (TimeDuration): Intervalo de tiempo para generar las curvas.
    """

    predefined_colors = [
        "green", "purple", "brown", "pink", "gray", "olive", "cyan", "magenta", "teal", "lime"
    ]

    if len(plans) > len(predefined_colors):
        raise ValueError("No hay suficientes colores disponibles para todos los planes.")

    fig = go.Figure()

    for plan, color in zip(plans, predefined_colors):
        debug_values = plan.show_instantaneous_capacity_curve(
            time_interval, debug=True
        )
        times_ms, capacities = zip(*debug_values)

        original_times = [t / time_interval.unit.to_milliseconds() for t in times_ms]

        rgba_color = f"rgba({','.join(map(str, [int(c * 255) for c in to_rgba(color)[:3]]))},0.2)"

        fig.add_trace(go.Scatter(
            x=original_times,
            y=capacities,
            mode='lines',
            line=dict(color=color, shape='hv', width=1.3),
            fill='tonexty',
            fillcolor=rgba_color,
            name=f"{plan.name} ({color})"
        ))

    fig.update_layout(
        title="Comparison of Instantaneous Capacity Curves",
        xaxis_title=f"Time ({time_interval.unit.value})",
        yaxis_title="Capacity",
        legend_title="Plans",
        template="plotly_white",
        width=1000,
        height=600
    )

    if return_fig:
        return fig

    fig.show()


if __name__ == "__main__":

    Github = Plan("Github", (0.0, TimeDuration(1, TimeUnit.MONTH)), 0.0, unitary_rate=None,quotes=[Limit(900, TimeDuration(1, TimeUnit.MINUTE)),Limit(5000, TimeDuration(1, TimeUnit.HOUR))])
    Zenhub = Plan("Zenhub", (0.0, TimeDuration(1, TimeUnit.MONTH)), 0.0, Limit(1, TimeDuration(600, TimeUnit.MILLISECOND)),[Limit(100, TimeDuration(1, TimeUnit.MINUTE)), Limit(5000, TimeDuration(1, TimeUnit.HOUR))])

    Github.show_capacity_curve("1h2min")
    
    plan = create_plan_interactive()