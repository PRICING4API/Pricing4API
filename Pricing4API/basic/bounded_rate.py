from concurrent.futures import ThreadPoolExecutor
from typing import List, Union, Optional

import numpy as np
import plotly.graph_objects as go
from matplotlib.colors import to_rgba

from Pricing4API.ancillary.time_unit import TimeDuration, TimeUnit
from Pricing4API.utils import parse_time_string_to_duration, format_time_with_unit, select_best_time_unit


class Rate:
    
    def __init__(self, consumption_unit: int, consumption_period: Union[str, TimeDuration], fa:int = None):
    
        if isinstance(consumption_period, str):
            consumption_period = parse_time_string_to_duration(consumption_period)
        self.consumption_unit = consumption_unit
        self.consumption_period = consumption_period
        self.fa = self.max_fa #FIX

        #FIX
        if fa:
            if fa <= 0 or fa > self.max_fa:
                raise ValueError(f"fa must be greater than 0 and less than or equal to {self.max_fa}")
            new_rate = self.create_equivalent_rate(fa)
            self.consumption_unit = new_rate.consumption_unit
            self.consumption_period = new_rate.consumption_period
            self.fa = new_rate.max_fa

    def __repr__(self):
        return f"Rate({self.consumption_unit}, {self.consumption_period})"

    @property
    def is_unitary(self):
        return self.consumption_unit == 1

    @property
    def get_units(self):
        return self.consumption_unit

    @property
    def get_interval(self):
        return self.consumption_period
        
        
    #FIX
    def create_equivalent_rate(self, fa= 1):
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

    #FIX
    @property
    def max_fa(self):

        if self.is_unitary:
            return 1

        max_period_ms = self.consumption_period.to_milliseconds()

        unitary_rate = self.create_equivalent_rate()

        unitary_rate_period_ms = unitary_rate.consumption_period.to_milliseconds()

        max_fa = int(max_period_ms / unitary_rate_period_ms)

        return max_fa

    #FIX
    @property
    def max_fa_and_uniform_fa(self):

        if self.is_unitary:
            return 1, 1

        max_period_ms = self.consumption_period.to_milliseconds()

        unitary_rate = self.create_equivalent_rate()

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
        #FIX
        if fa is None:
            fa = self.max_fa

        # Checker for fa 
        if fa <= 0 or fa > self.max_fa:
            raise ValueError(f"fa must be greater than 0 and less than or equal to {self.max_fa}")

        #FIX
        if fa < self.max_fa:
            new_rate = self.create_equivalent_rate(fa)
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
        #FIX
        if fa is None:
            fa = self.max_fa

        # Checker for fa
        if fa <= 0 or fa > self.max_fa:
            raise ValueError(f"fa must be greater than 0 and less than or equal to {self.max_fa}")

        #FIX
        if fa < self.max_fa:
            new_rate = self.create_equivalent_rate(fa)
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

        # Convert time durations to milliseconds
        end_instant_milliseconds = end_instant.to_milliseconds()
        start_instant_milliseconds = start_instant.to_milliseconds()

        # Ensure the time interval is valid
        if end_instant_milliseconds <= start_instant_milliseconds:
            raise ValueError("end_instant must be greater than start_instant")

        # Calculate capacity at the start and end instants
        capacity_at_end = self.capacity_at(TimeDuration(end_instant_milliseconds, TimeUnit.MILLISECOND))
        capacity_at_start = self.capacity_at(TimeDuration(start_instant_milliseconds, TimeUnit.MILLISECOND))

        # Return the difference in capacity
        return capacity_at_end - capacity_at_start

    def min_time(self, capacity_goal: int, return_unit: Optional[TimeUnit] = None, display=True) -> Union[str, TimeDuration]:
        """
        Calculates the minimum time to reach a capacity goal for the Rate.

        Args:
            capacity_goal (int): The capacity goal to reach.
            return_unit (Optional[TimeUnit]): The desired time unit for the result.
            display (bool): If True, returns the formatted output.

        Returns:
            Union[str, TimeDuration]: The minimum time to reach the capacity goal.
        """
        if capacity_goal < 0:
            raise ValueError("The 'capacity goal' should be greater or equal to 0.")
        
        # cálculo igual que antes
        T = np.floor((capacity_goal - 1) * self.consumption_period.to_milliseconds() / self.consumption_unit) if capacity_goal > 0 else 0
        
        # construimos siempre en milisegundos
        result_duration = TimeDuration(int(T), TimeUnit.MILLISECOND)
        
        if T == 0:
            return "0s"
        
        if return_unit is None:
            return_unit = self.consumption_period.unit
        
        duration_desired = result_duration.to_desired_time_unit(return_unit)
        
        return format_time_with_unit(duration_desired) if display else duration_desired

    def convert_to_largest(self, other: 'Rate') -> 'Rate':
        """
        Converts this rate to match the largest time unit between this rate and another rate.

        Args:
            other (Rate): The rate to compare against.

        Returns:
            Rate: A new rate with the largest time unit.
        """
        # Convert both periods to milliseconds for comparison
        self_ms = self.consumption_period.to_milliseconds()
        other_ms = other.consumption_period.to_milliseconds()

        if self_ms > other_ms:
            # Self has the larger period
            scaling_factor = self_ms / other_ms
            adjusted_unit = other.consumption_unit * scaling_factor
            return Rate(adjusted_unit, self.consumption_period)
        else:
            # Other has the larger period
            scaling_factor = other_ms / self_ms
            adjusted_unit = self.consumption_unit * scaling_factor
            return Rate(adjusted_unit, other.consumption_period)

    def convert_to_smallest(self, other: 'Rate') -> 'Rate':
        """
        Converts this rate to match the smallest time unit between this rate and another rate.

        Args:
            other (Rate): The rate to compare against.

        Returns:
            Rate: A new rate with the smallest time unit.
        """
        # Convert both periods to milliseconds for comparison
        self_ms = self.consumption_period.to_milliseconds()
        other_ms = other.consumption_period.to_milliseconds()

        if self_ms < other_ms:
            # Self has the smaller period
            scaling_factor = other_ms / self_ms
            adjusted_unit = self.consumption_unit * scaling_factor
            return Rate(adjusted_unit, other.consumption_period)
        else:
            # Other has the smaller period
            scaling_factor = self_ms / other_ms
            adjusted_unit = other.consumption_unit * scaling_factor
            return Rate(adjusted_unit, self.consumption_period)

    def convert_to_my_time_unit(self, other: 'Rate') -> 'Rate':
        """
        Converts the other rate to match this rate's time unit.

        Args:
            other (Rate): The rate to convert.

        Returns:
            Rate: A new rate with the same time unit as this rate.
        """
        # Convert both periods to milliseconds
        self_ms = self.consumption_period.to_milliseconds()
        other_ms = other.consumption_period.to_milliseconds()

        # Calculate the scaling factor (ceil to ensure no underestimation)
        scaling_factor = np.ceil(other_ms / self_ms)

        # Adjust the consumption unit of the other rate
        adjusted_unit = other.consumption_unit * scaling_factor

        # Return a new rate with the adjusted unit and this rate's time period
        return Rate(adjusted_unit, self.consumption_period)


class Quota:
    
    def __init__(self, consumption_unit: int, consumption_period: Union[str, TimeDuration]):
    
        if isinstance(consumption_period, str):
            consumption_period = parse_time_string_to_duration(consumption_period)
        self.consumption_unit = consumption_unit
        self.consumption_period = consumption_period
        
    def __str__(self):
        return f"Quota({self.consumption_unit}, {self.consumption_period})"
    
    def __repr__(self):
        return f"Quota({self.consumption_unit}, {self.consumption_period})"
        
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

        # Convert time durations to milliseconds
        end_instant_milliseconds = end_instant.to_milliseconds()
        start_instant_milliseconds = start_instant.to_milliseconds()

        # Ensure the time interval is valid
        if end_instant_milliseconds <= start_instant_milliseconds:
            raise ValueError("end_instant must be greater than start_instant")

        # Calculate capacity at the start and end instants
        capacity_at_end = self.capacity_at(TimeDuration(end_instant_milliseconds, TimeUnit.MILLISECOND))
        capacity_at_start = self.capacity_at(TimeDuration(start_instant_milliseconds, TimeUnit.MILLISECOND))

    # Return the difference in capacity
        return capacity_at_end - capacity_at_start

    def min_time(self, capacity_goal: int, return_unit: Optional[TimeUnit] = None, display=True) -> Union[str, TimeDuration]:
        """
        Calculates the minimum time to reach a capacity goal for the Quota.

        Args:
            capacity_goal (int): The capacity goal to reach.
            return_unit (Optional[TimeUnit]): The desired time unit for the result.
            display (bool): If True, returns the formatted output.

        Returns:
            Union[str, TimeDuration]: The minimum time to reach the capacity goal.
        """
        if capacity_goal < 0:
            raise ValueError("The 'capacity goal' should be greater or equal to 0.")
        T = np.floor((capacity_goal - 1) * self.consumption_period.to_milliseconds() / self.consumption_unit) if capacity_goal > 0 else 0
        result_duration = TimeDuration(int(T), TimeUnit.MILLISECOND)
        if T == 0:
            return "0s"
        if return_unit is None:
            return_unit = self.consumption_period.unit
        duration_desired = result_duration.to_desired_time_unit(return_unit)
        return format_time_with_unit(duration_desired) if display else duration_desired
        
        return duration_desired

    def convert_to_largest(self, other: 'Quota') -> 'Quota':
        """
        Converts this quota to match the largest time unit between this quota and another quota.

        Args:
            other (Quota): The quota to compare against.

        Returns:
            Quota: A new quota with the largest time unit.
        """
        # Convert both periods to milliseconds for comparison
        self_ms = self.consumption_period.to_milliseconds()
        other_ms = other.consumption_period.to_milliseconds()

        if self_ms > other_ms:
            # Self has the larger period
            scaling_factor = self_ms / other_ms
            adjusted_unit = other.consumption_unit * scaling_factor
            return Quota(adjusted_unit, self.consumption_period)
        else:
            # Other has the larger period
            scaling_factor = other_ms / self_ms
            adjusted_unit = self.consumption_unit * scaling_factor
            return Quota(adjusted_unit, other.consumption_period)


class BoundedRate:
        
    def __init__(self, rate: Rate, quota: Union[Quota, List[Quota], None] = None):
        self.rate = rate
        self.quota = []
        self.limits = [rate]

        if quota:
            quotas = [quota] if not isinstance(quota, list) else quota
            valid_quotas = []

            for q in quotas:
                # Validación rápida: que sea mayor que la rate y no supere el máximo posible
                if q.consumption_unit <= rate.consumption_unit:
                    continue
                rate_capacity = rate.consumption_unit * (
                    q.consumption_period.to_milliseconds() / rate.consumption_period.to_milliseconds()
                )
                if q.consumption_unit > rate_capacity:
                    continue

                # Simular capacidad hasta el momento de esa cuota
                temp_limits = [rate] + valid_quotas
                temp_br = object.__new__(BoundedRate)
                temp_br.rate = rate
                temp_br.quota = valid_quotas.copy()
                temp_br.limits = temp_limits
                capacity = temp_br.capacity_at(q.consumption_period)

                if capacity >= q.consumption_unit:
                    valid_quotas.append(q)
                    self.limits.append(q)
                else:
                    print(f"[WARNING] Quota omitted as unreachable: {q}")

            self.quota = valid_quotas

                
    def set_rate(self, new_rate: Rate):
        """
        Sets a new rate for the BoundedRate object.

        Args:
            new_rate (Rate): The new rate to be set.
        """
        self.rate = new_rate
        self.limits[0] = new_rate
        
    def reduce_rate(self, reduction_percentage: float):
        """
        Reduces the rate by a specified percentage.

        Args:
            reduction_percentage (float): The percentage by which the rate should be reduced.
        """
        if reduction_percentage < 0 or reduction_percentage > 100:
            raise ValueError("Reduction percentage must be between 0 and 100.")
        
        if reduction_percentage == 100:
            return self 
        
        max_uniformed_rate_time_period = TimeDuration(self.limits[1].consumption_period.to_milliseconds() / self.limits[1].consumption_unit, TimeUnit.MILLISECOND)
        max_uniformed_rate = Rate(1, max_uniformed_rate_time_period)
        

        uniformed_rate_time_period = TimeDuration(self.rate.consumption_period.to_milliseconds() / self.rate.consumption_unit, TimeUnit.MILLISECOND)
        uniformed_rate = Rate(1, uniformed_rate_time_period)
        
        p0 = 0
        p1 = 100
        t0 = max_uniformed_rate_time_period.to_milliseconds()
        t1 = uniformed_rate_time_period.to_milliseconds()
        
        
        t = t0 - ((t0 - t1) * (reduction_percentage / p1))

        new_rate_wait_period = TimeDuration(t, TimeUnit.MILLISECOND)
        best_unit_new_RWP = select_best_time_unit(new_rate_wait_period.to_milliseconds())
        
        new_rate = Rate(1, best_unit_new_RWP)

        return BoundedRate(new_rate, self.quota)
        

    def capacity_at(self, time_simulation: TimeDuration):
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
    
    def capacity_during(self, end_instant: Union[str, TimeDuration], start_instant: Union[str, TimeDuration] = "0ms") -> float:
        """
        Calculates the capacity during a specified time interval.

        Args:
            end_instant (Union[str, TimeDuration]): The final time instant.
            start_instant (Union[str, TimeDuration], optional): The initial time instant. Defaults to "0ms".

        Returns:
            float: The calculated capacity during the specified interval.
        """
        if isinstance(end_instant, str):
            end_instant = parse_time_string_to_duration(end_instant)
        if isinstance(start_instant, str):
            start_instant = parse_time_string_to_duration(start_instant)

        # Convert time durations to milliseconds
        end_instant_milliseconds = end_instant.to_milliseconds()
        start_instant_milliseconds = start_instant.to_milliseconds()

        # Ensure the time interval is valid
        if end_instant_milliseconds <= start_instant_milliseconds:
            raise ValueError("end_instant must be greater than start_instant")

        # Calculate capacity at the start and end instants
        capacity_at_end = self.capacity_at(TimeDuration(end_instant_milliseconds, TimeUnit.MILLISECOND))
        capacity_at_start = self.capacity_at(TimeDuration(start_instant_milliseconds, TimeUnit.MILLISECOND))

        # Return the difference in capacity
        return capacity_at_end - capacity_at_start

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
            defined_capacity_values = list(executor.map(lambda t: self.capacity_at(TimeDuration(t, TimeUnit.MILLISECOND)), defined_t_values_ms))

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
            capacity = self.capacity_at(TimeDuration(period_time, TimeUnit.MILLISECOND))
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

    def min_time(self, capacity_goal: int, return_unit: Optional[TimeUnit] = None, display=True) -> Union[str, TimeDuration]:
        """
        Calculates the minimum time to reach a capacity goal for the BoundedRate.

        Args:
            capacity_goal (int): The capacity goal to reach.
            return_unit (Optional[TimeUnit]): The desired time unit for the result.
            display (bool): If True, returns the formatted output.

        Returns:
            Union[str, TimeDuration]: The minimum time to reach the capacity goal.
        """
        # Validar que capacity_goal sea un entero no negativo
        if not isinstance(capacity_goal, int):
            raise TypeError("capacity_goal must be an integer number of requests")
        if capacity_goal < 0:
            raise ValueError("The 'capacity goal' should be greater or equal to 0.")

        # 1) Acumular tiempo para cada cuota (de mayor a menor), consumiendo batches completos
        T = 0
        for limit in reversed(self.limits[1:]):
            if capacity_goal <= 0:
                break
            nu = np.floor(capacity_goal / limit.consumption_unit)
            delta = (capacity_goal == nu * limit.consumption_unit)
            n_i = int(nu - 1 if delta else nu)
            T += n_i * limit.consumption_period.to_milliseconds()
            capacity_goal -= n_i * limit.consumption_unit

        # 2) Batch inicial del rate (por múltiplos enteros de consumption_unit)
        rate = self.limits[0]
        c_r = rate.consumption_unit
        if capacity_goal > c_r:
            from math import ceil
            batches = ceil(capacity_goal / c_r)
            p_r_ms = rate.consumption_period.to_milliseconds()
            T += (batches - 1) * p_r_ms

        # 3) Construir la duración en milisegundos
        result_duration = TimeDuration(int(T), TimeUnit.MILLISECOND)
        if T == 0:
            return "0s"

        # 4) Convertir a la unidad deseada
        if return_unit is None:
            return_unit = rate.consumption_period.unit
        duration_desired = result_duration.to_desired_time_unit(return_unit)
        return format_time_with_unit(duration_desired) if display else duration_desired




    def quota_exhaustion_threshold(self,display=True) -> List[Union[str, TimeDuration]]:
        """
        Calcula los tiempos t_ast para cada límite del plan.

        Returns:
            List[TimeDuration]: Una lista de objetos TimeDuration que representan los tiempos t_ast para cada límite.
        """
        exhaustion_thresholds = []

        # Iterar sobre los límites para calcular cada t_ast
        for object in self.limits:
            if isinstance(object, Rate):
                continue
            exhaustion_thresholds.append(self.min_time(object.consumption_unit, display=display))
 
        return exhaustion_thresholds[0] if len(exhaustion_thresholds) == 1 else exhaustion_thresholds




if __name__ == "__main__":
    pass
    
    









