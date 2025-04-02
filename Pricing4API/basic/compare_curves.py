from typing import List, Union
import plotly.graph_objects as go
from Pricing4API.basic.effective_capacity import Rate, Quota, EffectiveCapacity
from Pricing4API.ancillary.time_unit import TimeDuration, TimeUnit
from matplotlib.colors import to_rgba
from Pricing4API.utils import parse_time_string_to_duration

def compare_rates_capacity(rates: List[Rate], time_interval: Union[str, TimeDuration], return_fig=False):
    """
    Compares the capacity curves of a list of rates.

    Args:
        rates (List[Rate]): List of rates to compare.
        time_interval (Union[str, TimeDuration]): The time interval for generating the curves.
        return_fig (bool, optional): Whether to return the figure. Defaults to False.
    """
    if isinstance(time_interval, str):
        time_interval = parse_time_string_to_duration(time_interval)

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
            name=f"Rate ({color})"
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


if __name__ == "__main__":
    # Create a Rate object
    rate1 = Rate(consumption_unit=10, consumption_period="1h")
    print("Rate 1 Capacity at 1h:", rate1.capacity_at("1h"))
    print("Rate 1 Capacity during 1h:", rate1.capacity_during("1h"))


    # Create another Rate object
    rate2 = Rate(consumption_unit=5, consumption_period="30min")
    print("Rate 2 Capacity at 30min:", rate2.capacity_at("30min"))
    print("Rate 2 Capacity during 30min:", rate2.capacity_during("30min"))
    rate2.show_capacity("10min")

    # Compare the two rates
    compare_rates_capacity([rate2,rate1], "1h")

    # Create a Quota object
    quota = Quota(consumption_unit=20, consumption_period="2h")
    print("Quota Capacity at 2h:", quota.capacity_at("2h"))
    print("Quota Capacity during 2h:", quota.capacity_during("2h"))
    quota.show_capacity("1h")

    # Create an EffectiveCapacity object with one rate and one quota
    effective_capacity = EffectiveCapacity(rate=rate1, quota=quota)
    print("Effective Capacity at 1h:", effective_capacity.effective_capacity(TimeDuration(1, TimeUnit.HOUR)))
    effective_capacity.show_available_capacity_curve(TimeDuration(2, TimeUnit.HOUR))