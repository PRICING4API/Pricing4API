from concurrent.futures import ThreadPoolExecutor
from typing import List, Union

import numpy as np
import plotly.graph_objects as go
from matplotlib.colors import to_rgba

from Pricing4API.ancillary.time_unit import TimeDuration, TimeUnit
from Pricing4API.utils import parse_time_string_to_duration


class Rate:
    
    def __init__(self, consumption_unit: int, consumption_period: Union[str, TimeDuration]):
    
        if isinstance(consumption_period, str):
            consumption_period = parse_time_string_to_duration(consumption_period)
        self.consumption_unit = consumption_unit
        self.consumption_period = consumption_period
        
        
    
    def capacity(self, t: Union[str, TimeDuration]):
        if isinstance(t, str):
            t = parse_time_string_to_duration(t)
        
        if t.unit != TimeUnit.MILLISECOND:
            t_milliseconds = t.to_milliseconds()
        else:
            t_milliseconds = t.value
    
        value, period = self.consumption_unit, self.consumption_period.to_milliseconds()
        
        c = value * np.floor((t_milliseconds / period)+1)
        
        return c

    def show_capacity_curve(self, time_interval: Union[str, TimeDuration], color=None, return_fig=False):
        """
        Plots the capacity curve for this Rate.

        Args:
            time_interval (Union[str, TimeDuration]): The time interval for the curve.
            color (str, optional): Color for the curve. Defaults to None.
            return_fig (bool, optional): Whether to return the figure. Defaults to False.
        """
        if isinstance(time_interval, str):
            time_interval = parse_time_string_to_duration(time_interval)

        t_milliseconds = int(time_interval.to_milliseconds())
        step = int(self.consumption_period.to_milliseconds())
        defined_t_values_ms = list(range(0, t_milliseconds + 1, step))

        defined_capacity_values = [
            self.capacity(TimeDuration(t, TimeUnit.MILLISECOND)) for t in defined_t_values_ms
        ]

        original_times_in_specified_unit = [
            t / time_interval.unit.to_milliseconds() for t in defined_t_values_ms
        ]
        x_label = f"Time ({time_interval.unit.value})"

        fig = go.Figure()

        rgba_color = f"rgba({','.join(map(str, [int(c * 255) for c in to_rgba(color or 'green')[:3]]))},0.3)"

        fig.add_trace(go.Scatter(
            x=original_times_in_specified_unit,
            y=defined_capacity_values,
            mode='lines',
            line=dict(color=color or 'green', shape='hv', width=1.3),
            fill='tonexty',
            fillcolor=rgba_color,
            name='Rate Capacity'
        ))

        fig.update_layout(
            title=f'Capacity Curve - Rate - {time_interval.value} {time_interval.unit.value}',
            xaxis_title=x_label,
            yaxis_title='Capacity',
            legend_title='Curves',
            showlegend=True,
            template='plotly_white',
            width=1000,
            height=600
        )

        if return_fig:
            return fig

        fig.show()


class Quota:
    
    def __init__(self, consumption_unit: int, consumption_period: Union[str, TimeDuration]):
    
        if isinstance(consumption_period, str):
            consumption_period = parse_time_string_to_duration(consumption_period)
        self.consumption_unit = consumption_unit
        self.consumption_period = consumption_period
        
    def capacity(self, t: Union[str, TimeDuration]):
        if isinstance(t, str):
            t = parse_time_string_to_duration(t)
        
        if t.unit != TimeUnit.MILLISECOND:
            t_milliseconds = t.to_milliseconds()
        else:
            t_milliseconds = t.value
    
        value, period = self.consumption_unit, self.consumption_period.to_milliseconds()
        
        c = value * np.floor((t_milliseconds / period)+1)
        
        return c

    def show_capacity_curve(self, time_interval: Union[str, TimeDuration], color=None, return_fig=False):
        """
        Plots the capacity curve for this Quota.

        Args:
            time_interval (Union[str, TimeDuration]): The time interval for the curve.
            color (str, optional): Color for the curve. Defaults to None.
            return_fig (bool, optional): Whether to return the figure. Defaults to False.
        """
        if isinstance(time_interval, str):
            time_interval = parse_time_string_to_duration(time_interval)

        t_milliseconds = int(time_interval.to_milliseconds())
        step = int(self.consumption_period.to_milliseconds())
        defined_t_values_ms = list(range(0, t_milliseconds + 1, step))

        defined_capacity_values = [
            self.capacity(TimeDuration(t, TimeUnit.MILLISECOND)) for t in defined_t_values_ms
        ]

        original_times_in_specified_unit = [
            t / time_interval.unit.to_milliseconds() for t in defined_t_values_ms
        ]
        x_label = f"Time ({time_interval.unit.value})"

        fig = go.Figure()

        rgba_color = f"rgba({','.join(map(str, [int(c * 255) for c in to_rgba(color or 'blue')[:3]]))},0.3)"

        fig.add_trace(go.Scatter(
            x=original_times_in_specified_unit,
            y=defined_capacity_values,
            mode='lines',
            line=dict(color=color or 'blue', shape='hv', width=1.3),
            fill='tonexty',
            fillcolor=rgba_color,
            name='Quota Capacity'
        ))

        fig.update_layout(
            title=f'Capacity Curve - Quota - {time_interval.value} {time_interval.unit.value}',
            xaxis_title=x_label,
            yaxis_title='Capacity',
            legend_title='Curves',
            showlegend=True,
            template='plotly_white',
            width=1000,
            height=600
        )

        if return_fig:
            return fig

        fig.show()


class EffectiveCapacity:
        
    def __init__(self, rate: Rate, quota: Union[Quota, List[Quota], None] = None):
        self.rate = rate
        self.quota = quota
        self.limits = [rate]
        
        if quota:
            if isinstance(quota, list):
                self.limits.extend(quota)
            else:
                self.limits.append(quota)

    def effective_capacity(self, time_simulation: TimeDuration):
        """
        Calculates the effective capacity at a given time without exposing limits_length.

        Args:
            time_simulation (TimeDuration): The time simulation.

        Returns:
            float: The calculated effective capacity.
        """
        if isinstance(time_simulation, str):
            time_simulation = parse_time_string_to_duration(time_simulation)
        
        if time_simulation.unit != TimeUnit.MILLISECOND:
            t_milliseconds = time_simulation.to_milliseconds()
        else:
            t_milliseconds = time_simulation.value
        def _calculate_capacity(t_milliseconds, limits_length):
            if limits_length >= len(self.limits):
                raise ValueError("Try with length = {}".format(len(self.limits) - 1))

            value, period = self.limits[limits_length].consumption_unit, self.limits[limits_length].consumption_period.to_milliseconds()

            if limits_length == 0:
                c = value * np.floor((t_milliseconds / period) + 1)
            else:
                ni = np.floor(t_milliseconds / period)  # determines which interval number (ni) 't' belongs to
                qvalue = value * ni  # capacity due to quota
                aux = t_milliseconds - ni * period  # auxiliary variable
                cprevious = _calculate_capacity(aux, limits_length - 1)
                ramp = min(cprevious, value)  # capacity due to ramp
                c = qvalue + ramp

            return c

        if time_simulation.unit != TimeUnit.MILLISECOND:
            t_milliseconds = time_simulation.to_milliseconds()
        else:
            t_milliseconds = time_simulation.value

        return _calculate_capacity(t_milliseconds, len(self.limits) - 1)

    def show_available_capacity_curve(self, time_interval: TimeDuration, debug: bool = False, color=None, return_fig=False) -> None:
        t_milliseconds = int(time_interval.to_milliseconds())
        step = int(self.limits[0].consumption_period.to_milliseconds())
        defined_t_values_ms = list(range(0, t_milliseconds + 1, step))

        # ⚠️ Ensure at least two points if only one exists and t > 0
        if len(defined_t_values_ms) == 1 and t_milliseconds > 0:
            defined_t_values_ms.append(t_milliseconds)

        with ThreadPoolExecutor() as executor:
            defined_capacity_values = list(executor.map(lambda t: self.effective_capacity(TimeDuration(t, TimeUnit.MILLISECOND)), defined_t_values_ms))

        if debug:
            return list(zip(defined_t_values_ms, defined_capacity_values))

        original_times_in_specified_unit = [
            t / time_interval.unit.to_milliseconds() for t in defined_t_values_ms
        ]
        x_label = f"Time ({time_interval.unit.value})"

        fig = go.Figure()

        rgba_color = f"rgba({','.join(map(str, [int(c * 255) for c in to_rgba(color or 'green')[:3]]))},0.3)"

        fig.add_trace(go.Scatter(
            x=original_times_in_specified_unit,
            y=defined_capacity_values,
            mode='lines',
            line=dict(color=color or 'green', shape='hv', width=1.3),
            fill='tonexty',
            fillcolor=rgba_color,
            name='Accumulated Capacity'
        ))

        fig.update_layout(
            title=f'Capacity Curve - Effective Capacity - {time_interval.value} {time_interval.unit.value}',
            xaxis_title=x_label,
            yaxis_title='Capacity',
            legend_title='Curves',
            showlegend=True,
            template='plotly_white',
            width=1000,
            height=600
        )

        if return_fig:
            return fig

        fig.show()

    def show_instantaneous_capacity_curve(self, time_interval: TimeDuration, debug: bool = False, color=None, return_fig=False) -> None:
        t_milliseconds = int(time_interval.to_milliseconds())
        step = int(self.limits[0].consumption_period.to_milliseconds())
        quota_frequency_ms = self.limits[-1].consumption_period.to_milliseconds()

        defined_t_values_ms = list(range(0, t_milliseconds + 1, step))
        defined_capacity_values = []

        for t in defined_t_values_ms:
            period_index = t // quota_frequency_ms
            period_time = t % quota_frequency_ms
            capacity = self.effective_capacity(TimeDuration(period_time, TimeUnit.MILLISECOND))
            defined_capacity_values.append(capacity)

        if debug:
            return list(zip(defined_t_values_ms, defined_capacity_values))

        original_times_in_specified_unit = [
            t / time_interval.unit.to_milliseconds() for t in defined_t_values_ms
        ]
        x_label = f"Time ({time_interval.unit.value})"

        fig = go.Figure()

        rgba_color = f"rgba({','.join(map(str, [int(c * 255) for c in to_rgba(color or 'blue')[:3]]))},0.3)"

        fig.add_trace(go.Scatter(
            x=original_times_in_specified_unit,
            y=defined_capacity_values,
            mode='lines',
            line=dict(color=color or 'blue', shape='hv', width=1.3),
            fill='tonexty',
            fillcolor=rgba_color,
            name='Instantaneous Capacity'
        ))

        fig.update_layout(
            title=f'Instantaneous Capacity Curve - Effective Capacity - {time_interval.value} {time_interval.unit.value}',
            xaxis_title=x_label,
            yaxis_title='Capacity',
            legend_title='Curves',
            showlegend=True,
            template='plotly_white',
            width=1000,
            height=600
        )

        if return_fig:
            return fig

        fig.show()

    def show_capacity_curve(self, time_interval: Union[str, TimeDuration], debug: bool = False, color=None, return_fig=False):
        if isinstance(time_interval, str):
            time_interval = parse_time_string_to_duration(time_interval)

        t_milliseconds = int(time_interval.to_milliseconds())
        max_quota_duration_ms = self.limits[-1].consumption_period.to_milliseconds()

        if t_milliseconds > max_quota_duration_ms:
            print("Exceeded quota duration. Switching between accumulated and instantaneous curves is possible.")

            fig_accumulated = self.show_available_capacity_curve(time_interval, debug, color, return_fig=True)
            fig_instantaneous = self.show_instantaneous_capacity_curve(time_interval, debug, color, return_fig=True)

            fig = go.Figure()

            for trace in fig_accumulated.data:
                fig.add_trace(trace)

            for trace in fig_instantaneous.data:
                fig.add_trace(trace)

            n_acc = len(fig_accumulated.data)
            n_inst = len(fig_instantaneous.data)

            for i in range(n_acc):
                fig.data[i].visible = True
            for i in range(n_inst):
                fig.data[n_acc + i].visible = False

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
                legend_title="Curves",
                showlegend=True,
                template="plotly_white",
                width=1000,
                height=600
            )

            if return_fig:
                return fig
            else:
                fig.show()
        else:
            return self.show_available_capacity_curve(time_interval, debug, color, return_fig)


if __name__ == "__main__":
    rate = Rate(900, "1min")
    quota = Quota(5000, "1h")
    rate.show_capacity_curve("2min")
    quota.show_capacity_curve("2h")
    effective_capacity = EffectiveCapacity(rate, quota)  # No quota provided
    effective_capacity.show_capacity_curve("1h10min")











