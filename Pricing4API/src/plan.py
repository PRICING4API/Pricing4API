import math
from matplotlib import pyplot as plt
import numpy as np
# from src.utils import heaviside
from typing import List, Tuple, Optional
import matplotlib.patches as mpatches



# pyreverse: Plan -> Pricing

class RateFunction:
    def __init__(self, rate_value: int, rate_unit: int):
        self.r = rate_value
        self.tr = rate_unit

    def __call__(self, time_instant: int) -> int:
       # c= math.floor(time_instant/self.tr) +1 
        c= (np.floor(time_instant/self.tr)+1) * self.r
        return c

class QuoteFunction:
    def __init__(self, quote_value: int, quote_unit: int):
        self.q = quote_value
        self.tq = quote_unit

    def __call__(self, time_instant: int) -> int:
        c= (np.floor(time_instant/self.tq)+1) * self.q
        return c
    
class Plan:
    s_month = 3600 * 24 * 30

    def __init__(self, name: str, billing: tuple[float, int, Optional[float]] = None,
                rate: tuple[int, int] = None, quote: list[tuple[int, int]] = None, max_number_of_subscriptions: int = 1, **kwargs):
        """
        Constructor for initializing the SubscriptionPlan object.

        Args:
            name (str): The name of the subscription plan.
            billing (tuple[float, int, Optional[float]], optional): The billing details including price, billing unit, and overage cost. Defaults to None.
            rate (tuple[int, int], optional): The rate details including quantity and time. Defaults to None.
            quote (list[tuple[int, int]], optional): The quote details including quantity and time. Defaults to None.
            max_number_of_subscriptions (int, optional): The maximum number of subscriptions allowed. Defaults to 1.
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """
        
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
            self.rate_function= RateFunction(rate[0],rate[1])
            self.__limits.append(rate)

            
        
        if quote is not None:
            for q in quote:
                self.__q.append(q[0])
                self.__t.append(q[1])
                self.quote_function= QuoteFunction(q[0],q[1])
                self.__limits.append(q)

        
        self.__max_number_of_subscriptions = max_number_of_subscriptions

        #Linking plan objects
        self.__next_plan = self
        self.__previous_plan = self

        self.__m=len(self.__q)-1
        self.__t_ast=self.compute_t_ast(self.__limits)
        #self.__t_ast=self.compute_t_ast()
        


        


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
        """
        return self.__q[0]

    @property
    def rate_frequency(self) -> int:
        """
        Getter for the rate frequency of the subscription plan.
        """
        return self.__t[0]
    
    @property
    def quote_value(self)-> list:
        """
        Getter for the quotes values of the subscription plan.
        """
        return self.__q[1:]
    
    @property
    def quote_frequency(self) -> list:
        """
        Getter for the quotes frequencies of the subscription plan.
        """
        return self.__t[1:]

    @property
    def billing_unit(self) -> int:
        """
        Getter for the billing unit of the subscription plan.
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
    def next_plan(self) -> str:
        """
        Getter for the next subscription plan in the linked list.
        """
        return self.__next_plan
    
    def setNext(self, plan: "Plan"):
        self.__next_plan = plan

    @property
    def previous_plan(self) -> str:
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
        if self.__price == 0.0:
            return 0.0
        return self.__price / self.__q 
    
  
    @property
    def overage_quote(self):
        if self.__max_number_of_subscriptions == 1:
            return 0
        return math.floor((self.__price / self.__overage_cost) + self.__q)

    @property
    def cost_with_overage_quote(self):
        if self.__price == 0.0:
            return "--"
        return (self.__price + self.__overage_cost * (self.overage_quote - self.__q))

    @property
    def upgrade_quote(self):
        siguiente_plan = self.__next_plan
        if siguiente_plan is None:
            return 0
        elif self.__overage_cost == 0:
            return 0
        return math.floor(self.__q +(siguiente_plan.price-self.__price)/self.__overage_cost)
    
    @property
    def downgrade_quote(self):
        anterior_plan = self.previous_plan
        if anterior_plan is None:
            return 0
        elif self.__overage_cost == 0:
            return 0
        
        return math.floor(self.__q +(self.price-anterior_plan.price)/self.__overage_cost)
    
    # @property
    # def t_m(self):
    #     return self.__quote / self.__rate_value


    # Getters and Setters


    def accumulated_capacity(self, t: int, pos: int,  limits_list: List[Tuple[int, int]]) -> int:

        """Calculates the accumulated capacity at time 't' using the given limits."""

        if pos >= len(limits_list):
            raise IndexError("The 'pos' index is out of range.")

        value, period = limits_list[pos] 
        
        if pos == 0:
            c = value * np.floor((t / period)+1)

        else:
            ni = np.floor(t / period) # determines which interval number (ni) 't' belongs to
            qvalue = value * ni # capacity due to quota
            cprevious = self.accumulated_capacity(t - ni * period, pos - 1, limits_list)
            ramp = min(cprevious, value) # capacity due to ramp
            c = qvalue + ramp
        
        return c
    
    def min_time(self, capacity_goal:int, limit: List[Tuple[int, int]], i_initial=None) -> int:

        """Calculates the minimum time to reach a certain capacity goal using the given limits."""

        if i_initial is None:
            i_initial = len(limit) - 1

        #Inicialización
        T=0
        i= i_initial

        if capacity_goal < 0:
            raise IndexError("The 'capacity goal' should be greater or equal to 0.")

        #Iteración i
        while i>0:
            capacity_limit, period_limit= limit[i][0], limit[i][1]
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
        c_r,p_r= limit[0][0], limit[0][1]
        if capacity_goal>0:
            T += np.floor((capacity_goal-1) * p_r/c_r)
        else:
            T =0

        return T
    
    def compute_t_ast(self, limits: List[Tuple[int, int]])-> List[int]:
        t_ast = [0] + [None for _ in range(1, len(limits)-1)]

        for i in range(1,len(limits)-1):
            t_ast[i] = self.min_time(limits[i][0], limits, i_initial=i-1)

        return t_ast
    
    
    

    ## Auxiliary functions
    def adjust_time_unitsx(self, t_max:int) -> (str,int):
        """ Determine the units and scale for the time axis """
        if t_max < 60:
            units = 'Seconds'
            scale = 1
        elif t_max < 3600:
            units = 'Minutes'
            scale = 60
        elif t_max < 86400:
            units = 'Hours'
            scale = 3600
        else:
            units = 'Days'
            scale = 86400
        return units, scale
    
    def show_accumulated_capacity_curve(self, limits: List[Tuple[int, int]],list_t_c: List[Tuple[int, int]], debug:bool=False)->None:

        # Ajustar el gráfico para mostrar una señal de tipo escalón y círculos rellenos donde la función está definida

        # Determinar los puntos donde la función está definida según el segundo valor de la tupla de la primera posición

        step = limits[0][1]  # Coincide con el valor del rate
        time_interval = list_t_c[-1][0]  # Instante del último dato de pruega
        defined_t_values = range(0, time_interval+1, step)  # Puntos definidos de t: 0, 2, 4, 6, ...

        # Calcular valores de capacidad solo en los puntos definidos
        defined_capacity_values = [self.accumulated_capacity(t, len(limits) - 1, limits) for t in defined_t_values]

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
        plt.title("Accumulated capacity)")
        plt.xlabel("Time")
        plt.ylabel("Capacity")
        plt.legend()
        plt.grid(True)
        plt.show()
    
    





