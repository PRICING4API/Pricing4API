import math
from typing import List, Optional, Tuple

from matplotlib import pyplot as plt
from matplotlib.widgets import RadioButtons
import numpy as np
import yaml

from Pricing4API.ancillary.limit import Limit
from Pricing4API.ancillary.time_unit import TimeDuration, TimeUnit
from Pricing4API.utils import rearrange_time_axis_function, select_best_time_unit, format_time, format_time_with_unit


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
        if time_simulation.value != TimeUnit.MILLISECOND:
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
    
    # Método de la clase Plan para mostrar la curva de capacidad
    def show_available_capacity_curve(self, time_interval: TimeDuration, debug: bool = False, color = None, return_fig = False) -> None:
        # Convertir el intervalo de tiempo a milisegundos para cálculos internos
        t_miliseconds = int(time_interval.to_milliseconds())

        # Convertir el 'step' a milisegundos
        step = int(self.rate_frequency.to_milliseconds())

        # Determinar los puntos definidos de tiempo en milisegundos
        defined_t_values_ms = range(0, t_miliseconds + 1, step)

        # Calcular valores de capacidad solo en los puntos definidos
        defined_capacity_values = [
            self.available_capacity(TimeDuration(t, TimeUnit.MILLISECOND), len(self.__limits) - 1)
            for t in defined_t_values_ms
        ]
        
        if debug:
            return list(zip(defined_t_values_ms, defined_capacity_values))

        # Convertir los valores del eje x al formato inicial especificado por el usuario
        original_times_in_specified_unit = [
            t / time_interval.unit.to_milliseconds() for t in defined_t_values_ms
        ]
        x_label = f"Tiempo ({time_interval.unit.value})"

        # Configurar la gráfica inicial
        fig, ax = plt.subplots(figsize=(10, 6))

        if not color:
        # Graficar la señal de tipo escalón con la unidad de tiempo original
            ax.step(original_times_in_specified_unit, defined_capacity_values, where='post', color='green', label='Capacidad acumulada')
            
            # Rellenar el área bajo la curva de capacidad acumulada
            ax.fill_between(original_times_in_specified_unit, 0, defined_capacity_values, step='post', color="green", alpha=0.3)
        else:
            ax.step(original_times_in_specified_unit, defined_capacity_values, where='post', color=color, label='Capacidad acumulada')
            
            # Rellenar el área bajo la curva de capacidad acumulada
            ax.fill_between(original_times_in_specified_unit, 0, defined_capacity_values, step='post', color=color, alpha=0.3)
        
        ax.set_xlabel(x_label)
        ax.set_ylabel('Capacidad')
        ax.set_ylim(0)
        ax.set_title(f'Curva de capacidad - {self.name} - {time_interval.value} {time_interval.unit.value}')
        ax.grid(True)
        ax.legend()

        if return_fig:
            return fig, ax
        # Mostrar la gráfica
        plt.show()

    
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
    
    def show_capacity_areas(self, time_interval: TimeDuration) -> None:
        """Muestra las áreas de capacidad acumulada y la capacidad desplazada al recovery_interval corregido."""

        # Convertir el intervalo de tiempo a milisegundos
        time_interval_ms = time_interval.to_milliseconds()

        # Obtener el tiempo de recuperación máximo de la cuota en milisegundos
        recovery_interval_ms = self.max_quota_recovery_interval.to_milliseconds()

        # Obtener el periodo del rate y convertirlo a milisegundos
        rate_wait_period_ms = self.rate_wait_period.to_milliseconds()

        # Calcular el desplazamiento real
        shifted_recovery_interval_ms = recovery_interval_ms - rate_wait_period_ms

        # Definir los tiempos en milisegundos
        step_ms = self.limits[0].duration.to_milliseconds()
        defined_t_values = range(0, int(time_interval_ms) + 1, int(step_ms))

        # Calcular la capacidad en los puntos definidos
        defined_capacity_values = [
            self.available_capacity(TimeDuration(t, TimeUnit.MILLISECOND), len(self.limits) - 1) for t in defined_t_values
        ]

        # Calcular los tiempos desplazados restándoles el tiempo de rate
        defined_t_values_shifted = [
            t + shifted_recovery_interval_ms for t in defined_t_values if t + shifted_recovery_interval_ms <= time_interval_ms
        ]

        # Calcular la capacidad en los puntos desplazados
        defined_capacity_values_shifted = [
            self.available_capacity(TimeDuration(int(t - shifted_recovery_interval_ms), TimeUnit.MILLISECOND), len(self.limits) - 1)
            for t in defined_t_values_shifted
        ]

        # Convertir los valores del eje x al formato inicial especificado por el usuario
        original_times_in_specified_unit = [
            t / time_interval.unit.to_milliseconds() for t in defined_t_values
        ]
        shifted_times_in_specified_unit = [
            t / time_interval.unit.to_milliseconds() for t in defined_t_values_shifted
        ]
        x_label = f"Tiempo ({time_interval.unit.value})"

        # Crear la gráfica
        fig, ax = plt.subplots(figsize=(10, 6))

        line_width = 2

        # Dibujar la capacidad acumulada (azul)
        ax.step(original_times_in_specified_unit, defined_capacity_values, where='post', color="green", linewidth=line_width, label="Accumulated capacity")
        ax.fill_between(original_times_in_specified_unit, 0, defined_capacity_values, step='post', color="green", alpha=0.3)

        # Dibujar la capacidad desplazada (naranja)
        ax.step(shifted_times_in_specified_unit, defined_capacity_values_shifted, where='post', color="orange", linewidth=line_width, label="Shifted capacity")
        ax.fill_between(shifted_times_in_specified_unit, 0, defined_capacity_values_shifted, step='post', color="orange", alpha=0.3)

        # Añadir leyenda y ajustes finales
        ax.set_xlabel(x_label)
        ax.set_ylabel('Capacidad')
        ax.set_ylim(0)
        ax.set_title(f'Capacity areas - {self.name} - {time_interval.value} {time_interval.unit.value}')
        ax.legend()
        ax.grid(True)

        # Mostrar la gráfica
        plt.show()

    def generate_ideal_capacity_curve(self, subscription_time: TimeDuration = None) -> List[Tuple[int, int]]:
        
        quota = self.max_quota_burning_time + self.max_quota_recovery_interval if not subscription_time else subscription_time
        
        values = self.show_available_capacity_curve(quota, debug=True)
        
        return [(v[0]/1000, v[1]) for v in values]


























