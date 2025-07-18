import asyncio
from concurrent.futures import ThreadPoolExecutor
import math
from typing import List, Optional, Tuple, Union

from matplotlib import pyplot as plt
from matplotlib.colors import to_rgba
from matplotlib.widgets import RadioButtons
import numpy as np
import yaml
import plotly.graph_objects as go

from Pricing4API.ancillary.limit import Limit
from Pricing4API.ancillary.time_unit import TimeDuration, TimeUnit
from Pricing4API.utils import rearrange_time_axis_function, select_best_time_unit, format_time, format_time_with_unit, parse_time_string_to_duration


class Plan:
    
    def __init__(self, name, billing: Tuple[float, TimeDuration], overage_cost: float = None, 
                 unitary_rate: Limit = None, quotes = List[Limit], max_number_of_subscriptions: int = 1, **kwargs):
        
        self.__unitary_rate = unitary_rate
        self.__limits = []
        self.__name = name
        self.__quotes = quotes
        self.__times = []
        
        self.__price = billing[0]
        self.__billing_unit = billing[1]
        
        self.__overage_cost = overage_cost
        
        if unitary_rate is not None:
            self.__limits.append(unitary_rate)
        
        if quotes:
            for quote in quotes:
                self.__limits.append(quote)
            
        ## ordena los límites de menor duracion a mayor
        
        self.__limits.sort(key=lambda x: x.duration.to_seconds())
        
        for limit in self.__limits:
            self.__times.append(limit.duration)
        
        
        self.__max_number_of_subscriptions = max_number_of_subscriptions
        
        self.__next_plan = self
        self.__previous_plan = self
        
        self.__t_ast = self.compute_t_ast()
        
        if not quotes and unitary_rate is not None:
            self.__quotes = [unitary_rate]

    
    @property
    def unitary_rate(self):
        return self.__unitary_rate if self.__unitary_rate is not None else False
    
    @unitary_rate.setter
    def unitary_rate(self, value):
        if value is not None:
            self.__unitary_rate = value
            if self.__limits:
                self.__limits[0] = value
                self.__times[0] = value.duration
                
        else:
            return
    
    @property
    def name(self):
        return self.__name
    
    @property
    def price(self):
        return self.__price
    
    @property
    def billing_unit(self):
        return self.__billing_unit
    
    @property
    def rate_value(self):
        return self.limits[0].value
    
    
    @property
    def rate_frequency(self):
        return self.limits[0].duration
    
    
    
    @property
    def quotes_values(self):
        return [quote.value for quote in self.__quotes]
    
    @property
    def quotes_frequencies(self):
        return [quote.duration for quote in self.__quotes]
    
    @property
    def overage_cost(self):
        return self.__overage_cost
    
    @property
    def limits(self):
        return self.__limits

    @limits.setter
    def limits(self, new_limits: List[Limit]):
        """
        Setter for limits. Updates the internal limits and related properties.
        """
        self.__limits = sorted(new_limits, key=lambda x: x.duration.to_seconds())
        self.__times = [limit.duration for limit in self.__limits]

    @property
    def quotes(self):
        return self.__quotes

    @quotes.setter
    def quotes(self, new_quotes: List[Limit]):
        """
        Setter for quotes. Updates the internal quotes and related properties.
        """
        self.__quotes = new_quotes
    
    @property
    def max_number_of_subscriptions(self):
        return self.__max_number_of_subscriptions
    
    @property
    def unit_base_cost(self):
        """
        """
        if self.__price == 0.0:
            return 0.0
        return self.__price / self.limits[-1].value
    
    @property
    def next_plan(self):
        return self.__next_plan
    
    def setNext(self, plan):
        self.__next_plan = plan
        
    @property
    def previous_plan(self):
        return self.__previous_plan
    
    def setPrevious(self, plan):
        self.__previous_plan = plan
        
    @property
    def overage_quote(self):
        if self.__price == 0.0 or self.__overage_cost is None or self.__max_number_of_subscriptions == 1:
            return 'N/A'
        return math.floor((self.__price / self.__overage_cost) + self.__limits[-1].value)
    
    @property
    def cost_with_overage_quote(self):
        if self.__price == 0.0 or self.__overage_cost is None:
            return 'N/A'
        return (self.__price + self.__overage_cost * (self.__ovreage_quote - self.__limits[-1].value))
    
    @property
    def upgrade_quote(self):
        if self.__next_plan is None or self.__next_plan.price == 0.0 or self.__next_plan.overage_cost is None or self.__overage_cost is None:
            return 'N/A'
        return math.floor(self.__limits[-1].value + (self.__next_plan.price - self.__price) / self.__overage_cost)
    
    @property
    def downgrade_quote(self):
        if self.previous_plan is None:
            return 'N/A'
        return self.previous_plan.upgrade_quote
    
    # PROPIEDADES DEFINIDAS TRAS REUNIÓN 5/12/25
    
    @property
    def t_ast(self):
        return self.__t_ast
    
    @property
    def quotas_burning_times(self):
        t_ast = self.__t_ast
        if self.unitary_rate:
            #quitamos el primer elemento de la lista
            t_ast = t_ast[1:]
    
        return t_ast
    
    @property
    def max_quota_burning_time(self):
        return self.quotas_burning_times[-1]
    
    @property
    def quotas_recovery_intervals(self):
        quotas_freq = self.quotes_frequencies
        burning_times = self.quotas_burning_times
        
        return [quotas_freq[i] - burning_times[i] for i in range(len(quotas_freq))]
    
    @property
    def max_quota_recovery_interval(self):
        return self.quotas_recovery_intervals[-1]
    
    @property
    def rate_wait_period(self):
        return self.limits[0].duration
    

    @property
    def earliest_coolingdown_threshold(self):
        """
        Debería devolver cuando me fundo la cuota, pero no está todo en las mismas unidades, así que pensemos algo
        """
        first_limit_value = self.__limits[0].value  # Cuota inicial (ej. número de llamadas)
        first_limit_duration = self.__limits[0].duration  # Duración del primer límite (TimeDuration)

        # Obtenemos la segunda cuota (primer límite de cuota)
        first_quota_value = self.__limits[-1].value  # Primer límite de cuota (o lo que es hard limit?)

        # Convertir la duración del primer límite a milisegundos para trabajar consistentemente
        duration_ms = first_limit_duration.to_milliseconds()

        # Calcular el tiempo necesario para alcanzar la cuota del primer límite
        # Por ejemplo, si el primer límite son 20 llamadas y podemos hacer 1 llamada cada 2 segundos,
        # necesitamos calcular cuánto tiempo nos lleva hacer 20 llamadas.
        if first_limit_value == 0:
            raise ValueError("First limit value cannot be zero.")
        
        required_time_ms = (first_quota_value / first_limit_value) * duration_ms

        # Seleccionar la mejor unidad de tiempo para representar este valor
        return select_best_time_unit(required_time_ms)
    

    @property
    def max_unavailability_time(self):
        if not self.__times or len(self.__times) == 0:
            raise ValueError("No time values are available for calculating unavailability time.")

        # Obtener el tiempo de renovación de la cuota en milisegundos
        renewal_time = self.__times[-1]
        renewal_time_ms = renewal_time.to_milliseconds() if isinstance(renewal_time, TimeDuration) else renewal_time

        # Obtener el tiempo más temprano para gastar la cuota (en milisegundos)
        earliest_threshold = self.earliest_coolingdown_threshold
        earliest_threshold_ms = earliest_threshold.to_milliseconds() if isinstance(earliest_threshold, TimeDuration) else earliest_threshold

        # Calcular el tiempo máximo de no disponibilidad (en milisegundos)
        max_unavailability_ms = renewal_time_ms - earliest_threshold_ms

        # Asegurarse de que el resultado no sea negativo
        if max_unavailability_ms < 0:
            raise ValueError("The calculated unavailability time cannot be negative.")

        # Seleccionar la mejor unidad de tiempo para representar el resultado
        return select_best_time_unit(max_unavailability_ms)
    
    
    @property
    def max_unavailability_percentage(self) -> float:
        """
        Calcula, en porcentaje, el tiempo respecto de la renovación de la cuota que el plan no está disponible para hacer peticiones.

        La lógica convierte todos los valores de tiempo a milisegundos antes de calcular el porcentaje, 
        para asegurar que las operaciones sean consistentes.
        """
        if not self.__times or len(self.__times) == 0:
            raise ValueError("No time values are available for calculating unavailability percentage.")

        # Obtener el tiempo de renovación de la cuota en milisegundos
        renewal_time = self.__times[-1]
        renewal_time_ms = renewal_time.to_milliseconds() if isinstance(renewal_time, TimeDuration) else renewal_time

        # Obtener el tiempo necesario para gastar la cuota inicial (en milisegundos)
        earliest_threshold = self.earliest_coolingdown_threshold
        earliest_threshold_ms = earliest_threshold.to_milliseconds() if isinstance(earliest_threshold, TimeDuration) else earliest_threshold

        # Calcular el tiempo de no disponibilidad en milisegundos
        max_unavailability_ms = renewal_time_ms - earliest_threshold_ms

        # Asegurarse de que el resultado no sea negativo
        if max_unavailability_ms < 0:
            raise ValueError("The calculated unavailability time cannot be negative.")

        # Calcular el porcentaje de tiempo de no disponibilidad con respecto al tiempo de renovación
        max_unavailability_percentage = (max_unavailability_ms / renewal_time_ms) * 100

        # Redondear el resultado a 2 decimales para simplificar el resultado
        return round(max_unavailability_percentage, 2)
    
    
    def available_capacity(self, time_simulation: TimeDuration, limits_length):
        if time_simulation.unit != TimeUnit.MILLISECOND:
            t_milliseconds = time_simulation.to_milliseconds()
        else:
            t_milliseconds = time_simulation.value
     
            
        if limits_length >= len(self.limits):
            raise ValueError("Try with length = {}".format(len(self.limits) - 1))
        
        value, period = self.limits[limits_length].value, self.limits[limits_length].to_milliseconds()
        
        if limits_length == 0:
            c = value * np.floor((t_milliseconds / period)+1)
            #print(f"Limit Level: {limits_length}, t: {t_milliseconds}, Value: {value}, Period: {period}, C: {c}")
            
        else:
            ni = np.floor(t_milliseconds / period) # determines which interval number (ni) 't' belongs to
            qvalue = value * ni # capacity due to quota
            aux = t_milliseconds - ni * period # auxiliary variable
            cprevious = self.available_capacity(TimeDuration(aux, TimeUnit.MILLISECOND), limits_length - 1)
            ramp = min(cprevious, value) # capacity due to ramp
            c = qvalue + ramp
            #print(f"Limit Level: {limits_length}, t: {t_milliseconds}, Value: {value}, Period: {period}, Ni: {ni}, QValue: {qvalue}, Cprevious: {cprevious}, Ramp: {ramp}, C: {c}")
        
        return c
    
    def capacity(self, time_simulation):
        """
        Calculates the capacity for a given time simulation.

        Args:
            time_simulation (Union[str, TimeDuration]): The time simulation, either as a string or TimeDuration.

        Returns:
            float: The calculated capacity.
        """
        if isinstance(time_simulation, str):
            time_simulation = parse_time_string_to_duration(time_simulation)

        return self.available_capacity(time_simulation, len(self.limits) - 1)
    
    def compute_available_capacity_threads(self, t):
        
        return self.available_capacity(TimeDuration(t, TimeUnit.MILLISECOND), len(self.limits) - 1)
           
    def show_available_capacity_curve(self, time_interval: TimeDuration, debug: bool = False, color=None, return_fig=False) -> None:
        t_milliseconds = int(time_interval.to_milliseconds())
        step = int(self.rate_frequency.to_milliseconds())
        defined_t_values_ms = list(range(0, t_milliseconds + 1, step))

        # ⚠️ Añadido: forzar dos puntos si solo hay uno y t > 0
        if len(defined_t_values_ms) == 1 and t_milliseconds > 0:
            defined_t_values_ms.append(t_milliseconds)

        max_burning_time_ms = self.max_quota_burning_time.to_milliseconds()
        quota_frequency_ms = self.quotes_frequencies[-1].to_milliseconds()

        defined_t_values_ms = [
            t for t in defined_t_values_ms
            if not (max_burning_time_ms + step <= t % quota_frequency_ms <= quota_frequency_ms - step) or t == t_milliseconds
        ]

        if not defined_t_values_ms:
            defined_t_values_ms = [0, t_milliseconds]

        with ThreadPoolExecutor() as executor:
            defined_capacity_values = list(executor.map(self.compute_available_capacity_threads, defined_t_values_ms))

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
            title=f'Capacity Curve - {self.name} - {time_interval.value} {time_interval.unit.value}',
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

    def unitary_uniformed_capacity_curve(self, time_interval: Union[TimeDuration, str], debug: bool = False, color=None, return_fig=False) -> None:
        """
        Infers the unitary rate by calculating the interval between consecutive requests based on the
        largest quota. For example, if the largest limit is 5000 calls per hour (3600000 ms),
        the inferred unitary rate is 3600000/5000 ≈ 720 ms per call.
        
        This method creates a new Plan instance with the inferred unitary rate and existing limits,
        and shows the capacity curve for the new plan.
        
        Args:
            time_interval (Union[TimeDuration, str]): The time interval for the capacity curve.
            debug (bool): If True, returns debug information.
            color: The color of the curve.
            return_fig (bool): If True, returns the figure instead of displaying it.
        """
        # Convert time_interval to TimeDuration if provided as string.
        if isinstance(time_interval, str):
            time_interval = parse_time_string_to_duration(time_interval)
        
        # Ensure there is at least one limit.
        if not self.limits:
            raise ValueError("No limits available to infer the unitary rate.")
        
        # Find the limit with the highest value (largest quota).
        largest_limit = max(self.limits, key=lambda l: l.value)
        period_ms = largest_limit.duration.to_milliseconds()
        if largest_limit.value == 0:
            raise ValueError("The largest limit's value is 0, cannot infer unitary rate.")
        
        # Calculate the time interval per request (in ms) for the largest limit.
        inferred_interval_ms = period_ms / largest_limit.value
        inferred_rate_duration = TimeDuration(int(inferred_interval_ms), TimeUnit.MILLISECOND)
        
        # Create the inferred limit: 1 request per inferred_rate_duration.
        inferred_limit = Limit(1, inferred_rate_duration)
        
        # Create a new Plan instance with the inferred unitary rate and existing limits.
        new_plan = Plan(
            name=f"{self.name} (Unitary Uniformed)",
            billing=(self.price, self.billing_unit),
            overage_cost=self.overage_cost,
            unitary_rate=inferred_limit,
            quotes=[self.limits[-1]],
            max_number_of_subscriptions=self.max_number_of_subscriptions
        )
        
        # Show the capacity curve for the new plan.
        return new_plan.show_capacity_curve(time_interval, debug, color, return_fig)
    
    
    
    def show_instantaneous_capacity_curve(self, time_interval: TimeDuration, debug: bool = False, color=None, return_fig=False) -> None:
            t_milliseconds = int(time_interval.to_milliseconds())
            step = int(self.rate_frequency.to_milliseconds())
            quota_frequency_ms = self.quotes_frequencies[-1].to_milliseconds()

            defined_t_values_ms = list(range(0, t_milliseconds + 1, step))
            defined_capacity_values = []

            for t in defined_t_values_ms:
                period_index = t // quota_frequency_ms
                period_time = t % quota_frequency_ms
                capacity = self.available_capacity(TimeDuration(period_time, TimeUnit.MILLISECOND), len(self.limits) - 1)
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
                title=f'Instantaneous Capacity Curve - {self.name} - {time_interval.value} {time_interval.unit.value}',
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
            
        

    def show_capacity_curve(self, time_interval, debug: bool = False, color=None, return_fig=False):
        # Parse time_interval if it is a string
        if isinstance(time_interval, str):
            time_interval = parse_time_string_to_duration(time_interval)
        
        t_milliseconds = int(time_interval.to_milliseconds())
        max_quota_duration_ms = self.quotes_frequencies[-1].to_milliseconds()

        # CASO 1: Excede la duración de la cuota
        if t_milliseconds > max_quota_duration_ms:
            # ⚠️ Restaurado: Mostrar mensaje en consola
            print("Has superado la cuota. Puedes cambiar entre las curvas acumulada e instantánea.")

            # Obtenemos las figuras de cada curva
            fig_accumulated = self.show_available_capacity_curve(time_interval, debug, color, return_fig=True)
            fig_instantaneous = self.show_instantaneous_capacity_curve(time_interval, debug, color, return_fig=True)

            # Creamos una figura "contenedora"
            fig = go.Figure()

            # Agregamos las trazas de "Accumulated"
            for trace in fig_accumulated.data:
                fig.add_trace(trace)

            # Agregamos las trazas de "Instantaneous"
            for trace in fig_instantaneous.data:
                fig.add_trace(trace)

            # Contamos cuántas trazas hay en cada figura
            n_acc = len(fig_accumulated.data)
            n_inst = len(fig_instantaneous.data)

            # Definimos la visibilidad inicial:
            #   - "Accumulated": visible por defecto
            #   - "Instantaneous": oculto
            for i in range(n_acc):
                fig.data[i].visible = True  # las n_accumulated
            for i in range(n_inst):
                fig.data[n_acc + i].visible = False  # las n_instantaneous

            # Creamos dos patrones de visibilidad:
            accum_visible = [True] * n_acc + [False] * n_inst
            inst_visible  = [False] * n_acc + [True]  * n_inst

            # Añadimos los botones
            fig.update_layout(
                title="Accumulated Capacity",  # Título inicial
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

        # CASO 2: No excede -> se muestra directamente la curva "available"
        else:
            return self.show_available_capacity_curve(time_interval, debug, color, return_fig)



    
    def min_time(self, capacity_goal: int, return_unit: Optional[TimeUnit] = None, i_initial: Optional[int] = None, display = None) -> TimeDuration:
        """
        Calcula el tiempo mínimo para alcanzar una meta de capacidad usando los límites dados.

        Args:
            capacity_goal (int): La meta de capacidad que se desea alcanzar.
            return_unit (Optional[TimeUnit]): La unidad de tiempo en la que se desea obtener el resultado (ej. SECOND, MINUTE).
                                            Si no se especifica, se usará la unidad del primer límite.
            i_initial (Optional[int]): El índice inicial para comenzar la iteración. Si no se especifica, se usará el límite más alto.

        Returns:
            TimeDuration: El tiempo mínimo para alcanzar la meta de capacidad, representado en la unidad deseada.
        """

        if i_initial is None:
            i_initial = len(self.__limits) - 1

        # Inicialización
        T = 0  # Tiempo en milisegundos
        i = i_initial

        if capacity_goal < 0:
            raise ValueError("The 'capacity goal' should be greater or equal to 0.")

        # Iteración sobre los límites
        while i > 0:
            capacity_limit = self.__limits[i].value
            period_limit_ms = self.__limits[i].duration.to_milliseconds()

            nu = np.floor(capacity_goal / capacity_limit)

            # Cálculo de delta
            delta = capacity_goal == nu * capacity_limit

            # Cálculo n_i
            if capacity_goal == 0:
                n_i = 0
            else:
                n_i = nu - 1 if delta else nu

            # Traslación del origen
            T += n_i * period_limit_ms

            if capacity_goal > 0:
                capacity_goal -= n_i * capacity_limit

            # Actualización de i
            i -= 1

        # Iteración para i = 0
        c_r = self.__limits[0].value
        p_r_ms = self.__limits[0].duration.to_milliseconds()

        if capacity_goal > 0:
            T += np.floor((capacity_goal - 1) * p_r_ms / c_r)
        else:
            T = 0

        # Crear una instancia de TimeDuration en milisegundos
        result_duration = TimeDuration(int(T), TimeUnit.MILLISECOND)

        # Si no se especifica return_unit, se toma la unidad del primer límite
        if return_unit is None:
            return_unit = self.__limits[0].duration.unit

        # Convertir el resultado a la unidad especificada usando el nuevo método to_desired_time_unit
        duration_desired = result_duration.to_desired_time_unit(return_unit)

        if display:
            return format_time_with_unit(duration_desired)
        
        return duration_desired
    
    
    def compute_t_ast(self) -> List[TimeDuration]:
        """
        Calcula los tiempos t_ast para cada límite del plan.

        Returns:
            List[TimeDuration]: Una lista de objetos TimeDuration que representan los tiempos t_ast para cada límite.
        """
        t_ast = []

        # Iterar sobre los límites para calcular cada t_ast
        for i in range(len(self.__limits)):
            # Usar la función min_time() para calcular el tiempo mínimo, especificando i_initial
            min_time_result = self.min_time(self.__limits[i].value, return_unit=self.__limits[i].duration.unit, i_initial=i - 1)

            # Convertir el resultado al valor en milisegundos
            duration_ms = min_time_result.to_milliseconds()

            # Seleccionar la mejor unidad de tiempo para representar este valor
            t_ast.append(select_best_time_unit(duration_ms))

        return t_ast
    
    def generate_ideal_capacity_curve(self, subscription_time: TimeDuration = None) -> List[Tuple[int, int]]:
        
        quota = self.max_quota_burning_time + self.max_quota_recovery_interval if not subscription_time else subscription_time
        
        values = self.show_available_capacity_curve(quota, debug=True)
        
        return [(v[0]/1000, v[1]) for v in values]
    
    def show_quota_uniform_capacity_curve(self, time_interval: Union[TimeDuration, str], limit_index: int, debug: bool = False, color=None, return_fig=False) -> None:
        """
        Uniformizes the consumption based on a specific quota limit and displays the capacity curve.

        Args:
            time_interval (Union[TimeDuration, str]): The time interval for the curve.
            limit_index (int): The index of the limit to uniformize.
            debug (bool): If True, returns debug information.
            color: The color of the curve.
            return_fig (bool): If True, returns the figure instead of displaying it.
        """
        # Check if the limit index is valid
        if limit_index >= len(self.limits) or limit_index < 0:
            raise ValueError(f"Invalid limit index. Available range: 0 to {len(self.limits) - 1}")

        # Check if the plan has a unitary rate
        if self.unitary_rate:
            raise ValueError("Cannot uniformize a plan with an already unitary rate.")

        # Get the selected limit
        selected_limit = self.limits[limit_index]

        # Determine the directly inferior time unit
        duration_unit = selected_limit.duration.unit
        if duration_unit == TimeUnit.MILLISECOND:
            raise ValueError("Cannot uniformize a limit with millisecond duration.")
        inferior_unit = duration_unit.inferior_unit()

        # Infer the uniform rate for the selected limit
        inferred_rate_value = math.floor(selected_limit.value / duration_unit.to(inferior_unit))
        inferred_rate_duration = TimeDuration(1, inferior_unit)  # Uniformize to 1 unit of the inferior time
        inferred_limit = Limit(inferred_rate_value, inferred_rate_duration)

        # Temporarily modify the limits and quotes using the setters
        original_limits = self.limits.copy()
        original_quotes = self.quotes.copy()
        self.limits = self.limits[:limit_index] + [inferred_limit] + self.limits[limit_index + 1:]
        self.quotes = self.quotes[:limit_index] + self.quotes[limit_index + 1:]

        # Show the capacity curve
        result = self.show_capacity_curve(time_interval, debug, color, return_fig)

        # Restore the original limits and quotes
        self.limits = original_limits
        self.quotes = original_quotes

        return result
    
    
    def uniformed_curve_by_quota(self, time_interval_str: str):
        """
        Método interactivo que muestra por consola las cuotas disponibles (los límites)
        y pide al usuario que ingrese el índice del límite a uniformizar. Luego, muestra
        la curva uniformizada para ese límite.

        Args:
            time_interval_str (str): Cadena que representa el intervalo de tiempo para la curva
                                    (ej. "1h" o "1h1min").
        """
        from Pricing4API.utils import parse_time_string_to_duration

        try:
            ti = parse_time_string_to_duration(time_interval_str)
        except Exception as e:
            print("Error al parsear el intervalo de tiempo:", e)
            return

        print("\n--- Cuotas disponibles ---")
        for idx, limit in enumerate(self.limits):
            print(f"Índice {idx}: {limit.value} cada {limit.duration}")
            
        index_str = input("Ingrese el índice del límite a uniformizar: ").strip()
        try:
            idx = int(index_str)
        except Exception as e:
            print("Índice inválido:", e)
            return

        try:
            result = self.show_quota_uniform_capacity_curve(ti, idx, return_fig=True)
            result.show()
        except Exception as e:
            print("Error al mostrar la curva uniformizada por cuota:", e)
            
            
    def show_all_capacity_modes(self, time_interval_str: str) -> None:
        """
        Método maestro que combina las curvas:
        - Capacidad acumulada (original).
        - Capacidad instantánea.
        - Capacidad con rate uniformizado.
        - Capacidad con cuota uniformizada.
        
        Si se excede la duración de la cuota máxima, permite alternar entre acumulada e instantánea.
        Este método no requiere input() directo, sino que muestra automáticamente todas las variantes posibles.

        Args:
            time_interval_str (str): Cadena de intervalo de tiempo (ej. '1h').
        """
        from Pricing4API.utils import parse_time_string_to_duration

        time_interval = parse_time_string_to_duration(time_interval_str)
        t_ms = time_interval.to_milliseconds()
        quota_ms = self.quotes_frequencies[-1].to_milliseconds()

        fig = go.Figure()
        color_map = {
            "Accumulated": "green",
            "Instantaneous": "blue",
            "Unitary Uniformed": "purple",
            "Quota Uniformed": "orange"
        }
        traces = []
        visibilities = []

        # Curva acumulada
        acc_data = self.show_available_capacity_curve(time_interval, debug=True)
        times, caps = zip(*acc_data)
        times_unit = [t / time_interval.unit.to_milliseconds() for t in times]
        traces.append(go.Scatter(x=times_unit, y=caps, mode='lines', name='Accumulated', line=dict(shape='hv', color=color_map["Accumulated"])))
        visibilities.append([True, False, False, False])

        # Curva instantánea
        if t_ms > quota_ms:
            inst_data = self.show_instantaneous_capacity_curve(time_interval, debug=True)
            t_inst, c_inst = zip(*inst_data)
            t_inst_unit = [t / time_interval.unit.to_milliseconds() for t in t_inst]
            traces.append(go.Scatter(x=t_inst_unit, y=c_inst, mode='lines', name='Instantaneous', line=dict(shape='hv', color=color_map["Instantaneous"])))
            visibilities[0][1] = True  # activable si está presente

        # Curva unitary uniformizada
        try:
            uuf_plan = self.unitary_uniformed_capacity_curve(time_interval, debug=True, return_fig=True)
            for trace in uuf_plan.data:
                trace.name = "Unitary Uniformed"
                trace.line.color = color_map["Unitary Uniformed"]
                traces.append(trace)
                visibilities[0][2] = True
        except:
            pass

        # Curva por cuota uniformizada (se muestra solo para el último límite)
        try:
            q_fig = self.show_quota_uniform_capacity_curve(time_interval, limit_index=len(self.limits)-1, debug=True, return_fig=True)
            for trace in q_fig.data:
                trace.name = "Quota Uniformed"
                trace.line.color = color_map["Quota Uniformed"]
                traces.append(trace)
                visibilities[0][3] = True
        except:
            pass

        for trace in traces:
            fig.add_trace(trace)

        # Botones para alternar visibilidad
        fig.update_layout(
            updatemenus=[
                dict(
                    type="buttons",
                    direction="right",
                    x=0.1,
                    xanchor="left",
                    y=1.1,
                    yanchor="top",
                    buttons=[
                        dict(
                            label="Accumulated",
                            method="update",
                            args=[{"visible": [True, False, False, False]},
                                {"title": f"Accumulated Capacity - {self.name}"}]
                        ),
                        dict(
                            label="Instantaneous",
                            method="update",
                            args=[{"visible": [False, True, False, False]},
                                {"title": f"Instantaneous Capacity - {self.name}"}]
                        ),
                        dict(
                            label="Unitary Uniformed",
                            method="update",
                            args=[{"visible": [False, False, True, False]},
                                {"title": f"Unitary Uniformed Capacity - {self.name}"}]
                        ),
                        dict(
                            label="Quota Uniformed",
                            method="update",
                            args=[{"visible": [False, False, False, True]},
                                {"title": f"Quota Uniformed Capacity - {self.name}"}]
                        ),
                    ]
                )
            ],
            title=f"Accumulated Capacity - {self.name}",
            xaxis_title=f"Time ({time_interval.unit.value})",
            yaxis_title="Capacity",
            showlegend=True,
            template="plotly_white",
            width=1000,
            height=600
        )

        fig.show()


    
if __name__ == "__main__":

    Github = Plan("Github", (0.0, TimeDuration(1, TimeUnit.MONTH)), 0.0, unitary_rate=None,quotes=[Limit(900, TimeDuration(1, TimeUnit.MINUTE)),Limit(5000, TimeDuration(1, TimeUnit.HOUR))])
    Zenhub = Plan("Zenhub", (0.0, TimeDuration(1, TimeUnit.MONTH)), 0.0, Limit(1, TimeDuration(600, TimeUnit.MILLISECOND)),[Limit(100, TimeDuration(1, TimeUnit.MINUTE)), Limit(5000, TimeDuration(1, TimeUnit.HOUR))])
    Aux = Plan("Aux", (0.0, TimeDuration(1, TimeUnit.MONTH)), 0.0, quotes=[Limit(10, TimeDuration(1, TimeUnit.SECOND)), Limit(100, TimeDuration(1, TimeUnit.MINUTE))])
    print(Aux.t_ast)
    
    dblp = Plan("dblp", (0.0, TimeDuration(1, TimeUnit.MONTH)), 0.0, Limit(1, TimeDuration(2, TimeUnit.SECOND)),[Limit(18, TimeDuration(60, TimeUnit.SECOND)),Limit(48, TimeDuration(300, TimeUnit.SECOND)),Limit(1800, TimeDuration(1, TimeUnit.HOUR))])
    print(dblp.available_capacity(TimeDuration(1, TimeUnit.HOUR), len(dblp.limits) - 1))
    dblp.show_capacity_curve("2h")
    
    
    







