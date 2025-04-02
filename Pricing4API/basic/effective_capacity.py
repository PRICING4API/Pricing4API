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


    @property
    def is_unitary(self):
        return self.consumption_unit == 1

    @property
    def get_units(self):
        return self.consumption_unit

    @property
    def get_interval(self):
        return self.consumption_period
        
        


    def create_unitary(self, fa= 1):
        """
        Creates a unitary Rate from this Rate.

        Args:
            fa (int, optional): Factor for unitary rate. Defaults to 1.

        Returns:
            Rate: The unitary Rate.
        """

        period = self.consumption_period.to_milliseconds() / self.consumption_unit

        period = period * fa

        return Rate(fa, TimeDuration(period, TimeUnit.MILLISECOND))

    @property
    def max_fa(self):

        if self.is_unitary:
            return 1

        max_period_ms = self.consumption_period.to_milliseconds()

        unitary_rate = self.create_unitary()

        unitary_rate_period_ms = unitary_rate.consumption_period.to_milliseconds()

        max_fa = int(max_period_ms / unitary_rate_period_ms)

        return max_fa

    @property
    def max_fa_and_uniform_fa(self):

        if self.is_unitary:
            return 1, 1

        max_period_ms = self.consumption_period.to_milliseconds()

        unitary_rate = self.create_unitary()

        unitary_rate_period_ms = unitary_rate.consumption_period.to_milliseconds()

        max_fa = int(max_period_ms / unitary_rate_period_ms)

        return max_fa, 1


    def capacity_at(self, t: Union[str, TimeDuration], fa: int = None):
        """
        Calculates the capacity at a given time.

        Args:
            t (Union[str, TimeDuration]): The time at which to calculate capacity.
            fa (int, optional): Factor de aceleración (acceleration factor). Defaults to the maximum factor if None.

        Returns:
            float: The calculated capacity.
        """
        if fa is None:
            fa = self.max_fa

        # Checker for fa
        if fa <= 0 or fa > self.max_fa:
            raise ValueError(f"fa must be greater than 0 and less than or equal to {self.max_fa}")

        if fa < self.max_fa:
            new_rate = self.create_unitary(fa)
            return new_rate.capacity_at(t)

        if isinstance(t, str):
            t = parse_time_string_to_duration(t)
        
        if t.unit != TimeUnit.MILLISECOND:
            t_milliseconds = t.to_milliseconds()
        else:
            t_milliseconds = t.value
    
        value, period = self.consumption_unit, self.consumption_period.to_milliseconds()
        
        c = value * np.floor((t_milliseconds / period)+1)
        
        return c

    def show_capacity(self, time_interval: Union[str, TimeDuration], fa: int = None, color=None, return_fig=False, debug=False):
        """
        Plots the capacity curve for this Rate.

        Args:
            time_interval (Union[str, TimeDuration]): The time interval for the curve.
            fa (int, optional): Factor de aceleración (acceleration factor). Defaults to the maximum factor if None.
            color (str, optional): Color for the curve. Defaults to None.
            return_fig (bool, optional): Whether to return the figure. Defaults to False.

        Returns:
            Optional[go.Figure]: The plotly figure if return_fig is True.
        """
        if fa is None:
            fa = self.max_fa

        # Checker for fa
        if fa <= 0 or fa > self.max_fa:
            raise ValueError(f"fa must be greater than 0 and less than or equal to {self.max_fa}")

        if fa < self.max_fa:
            new_rate = self.create_unitary(fa)
            return new_rate.show_capacity(time_interval, color=color, return_fig=return_fig, debug=debug)

        if isinstance(time_interval, str):
            time_interval = parse_time_string_to_duration(time_interval)

        t_milliseconds = int(time_interval.to_milliseconds())
        step = int(self.consumption_period.to_milliseconds())
        defined_t_values_ms = list(range(0, t_milliseconds + 1, step))

        # Ensure the last point is included
        if defined_t_values_ms[-1] != t_milliseconds:
            defined_t_values_ms.append(t_milliseconds)

        defined_capacity_values = [
            self.capacity_at(TimeDuration(t, TimeUnit.MILLISECOND)) for t in defined_t_values_ms
        ]

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

    def capacity_during(self, end_instant: Union[str, TimeDuration], start_instant: Union[str, TimeDuration] = "0ms"):
        """
        Calculates the capacity during a specified time interval.

        Args:
            end_instant (Union[str, TimeDuration]): The final time instant.
            start_instant (Union[str, TimeDuration], optional): The initial time instant. Defaults to "0ms".

        Returns:
            float: The calculated capacity just before the final instant.
        """
        if isinstance(end_instant, str):
            end_instant = parse_time_string_to_duration(end_instant)
        if isinstance(start_instant, str):
            start_instant = parse_time_string_to_duration(start_instant)

        # Calculate the time just before the final instant
        end_instant_milliseconds = end_instant.to_milliseconds() - 0.1

        # Ensure the time is not negative
        if end_instant_milliseconds < 0:
            raise ValueError("end_instant must be greater than start_instant")

        # Calculate capacity at the time just before the final instant
        return self.capacity_at(TimeDuration(end_instant_milliseconds, TimeUnit.MILLISECOND))

    



class Quota:
    
    def __init__(self, consumption_unit: int, consumption_period: Union[str, TimeDuration]):
    
        if isinstance(consumption_period, str):
            consumption_period = parse_time_string_to_duration(consumption_period)
        self.consumption_unit = consumption_unit
        self.consumption_period = consumption_period
        
    def capacity_at(self, t: Union[str, TimeDuration]):
        if isinstance(t, str):
            t = parse_time_string_to_duration(t)
        
        if t.unit != TimeUnit.MILLISECOND:
            t_milliseconds = t.to_milliseconds()
        else:
            t_milliseconds = t.value
    
        value, period = self.consumption_unit, self.consumption_period.to_milliseconds()
        
        c = value * np.floor((t_milliseconds / period)+1)
        
        return c

    def show_capacity(self, time_interval: Union[str, TimeDuration], color=None, return_fig=False, debug=False):
        if isinstance(time_interval, str):
            time_interval = parse_time_string_to_duration(time_interval)

        t_milliseconds = int(time_interval.to_milliseconds())
        step = int(self.consumption_period.to_milliseconds())
        defined_t_values_ms = list(range(0, t_milliseconds + 1, step))

        # Ensure at least two points if only one exists and t > 0
        if len(defined_t_values_ms) == 1 and t_milliseconds > 0:
            defined_t_values_ms.append(t_milliseconds)

        # Ensure the last point is included
        if defined_t_values_ms[-1] != t_milliseconds:
            defined_t_values_ms.append(t_milliseconds)

        defined_capacity_values = [
            self.capacity_at(TimeDuration(t, TimeUnit.MILLISECOND)) for t in defined_t_values_ms
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

    def capacity_during(self, end_instant: Union[str, TimeDuration], start_instant: Union[str, TimeDuration] = "0ms"):
        """
        Calculates the capacity during a specified time interval.

        Args:
            end_instant (Union[str, TimeDuration]): The final time instant.
            start_instant (Union[str, TimeDuration], optional): The initial time instant. Defaults to "0ms".

        Returns:
            float: The calculated capacity just before the final instant.
        """
        if isinstance(end_instant, str):
            end_instant = parse_time_string_to_duration(end_instant)
        if isinstance(start_instant, str):
            start_instant = parse_time_string_to_duration(start_instant)

        # Calculate the time just before the final instant
        end_instant_milliseconds = end_instant.to_milliseconds() - 0.1

        # Ensure the time is not negative
        if end_instant_milliseconds < 0:
            raise ValueError("end_instant must be greater than start_instant")

        # Calculate capacity at the time just before the final instant
        return self.capacity_at(TimeDuration(end_instant_milliseconds, TimeUnit.MILLISECOND))


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

        # Ensure at least two points if only one exists and t > 0
        if len(defined_t_values_ms) == 1 and t_milliseconds > 0:
            defined_t_values_ms.append(t_milliseconds)

        # Ensure the last point is included
        if defined_t_values_ms[-1] != t_milliseconds:
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

        # Ensure the last point is included
        if defined_t_values_ms[-1] != t_milliseconds:
            defined_t_values_ms.append(t_milliseconds)

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

    def show_capacity(self, time_interval: Union[str, TimeDuration], debug: bool = False, color=None, return_fig=False):
        if isinstance(time_interval, str):
            time_interval = parse_time_string_to_duration(time_interval)

        t_milliseconds = int(time_interval.to_milliseconds())
        step = int(self.limits[0].consumption_period.to_milliseconds())
        defined_t_values_ms = list(range(0, t_milliseconds + 1, step))

        # Ensure at least two points if only one exists and t > 0
        if len(defined_t_values_ms) == 1 and t_milliseconds > 0:
            defined_t_values_ms.append(t_milliseconds)

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


