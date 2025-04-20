import re
from typing import List, Optional, Union
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
    rates.sort(key=lambda rate: rate.consumption_period.to_milliseconds() / rate.consumption_unit, reverse=False)

    predefined_colors = [
        "green", "purple", "brown", "pink", "gray", "olive", "cyan", "magenta", "teal", "lime"
    ]

    if len(rates) > len(predefined_colors):
        raise ValueError("Not enough colors available for all rates.")

    fig = go.Figure()

    # añadimos índice i para controlar el fill
    for i, (rate, color) in enumerate(zip(rates, predefined_colors)):
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

            rgba_color = (
                f"rgba({','.join(map(str, [int(c * 255) for c in to_rgba(color)[:3]]))},0.2)"
            )

            # Accumulated curve: primera capa hasta el eje, las demás sobre la anterior
            fig.add_trace(go.Scatter(
                x=original_times_acc,
                y=capacities_acc,
                mode='lines',
                line=dict(color=color, shape='hv', width=1.3),
                fill='tozeroy' if i == 0 else 'tonexty',
                fillcolor=rgba_color,
                name=f"Accumulated Rate ({rate.consumption_unit}/{rate.consumption_period})"
            ))

            # Instantaneous curve: igual regla de fill
            fig.add_trace(go.Scatter(
                x=original_times_inst,
                y=capacities_inst,
                mode='lines',
                line=dict(color=color, shape='hv', width=1.3),
                fill='tozeroy' if i != 0 else 'tonexty',
                fillcolor=rgba_color,
                name=f"Instantaneous Rate ({rate.consumption_unit}/{rate.consumption_period})"
            ))

            n_acc = len(times_ms_acc)
            n_inst = len(times_ms_inst)

            accum_visible = [True] * n_acc + [False] * n_inst
            inst_visible  = [False] * n_acc + [True] * n_inst

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

            rgba_color = (
                f"rgba({','.join(map(str, [int(c * 255) for c in to_rgba(color)[:3]]))},0.2)"
            )

            fig.add_trace(go.Scatter(
                x=original_times,
                y=capacities,
                mode='lines',
                line=dict(color=color, shape='hv', width=1.3),
                fill='tozeroy' if i != 0 else 'tonexty',
                fillcolor=rgba_color,
                name=f"Rate ({rate.consumption_unit}/{rate.consumption_period})"
            ))

    if return_fig:
        return fig

    fig.show()


def compare_bounded_rates_capacity(bounded_rates: List[BoundedRate],
                                   time_interval: Union[str, TimeDuration],
                                   return_fig=False):
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
    bounded_rates.sort(
        key=lambda br: br.rate.consumption_period.to_milliseconds() / br.rate.consumption_unit,
        reverse=False
    )

    predefined_colors = [
        "green", "purple", "brown", "pink", "gray", "olive",
        "cyan", "magenta", "teal", "lime"
    ]

    if len(bounded_rates) > len(predefined_colors):
        raise ValueError("Not enough colors available for all bounded rates.")

    fig = go.Figure()

    # añadimos índice i para controlar el fill
    for i, (bounded_rate, color) in enumerate(zip(bounded_rates, predefined_colors)):
        max_quota_duration_ms = bounded_rate.limits[-1].consumption_period.to_milliseconds()
        t_milliseconds = int(time_interval.to_milliseconds())

        if t_milliseconds > max_quota_duration_ms:
            print("Exceeded quota duration. Switching between accumulated and instantaneous curves is possible.")

            debug_values_accumulated = bounded_rate.show_available_capacity_curve(time_interval, debug=True)
            debug_values_instantaneous = bounded_rate.show_instantaneous_capacity_curve(time_interval, debug=True)

            times_ms_acc, capacities_acc = zip(*debug_values_accumulated)
            times_ms_inst, capacities_inst = zip(*debug_values_instantaneous)

            original_times_acc = [t / time_interval.unit.to_milliseconds() for t in times_ms_acc]
            original_times_inst = [t / time_interval.unit.to_milliseconds() for t in times_ms_inst]

            rgba_color = (
                f"rgba({','.join(map(str, [int(c * 255) for c in to_rgba(color)[:3]]))},0.2)"
            )
            rate_info = f"{bounded_rate.rate.consumption_unit}/{bounded_rate.rate.consumption_period}"

            fig.add_trace(go.Scatter(
                x=original_times_acc,
                y=capacities_acc,
                mode='lines',
                line=dict(color=color, shape='hv', width=1.3),
                fill='tozeroy' if i != 0 else 'tonexty',
                fillcolor=rgba_color,
                name=f"Accumulated Rate: {rate_info}",
                visible=True
            ))

            fig.add_trace(go.Scatter(
                x=original_times_inst,
                y=capacities_inst,
                mode='lines',
                line=dict(color=color, shape='hv', width=1.3),
                fill='tozeroy' if i != 0 else 'tonexty',
                fillcolor=rgba_color,
                name=f"Instantaneous Rate: {rate_info}",
                visible=False
            ))

            accum_visible = [True, False]
            inst_visible  = [False, True]

            fig.update_layout(
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
                                ]
                            ),
                            dict(
                                label="Instantaneous",
                                method="update",
                                args=[
                                    {"visible": inst_visible},
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

            rgba_color = (
                f"rgba({','.join(map(str, [int(c * 255) for c in to_rgba(color)[:3]]))},0.2)"
            )
            rate_info = f"{bounded_rate.rate.consumption_unit}/{bounded_rate.rate.consumption_period}"

            fig.add_trace(go.Scatter(
                x=original_times,
                y=capacities,
                mode='lines',
                line=dict(color=color, shape='hv', width=1.3),
                fill='tozeroy' if i != 0 else 'tonexty',
                fillcolor=rgba_color,
                name=f"{rate_info}"
            ))

            # Update layout to include axis titles and legend
            fig.update_layout(
                title="Capacity Curve",
                xaxis_title=f"Time ({time_interval.unit.value})",
                yaxis_title="Capacity",
                legend_title="Bounded Rates",
                template="plotly_white",
                width=1000,
                height=600
            )

    if return_fig:
        return fig

    fig.update_layout(
        title="Capacity Curves")
    fig.show()
    

def show_line(
    fig: go.Figure,
    *,
    x: Optional[str] = None,           # e.g. "30min", "0.5h", "120s"
    y: Optional[float] = None,         # valor numérico de capacidad
    color: str = "red",                # color de la línea
    dash: str = "dash",                # "solid" | "dash" | "dot" | "dashdot"
    width: int = 1,                    # ancho de la línea
    opacity: float = 1.0,              # 0.0–1.0
    layer: str = "above",              # "above" o "below"
    annotation_text: Optional[str] = None,     # texto de la anotación
    annotation_position: Optional[str] = None,  # "top left", "bottom right", …
    annotation_font: Optional[dict] = None,      # p.ej. {"size":12,"color":"black"}
    annotation_align: Optional[str] = None       # "left" | "center" | "right"
) -> None:
    # 1. extraemos unidad del eje X
    title = fig.layout.xaxis.title.text or ""
    m = re.search(r"\((ms|s|min|h|day|week|month|year)\)", title)
    tgt = TimeUnit(m.group(1)) if m else TimeUnit.SECOND

    # 2. línea vertical
    if x is not None:
        td = parse_time_string_to_duration(x)
        td_conv = td.to_desired_time_unit(tgt)
        fig.add_vline(
            x=td_conv.value,
            line=dict(color=color, dash=dash, width=width),
            opacity=opacity,
            layer=layer,
            annotation_text=annotation_text,
            annotation_position=annotation_position,
            annotation_font=annotation_font,
            annotation_align=annotation_align
        )

    # 3. línea horizontal
    if y is not None:
        fig.add_hline(
            y=y,
            line=dict(color=color, dash=dash, width=width),
            opacity=opacity,
            layer=layer,
            annotation_text=annotation_text,
            annotation_position=annotation_position,
            annotation_font=annotation_font,
            annotation_align=annotation_align
        )
        

def update_legend_names(fig: go.Figure, legend_names: List[str]) -> None:
    """
    Dynamically updates the legend names for the traces in the figure.

    Args:
        fig (go.Figure): The Plotly figure to update.
        legend_names (List[str]): A list of legend names to apply to the traces.
    """

    for i, trace in enumerate(fig.data):
        if i < 2:  # First two traces (0 and 1)
            trace.name = legend_names[0]
        else:  # Next two traces (2 and 3)
            trace.name = legend_names[1]
        
def update_legend(fig: go.Figure, legend_title: str) -> None:
    """
    Updates the legend title of the figure.

    Args:
        fig (go.Figure): The Plotly figure to update.
        legend_title (str): The new title for the legend.
    """
    fig.update_layout(legend_title=dict(text=legend_title))


def update_yaxis(fig: go.Figure, yaxis_title: str) -> None:
    """
    Updates the y-axis title of the figure.

    Args:
        fig (go.Figure): The Plotly figure to update.
        yaxis_title (str): The new title for the y-axis.
    """
    fig.update_layout(yaxis_title=yaxis_title)


def update_title(fig: go.Figure, title: str) -> None:
    """
    Updates the title of the figure.

    Args:
        fig (go.Figure): The Plotly figure to update.
        title (str): The new title for the figure.
    """
    fig.update_layout(title=title)
    
if __name__ == "__main__":
    br1 = BoundedRate(Rate(1, "2s"), Quota(1800, "1h"))
    br2 = BoundedRate(
        Rate(1, "2s"),
        [
            Quota(18,   "60s"),
            Quota(48,  "300s"),
            Quota(1800, "1h")
        ]
    )
    
    #print(br2.capacity_at("1h"))
    
    fig = compare_bounded_rates_capacity([br1, br2], "2h", return_fig=True)
    
    show_line(fig, x="1h", y=0.5, color="blue", dash="solid", width=2, opacity=0.5,
                layer="above", annotation_text="1h", annotation_position="top left",
                annotation_font={"size": 12, "color": "black"}, annotation_align="left")
    
    update_legend_names(fig, ["Nominal Capacity", "Regulated Capacity"])
    update_legend(fig, "Bounded Rates")
    update_yaxis(fig, "Requests")
    update_title(fig, "Nominal and regulated capacity of DBLP")
    fig.show()
    
    
