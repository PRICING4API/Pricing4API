import math
from matplotlib import pyplot as plt
import numpy as np
import numpy as np
from typing import List, Tuple, Optional, Union

from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
import re



# pyreverse: Plan -> Pricing


class Plan:
    """
    A class used to represent a Plan.

    Attributes:
        s_month (int): Static attribute representing the number of seconds in a month.
        __limits (list): A private list to store limits.
        __q (list): A private list to store q values.
        __t (list): A private list to store t values.
        __m (int): A private attribute to store the length of __q.
        __name (str): The name of the plan.
        __price (float): The price of the plan. Only set if billing is not None.
        __billing_unit (int): The billing unit of the plan. Only set if billing is not None.
        __overage_cost (float): The overage cost of the plan. Only set if billing is not None.
        __max_number_of_subscriptions (int): The maximum number of subscriptions for the plan.
        __next_plan (Plan): A reference to the next plan. Initially set to self.
        __previous_plan (Plan): A reference to the previous plan. Initially set to self.
        __t_ast: The result of the compute_t_ast method.

    Methods:
        compute_t_ast: This method is not defined in this snippet.
    """
    s_month = 3600 * 24 * 30

    def __init__(self, name: str, billing: Tuple[float, int, Optional[float]] = None,
                rate: Tuple[int, int] = None, quote: List[Tuple[int, int]] = None, max_number_of_subscriptions: int = 1, **kwargs):
        
        self.__limits=[]
        self.__q=[]
        self.__t=[]
        self.__m=len(self.__q)-1
        self.__name = name
        if billing is not None:
            self.__price = billing[0]
            self.__billing_unit = billing[1]
            self.__overage_cost = billing[2]
        
        if rate is not None:
            self.__q.append(rate[0])
            self.__t.append(rate[1])
            self.__limits.append(rate)

            
        
        if quote is not None:
            for q in quote:
                self.__q.append(q[0])
                self.__t.append(q[1])
                self.__limits.append(q)

        
        self.__max_number_of_subscriptions = max_number_of_subscriptions

        #Linking plan objects
        self.__next_plan = self
        self.__previous_plan = self

        self.__m=len(self.__q)-1
        
        self.__t_ast=self.compute_t_ast()
        


    
    @property
    def q(self) -> list:
        """
        Getter for the q values of the subscription plan.
        """
        return self.__q
    
    @property
    def t(self) -> list:
        """
        Getter for the t values of the subscription plan.
        """
        return self.__t
        
    @property
    def name(self) -> str:
        """
        Getter for the name of the subscription plan.
        """
        return self.__name

    @property
    def price(self) -> float:
        """
        Getter for the price of the subscription plan.
        """
        return self.__price

    @property
    def rate_value(self) -> int:
        """
        Getter for the rate value of the subscription plan.
        La cantidad de peticiones que se pueden hacer en una unidad de tiempo.
        
        """
        return self.__q[0]

    @property
    def rate_frequency(self) -> int:
        """
        Getter for the rate frequency of the subscription plan.
        La unidad de tiempo en la que se mide la velocidad de peticiones.
        """
        return self.__t[0]
    
    @property
    def quote_value(self)-> list:
        """
        Getter for the quotes values of the subscription plan.
        El valor de la cuota límite del plan
        """
        return self.__q[1:]
    
    @property
    def quote_frequency(self) -> list:
        """
        Getter for the quotes frequencies of the subscription plan.
        Cada cuanto tiempo se renueva la cuota límite
        """
        return self.__t[1:]

    @property
    def billing_unit(self) -> int:
        """
        Getter for the billing unit of the subscription plan.
        Cuando se renueva la suscripción del plan
        """
        return self.__billing_unit

    @property
    def overage_cost(self) -> Optional[float]:
        """
        Getter for the overage cost of the subscription plan.
        """
        return self.__overage_cost
    
    @property
    def max_number_of_subscriptions(self) -> int:
        """
        Getter for the maximum number of subscriptions allowed in the subscription plan.
        """
        return self.__max_number_of_subscriptions
    
    @property
    def next_plan(self) -> "Plan":
        """
        Getter for the next subscription plan in the linked list.
        """
        return self.__next_plan
    
    def setNext(self, plan: "Plan"):
        self.__next_plan = plan

    @property
    def previous_plan(self) -> "Plan":
        """
        Getter for the previous subscription plan in the linked list.
        """
        return self.__previous_plan
    
    def setPrevious(self, plan: "Plan"):
        self.__previous_plan = plan
    
    @property
    def limits(self) -> list:
        return self.__limits
    

    
    @property
    def unit_base_cost(self) -> float:
        """
        Cuanto cuesta una unidad de petición sin incurrir en petición adicional
        """
        if self.__price == 0.0:
            return 0.0
        return self.__price / self.__q[-1]
    
  
    @property
    def overage_quote(self):
        """
        Cual es la cuota de peticiones que se pueden hacer antes de superar el coste de suscribirnos a dos
        planes del mismo tipo.
        """
        if self.__price == 0.0 or self.__overage_cost is None or self.__max_number_of_subscriptions == 1:
            return 'N/A'
        return math.floor((self.__price / self.__overage_cost) + self.__q[-1])

    @property
    def cost_with_overage_quote(self):
        """
        Suele ser 2 veces el precio del plan, porque el método anterior calcula el número de peticiones extra que equivalen al 
        precio del plan.
        """
        if self.__price == 0.0 or self.__overage_cost is None:
            return "N/A"
        return (self.__price + self.__overage_cost * (self.overage_quote - self.__q[-1]))

    @property
    def upgrade_quote(self) -> int:
        if self.__next_plan is None or self.__next_plan.price == 0 or self.__next_plan.__overage_cost is None or self.__overage_cost is None:
            return 'N/A'
        return math.floor(self.__q[-1] + (self.__next_plan.price-self.__price)/self.__overage_cost)
    
    @property
    def downgrade_quote(self) -> int:
        if self.previous_plan is None:
            return 'N/A'
        return self.previous_plan.upgrade_quote
    
    @property
    def earliest_coolingdown_threshold(self):
        """
        El truco aquí está en que todo está en las mismas unidades, por tanto esto calcula los segundos
        en el que llego al primer límite de cuota.
        """
        return self.__q[-1] / self.__q[0]
    
    @property
    def max_unavailability_time(self):
        """
         Calcula el tiempo máximo hasta poder volver a hacer peticiones, restándole el necesario para gastar la cuota.
         t[-1] es el tiempo de renovación de la cuota
        """
        return self.__t[-1] - self.earliest_coolingdown_threshold

    @property
    def max_unavailability_percentage(self):
        """
        En porcentaje, el tiempo respecto de la renovación de la cuota que el plan no está disponible para hacer peticiones.
        """
        return round((self.__t[-1] - self.earliest_coolingdown_threshold) * 100 / self.__t[-1], 2)



    def parse_duration(self, duration_str):
        # Parsea la cadena de duración a sus componentes
        duration_parts = re.findall(r'(\d+)([Mwdhms])', duration_str)
        
        # Diccionario para acumular los valores de duración
        duration_values = {"months": 0, "weeks": 0, "days": 0, "hours": 0, "minutes": 0, "seconds": 0}
        
        # Procesa cada parte de la duración
        for amount, unit in duration_parts:
            amount = int(amount)
            if unit == 'M':  # Meses
                duration_values["months"] += amount
            elif unit == 'w':  # Semanas
                duration_values["weeks"] += amount
            elif unit == 'd':  # Días
                duration_values["days"] += amount
            elif unit == 'h':  # Horas
                duration_values["hours"] += amount
            elif unit == 'm':  # Minutos
                duration_values["minutes"] += amount
            elif unit == 's':  # Segundos
                duration_values["seconds"] += amount
                
        # Crea un objeto relativedelta con los meses y timedelta con los otros componentes
        delta = relativedelta(months=duration_values["months"]) + timedelta(
            weeks=duration_values["weeks"],
            days=duration_values["days"],
            hours=duration_values["hours"],
            minutes=duration_values["minutes"],
            seconds=duration_values["seconds"]
        )
        
        return delta
    
    # Primero, definimos la función auxiliar para parsear las cadenas de tiempo
    def parse_time_input(self, time_input):
        if isinstance(time_input, int):
            # Si el tiempo ya está en segundos, simplemente lo devolvemos
            return time_input
        elif isinstance(time_input, str):
            # Aquí convertimos la cadena formateada a segundos o a un objeto relativedelta/timedelta
            duration = self.parse_duration(time_input)  # Utiliza la función parse_duration definida previamente
            # Para este ejemplo, vamos a asumir que necesitamos convertirlo todo a segundos.
            # Esto es más complejo con meses debido a su naturaleza variable, así que se simplificará.
            # Calcula los segundos desde el momento actual (esto es un ejemplo; adapta según sea necesario)
            now = datetime.now()
            future = now + duration
            return (future - now).total_seconds()
        else:
            raise ValueError("El tiempo debe ser un entero o una cadena formateada.")
        

    def available_capacity(self, t: Union[int, str], pos: int) -> int:
        """
        DAMOS RESPUESTA A CUANTAS LLAMADAS PUEDO HACER EN UN MOMENTO DADO
        
        
        Calculates the accumulated capacity at time 't' using the given limits.

        This method calculates the available capacity at a given time 't' for a specific limit position 'pos'.
        The time 't' can be given as an integer (representing seconds) or as a string (which will be parsed using the parse_time_input method).
        The 'pos' parameter represents the position of the limit in the __limits list.

        Args:
            t (Union[int, str]): The time at which to calculate the available capacity. Can be an integer (seconds) or a string (parsed using parse_time_input).
            pos (int): The position of the limit in the __limits list.

        Returns:
            int: The available capacity at time 't' for the limit at position 'pos'.

        Raises:
            IndexError: If 'pos' is out of range of the __limits list.
        """

        """Calculates the accumulated capacity at time 't' using the given limits."""
        
        t_seconds= self.parse_time_input(t)
        if pos >= len(self.__limits):
            raise IndexError("The 'pos' index is out of range.")

        value, period = self.__limits[pos] 
        
        if pos == 0:
            c = value * np.floor((t_seconds / period)+1)

        else:
            ni = np.floor(t_seconds / period) # determines which interval number (ni) 't' belongs to
            qvalue = value * ni # capacity due to quota
            cprevious = self.available_capacity(int(t_seconds - ni * period), pos - 1)
            ramp = min(cprevious, value) # capacity due to ramp
            c = qvalue + ramp
        
        return c
    
    def min_time(self, capacity_goal:int, i_initial=None) -> int:

        """
        AQUI DAMOS RESPUESTA DEL TIEMPO MINIMO PARA ALCANZAR UNA META DE CAPACIDAD
        
        Calculates the minimum time to reach a certain capacity goal using the given limits.
        """

        if i_initial is None:
            i_initial = len(self.__limits) - 1

        #Inicialización
        T=0
        i= i_initial

        if capacity_goal < 0:
            raise IndexError("The 'capacity goal' should be greater or equal to 0.")

        #Iteración i
        while i>0:
            capacity_limit, period_limit= self.__limits[i][0], self.__limits[i][1]
            nu = np.floor(capacity_goal / capacity_limit)

            #Cálculo de delta
            delta= capacity_goal == nu * capacity_limit

            #Cálculo n_i
            if capacity_goal==0:
                n_i= 0
            else:
                if delta:
                    n_i= nu -1
                else:
                    n_i= nu

            #Traslación del origen
            T += n_i * period_limit
            if capacity_goal>0:
                capacity_goal -= n_i * capacity_limit

            #Actualización de i
            i-=1

        #Iteración i=0
        c_r,p_r= self.__limits[0][0], self.__limits[0][1]
        if capacity_goal>0:
            T += np.floor((capacity_goal-1) * p_r/c_r)
        else:
            T =0

        return T
    
    def compute_t_ast(self)-> List[int]:
        t_ast = [0] + [None for _ in range(1, len(self.__limits)-1)]

        for i in range(1,len(self.__limits)-1):
            t_ast[i] = self.min_time(self.__limits[i][0], i_initial=i-1)

        return t_ast
    
    
    def show_available_capacity_curve(self, time_interval: int, debug:bool=False)->None:

        # Ajustar el gráfico para mostrar una señal de tipo escalón y círculos rellenos donde la función está definida

        # Determinar los puntos donde la función está definida según el segundo valor de la tupla de la primera posición

        step = self.__limits[0][1]  # Coincide con el valor del rate
        # time_interval = list_t_c[-1][0]  # Instante del último dato de pruega
        # Instante del último dato de pruega
        defined_t_values = range(0, time_interval+1, step)  # Puntos definidos de t: 0, 2, 4, 6, ...

        # Calcular valores de capacidad solo en los puntos definidos
        defined_capacity_values = [self.available_capacity(t, len(self.__limits) - 1) for t in defined_t_values]

    
        # Crear una versión escalonada de la curva de capacidad
        plt.figure(figsize=(12, 7))


        # Graficar la señal de tipo escalón
        plt.step(defined_t_values, defined_capacity_values, where='post', label="Accumulated capacity", color="blue")
        plt.fill_between(defined_t_values, 0, defined_capacity_values, step='post', color="green", alpha=0.3)

        # Añadir círculos rellenos en los puntos definidos
        plt.scatter(defined_t_values, defined_capacity_values, color="black", s=5, zorder=5)

        if debug:
            #Añadir líneas discontinuas rojas en los puntos definidos
            for t, c in zip(defined_t_values, defined_capacity_values):
                plt.vlines(t, 0, c, colors='red', linestyles='dashed', alpha=0.5)

        # Ajustes finales del gráfico
        plt.title("Accumulated capacity")
        plt.xlabel("Time")
        plt.ylabel("Capacity")
        plt.legend()
        plt.grid(True)
        plt.show()
    

    def show_capacity_areas(self, time_interval: int)->None:

        """Shows the accumulated capacity curve and the wasted capacity threshold curve."""
        
        period_q = self.__limits[1][1]
        wastage_threshold = self.__t_ast[1]

        # Parse time values in list_t_c
        #list_t_c = [(self.parse_time_input(t), c) for t, c in list_t_c]

        step = self.__limits[0][1]  # Coincides with the rate value
        # Instant of the last test data
        defined_t_values = range(0, time_interval+1, step)  # Defined points of t: 0, 2, 4, 6, ...

        # Calculate capacity values only at defined points
        defined_capacity_values = [self.available_capacity(t, len(self.__limits) - 1) for t in defined_t_values]

        defined_t_values_shifted = [t + (period_q-wastage_threshold) for t in defined_t_values if t + (period_q-wastage_threshold) <= time_interval]  # Ensure it does not exceed the limit of 7200

        defined_capacity_values_shifted = [self.available_capacity(int(t-(period_q-wastage_threshold)), len(self.__limits) - 1) for t in defined_t_values_shifted]
        
        plt.figure(figsize=(12, 7))

        line_width = 2
        
        # Plot the original step signal with green fill
        plt.step(defined_t_values, defined_capacity_values, where='post', color="blue", linewidth=line_width, label="Accumulated capacity")
        plt.fill_between(defined_t_values, 0, defined_capacity_values, step='post', color="green", alpha=0.3)

        # Plot the shifted step signal with red fill
        plt.step(defined_t_values_shifted, defined_capacity_values_shifted, where='post', color="darkorange", linewidth=line_width, label="Wasted capacity threshold")
        plt.fill_between(defined_t_values_shifted, 0, defined_capacity_values_shifted, step='post', color="red", alpha=0.3)

        # Add filled circles at the defined and shifted points
        plt.scatter(defined_t_values, defined_capacity_values, color="blue", s=line_width*10, zorder=5)
        plt.scatter(defined_t_values_shifted, defined_capacity_values_shifted, color="darkorange", s=line_width*10, zorder=5)

        # Final adjustments of the graph
        plt.title("Capacity areas")
        plt.xlabel("Time")
        plt.ylabel("Capacity")
        plt.legend()
        plt.grid(True)
        plt.show()
    
    def show_capacity_areas_old(self, list_t_c: List[Tuple[Union[int, str], int]])->None:

        """Shows the accumulated capacity curve and the wasted capacity threshold curve."""
        
        period_q = self.__limits[1][1]
        wastage_threshold = self.__t_ast[1]

        # Parse time values in list_t_c
        list_t_c = [(self.parse_time_input(t), c) for t, c in list_t_c]

        step = self.__limits[0][1]  # Coincides with the rate value
        time_interval = list_t_c[-1][0]  # Instant of the last test data
        defined_t_values = range(0, time_interval+1, step)  # Defined points of t: 0, 2, 4, 6, ...

        # Calculate capacity values only at defined points
        defined_capacity_values = [self.available_capacity(t, len(self.__limits) - 1) for t in defined_t_values]

        defined_t_values_shifted = [t + (period_q-wastage_threshold) for t in defined_t_values if t + (period_q-wastage_threshold) <= time_interval]  # Ensure it does not exceed the limit of 7200

        defined_capacity_values_shifted = [self.available_capacity(int(t-(period_q-wastage_threshold)), len(self.__limits) - 1) for t in defined_t_values_shifted]
        
        plt.figure(figsize=(12, 7))

        line_width = 2
        
        # Plot the original step signal with green fill
        plt.step(defined_t_values, defined_capacity_values, where='post', color="blue", linewidth=line_width, label="Accumulated capacity")
        plt.fill_between(defined_t_values, 0, defined_capacity_values, step='post', color="green", alpha=0.3)

        # Plot the shifted step signal with red fill
        plt.step(defined_t_values_shifted, defined_capacity_values_shifted, where='post', color="darkorange", linewidth=line_width, label="Wasted capacity threshold")
        plt.fill_between(defined_t_values_shifted, 0, defined_capacity_values_shifted, step='post', color="red", alpha=0.3)

        # Add filled circles at the defined and shifted points
        plt.scatter(defined_t_values, defined_capacity_values, color="blue", s=line_width*10, zorder=5)
        plt.scatter(defined_t_values_shifted, defined_capacity_values_shifted, color="darkorange", s=line_width*10, zorder=5)

        # Final adjustments of the graph
        plt.title("Capacity areas")
        plt.xlabel("Time")
        plt.ylabel("Capacity")
        plt.legend()
        plt.grid(True)
        plt.show()
    
    
if __name__ == "__main__":
    s_second = 1
    s_minute = 60
    s_hour = 3600
    s_day = 3600 * 24
    s_month = 3600 * 24 * 30

    # Definir los planes
    plan_basic = Plan('Basic', (0.0, s_month, 0.001), (10, s_second), [(1500, s_month)])
    plan_pro = Plan('Pro', (9.95, s_month, 0.001), (10, s_second), [(40000, s_month)], 10)
    
    print(plan_basic.min_time(21))






