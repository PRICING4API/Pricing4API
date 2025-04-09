from typing import List, Union
import plotly.graph_objects as go
from Pricing4API.basic.bounded_rate import Rate, Quota, BoundedRate
from Pricing4API.ancillary.time_unit import TimeDuration, TimeUnit
from matplotlib.colors import to_rgba
from Pricing4API.utils import parse_time_string_to_duration

def compare_rates_capacity(rates: List[Rate], time_interval: Union[str, TimeDuration], return_fig=False):
    """
    Compares the capacity curves of a list of rates, starting with the slowest.

    Args:
        rates (List[Rate]): List of rates to compare.
        time_interval (Union[str, TimeDuration]): The time interval for generating the curves.
        return_fig (bool, optional): Whether to return the figure. Defaults to False.
    """
    if isinstance(time_interval, str):
        time_interval = parse_time_string_to_duration(time_interval)

    # Sort rates by speed (slowest first)
    rates.sort(key=lambda rate: rate.consumption_period.to_milliseconds() / rate.consumption_unit)

    predefined_colors = [
        "green", "purple", "brown", "pink", "gray", "olive", "cyan", "magenta", "teal", "lime"
    ]

    if len(rates) > len(predefined_colors):
        raise ValueError("Not enough colors available for all rates.")

    fig = go.Figure()

    for rate, color in zip(rates, predefined_colors):
        debug_values = rate.show_capacity(time_interval, debug=True)
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
            name=f"Rate ({rate.consumption_unit}/{rate.consumption_period})"
        ))

    fig.update_layout(
        title="Comparison of Rate Capacity Curves",
        xaxis_title=f"Time ({time_interval.unit.value})",
        yaxis_title="Capacity",
        legend_title="Rates",
        template="plotly_white",
        width=1000,
        height=600
    )

    if return_fig:
        return fig

    fig.show()


def compare_bounded_rates_capacity(bounded_rates: List[BoundedRate], time_interval: Union[str, TimeDuration], return_fig=False):
    """
    Compares the capacity curves of a list of bounded rates, starting with the slowest.

    Args:
        bounded_rates (List[BoundedRate]): List of bounded rates to compare.
        time_interval (Union[str, TimeDuration]): The time interval for generating the curves.
        return_fig (bool, optional): Whether to return the figure. Defaults to False.
    """
    if isinstance(time_interval, str):
        time_interval = parse_time_string_to_duration(time_interval)

    # Sort bounded rates by speed (slowest first)
    bounded_rates.sort(key=lambda br: br.rate.consumption_period.to_milliseconds() / br.rate.consumption_unit)

    predefined_colors = [
        "green", "purple", "brown", "pink", "gray", "olive", "cyan", "magenta", "teal", "lime"
    ]

    if len(bounded_rates) > len(predefined_colors):
        raise ValueError("Not enough colors available for all bounded rates.")

    fig = go.Figure()

    for bounded_rate, color in zip(bounded_rates, predefined_colors):
        debug_values = bounded_rate.show_available_capacity_curve(time_interval, debug=True)
        times_ms, capacities = zip(*debug_values)

        original_times = [t / time_interval.unit.to_milliseconds() for t in times_ms]

        rgba_color = f"rgba({','.join(map(str, [int(c * 255) for c in to_rgba(color)[:3]]))},0.2)"

        rate_info = f"Rate: {bounded_rate.rate.consumption_unit}/{bounded_rate.rate.consumption_period}"
        quota_info = f"Quota: {bounded_rate.quota.consumption_unit}/{bounded_rate.quota.consumption_period}" if bounded_rate.quota else "No Quota"
        
        fig.add_trace(go.Scatter(
            x=original_times,
            y=capacities,
            mode='lines',
            line=dict(color=color, shape='hv', width=1.3),
            fill='tonexty',
            fillcolor=rgba_color,
            name=f"{rate_info}, {quota_info}"
        ))

    fig.update_layout(
        title="Comparison of Bounded Rate Capacity Curves",
        xaxis_title=f"Time ({time_interval.unit.value})",
        yaxis_title="Capacity",
        legend_title="Bounded Rates",
        template="plotly_white",
        width=1000,
        height=600
    )

    if return_fig:
        return fig

    fig.show()
            
