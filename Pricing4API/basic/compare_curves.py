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
        max_period_ms = rate.consumption_period.to_milliseconds()
        t_milliseconds = int(time_interval.to_milliseconds())

        if t_milliseconds > max_period_ms:
            print("Exceeded rate period. Switching between accumulated and instantaneous curves is possible.")

            # Use debug values to plot accumulated and instantaneous curves
            debug_values_accumulated = rate.show_capacity(time_interval, debug=True)
            debug_values_instantaneous = rate.show_capacity(time_interval, debug=True)

            times_ms_acc, capacities_acc = zip(*debug_values_accumulated)
            times_ms_inst, capacities_inst = zip(*debug_values_instantaneous)

            original_times_acc = [t / time_interval.unit.to_milliseconds() for t in times_ms_acc]
            original_times_inst = [t / time_interval.unit.to_milliseconds() for t in times_ms_inst]

            rgba_color = f"rgba({','.join(map(str, [int(c * 255) for c in to_rgba(color)[:3]]))},0.2)"

            fig.add_trace(go.Scatter(
                x=original_times_acc,
                y=capacities_acc,
                mode='lines',
                line=dict(color=color, shape='hv', width=1.3),
                fill='tonexty',
                fillcolor=rgba_color,
                name=f"Accumulated Rate ({rate.consumption_unit}/{rate.consumption_period})"
            ))

            fig.add_trace(go.Scatter(
                x=original_times_inst,
                y=capacities_inst,
                mode='lines',
                line=dict(color=color, shape='hv', width=1.3),
                fill='tonexty',
                fillcolor=rgba_color,
                name=f"Instantaneous Rate ({rate.consumption_unit}/{rate.consumption_period})"
            ))

            n_acc = len(times_ms_acc)
            n_inst = len(times_ms_inst)

            accum_visible = [True] * n_acc + [False] * n_inst
            inst_visible = [False] * n_acc + [True] * n_inst

            fig.update_layout(
                title="Accumulated Capacity",
                updatemenus=[
                    dict(
                        type="buttons",
                        direction="left",
                        x=0.30,
                        xanchor="left",
                        y=1.10,
                        yanchor="top",
                        buttons=[
                            dict(
                                label="Accumulated",
                                method="update",
                                args=[
                                    {"visible": accum_visible},
                                    {"title": "Accumulated Capacity"}
                                ]
                            ),
                            dict(
                                label="Instantaneous",
                                method="update",
                                args=[
                                    {"visible": inst_visible},
                                    {"title": "Instantaneous Capacity"}
                                ]
                            )
                        ]
                    )
                ],
                xaxis_title=f"Time ({time_interval.unit.value})",
                yaxis_title="Capacity",
                legend_title="Rates",
                template="plotly_white",
                width=1000,
                height=600
            )
        else:
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
        max_quota_duration_ms = bounded_rate.limits[-1].consumption_period.to_milliseconds()
        t_milliseconds = int(time_interval.to_milliseconds())

        if t_milliseconds > max_quota_duration_ms:
            print("Exceeded quota duration. Switching between accumulated and instantaneous curves is possible.")

            # Use debug values to plot accumulated and instantaneous curves
            debug_values_accumulated = bounded_rate.show_available_capacity_curve(time_interval, debug=True)
            debug_values_instantaneous = bounded_rate.show_instantaneous_capacity_curve(time_interval, debug=True)

            times_ms_acc, capacities_acc = zip(*debug_values_accumulated)
            times_ms_inst, capacities_inst = zip(*debug_values_instantaneous)

            original_times_acc = [t / time_interval.unit.to_milliseconds() for t in times_ms_acc]
            original_times_inst = [t / time_interval.unit.to_milliseconds() for t in times_ms_inst]

            rgba_color = f"rgba({','.join(map(str, [int(c * 255) for c in to_rgba(color)[:3]]))},0.2)"

            rate_info = f"Rate: {bounded_rate.rate.consumption_unit}/{bounded_rate.rate.consumption_period}"
            
            fig.add_trace(go.Scatter(
                x=original_times_acc,
                y=capacities_acc,
                mode='lines',
                line=dict(color=color, shape='hv', width=1.3),
                fill='tonexty',
                fillcolor=rgba_color,
                name=f"Accumulated {rate_info}",
                visible=True  # Set accumulated as visible by default
            ))

            fig.add_trace(go.Scatter(
                x=original_times_inst,
                y=capacities_inst,
                mode='lines',
                line=dict(color=color, shape='hv', width=1.3),
                fill='tonexty',
                fillcolor=rgba_color,
                name=f"Instantaneous {rate_info}",
                visible=False  # Set instantaneous as not visible by default
            ))

            # Ensure only one set of traces is visible at a time
            accum_visible = [True, False]
            inst_visible = [False, True]

            fig.update_layout(
                title="Accumulated Capacity",
                updatemenus=[
                    dict(
                        type="buttons",
                        direction="left",
                        x=0.30,
                        xanchor="left",
                        y=1.10,
                        yanchor="top",
                        buttons=[
                            dict(
                                label="Accumulated",
                                method="update",
                                args=[
                                    {"visible": accum_visible},
                                    {"title": "Accumulated Capacity"}
                                ]
                            ),
                            dict(
                                label="Instantaneous",
                                method="update",
                                args=[
                                    {"visible": inst_visible},
                                    {"title": "Instantaneous Capacity"}
                                ]
                            )
                        ]
                    )
                ],
                xaxis_title=f"Time ({time_interval.unit.value})",
                yaxis_title="Capacity",
                legend_title="Bounded Rates",
                template="plotly_white",
                width=1000,
                height=600
            )
        else:
            debug_values = bounded_rate.show_available_capacity_curve(time_interval, debug=True)
            times_ms, capacities = zip(*debug_values)

            original_times = [t / time_interval.unit.to_milliseconds() for t in times_ms]

            rgba_color = f"rgba({','.join(map(str, [int(c * 255) for c in to_rgba(color)[:3]]))},0.2)"

            rate_info = f"Rate: {bounded_rate.rate.consumption_unit}/{bounded_rate.rate.consumption_period}"
            
            fig.add_trace(go.Scatter(
                x=original_times,
                y=capacities,
                mode='lines',
                line=dict(color=color, shape='hv', width=1.3),
                fill='tonexty',
                fillcolor=rgba_color,
                name=f"{rate_info}"
            ))

    if return_fig:
        return fig

    fig.show()
    
    
            
