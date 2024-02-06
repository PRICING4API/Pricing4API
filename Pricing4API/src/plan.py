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
        # self.__t_ast=self.compute_t_ast(self.__limits)

        


        


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


    def recurs_accumulated_capacity(self, t: int, pos: int,  limits_list: List[Tuple[int, int]]) -> int:

        """Calculates the accumulated capacity at time 't' using the given limits."""

        if pos >= len(limits_list):
            raise IndexError("The 'pos' index is out of range.")

        value, period = limits_list[pos] 
        
        if pos == 0:
            c = value * np.floor((t / period)+1)

        else:
            ni = np.floor(t / period) # determines which interval number (ni) 't' belongs to
            qvalue = value * ni # capacity due to quota
            cprevious = self.recurs_accumulated_capacity(t - ni * period, pos - 1, limits_list)
            ramp = min(cprevious, value) # capacity due to ramp
            c = qvalue + ramp
        
        return c
    
    


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
    
    def show_rate_curve(self, time_interval:int) -> None:
        """ shows the available requests in the plan over time"""
        units, scale =  self.adjust_time_unitsx(time_interval)
        # dado que el rate es una función escalón, no tiene sentido obtener más valores que la unida del rate t`0
        time_values = np.arange(0, time_interval, self.rate_frequency)  # Define el rango de valores de c que desees

        # Calcula los valores de capacidad del rate a representar
        capacity = self.rate_function(time_values)
        # Crea el gráfico
        
        print(time_values)
        print(capacity)
        # Crear la figura principal con dos subgráficos
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))

        # Gráfico principal (la curva completa)
        ax1.step(time_values, capacity, where='post')
        ax1.fill_between(time_values[:-1], capacity[:-1], step='post', color='green', alpha=0.3)  # Rellenar el área bajo la curva
        ax1.set_ylim(0, max(capacity) + 1)  # Forzar el eje Y para que comience en 0
        ax1.set_xlabel(f'Time ({units})')
        ax1.set_ylabel('Requests')
        ax1.set_title(f'Rate curve of plan {self.name}. ({self.rate_value}  req / {self.rate_frequency} sec)')
        ax1.grid(True)  # Agregar un grid

        # Calcular la intersección con la función en x=60
        x_value = 60
        y_value = self.rate_function(x_value)

        # Dibujar la línea roja que termina en la intersección con la función
        ax1.plot([x_value, x_value], [0, y_value], color='red', linestyle='--')
        ax1.plot([0, x_value], [y_value, y_value], color='red', linestyle='--')


        # Mostrar los valores de x e y para la línea roja sin que intersecten con los ejes
        ax1.text(x_value, -0.2, f'x={x_value}', fontsize=12, ha='center')
        ax1.text(-1, y_value + 0.2, f'y={y_value}', fontsize=12, va='center')

        # Subgráfico (solo los primeros 20 segundos)
        units, scale =  self.adjust_time_unitsx(10)
        ax2.step(time_values[:11], capacity[:11], where='post')
        ax2.fill_between(time_values[:11], capacity[:11], step='post', color='green', alpha=0.3)  # Rellenar el área bajo la curva
        # Dibujar círculos sólidos en cada punto del gráfico
        ax2.plot(time_values[:11], capacity[:11], 'o', markersize=3, color='green')

        ax2.set_ylim(0, max(capacity[:11]) + 1)  # Forzar el eje Y para que comience en 0
        ax2.set_xlabel(f'Time ({units})')
        ax2.set_ylabel('Requests')
        ax2.set_title(f'First {10*self.__t[0]} seconds') 
        # Establecer las ubicaciones del grid en el eje x
        ax2.set_xticks(time_values[:11])
        ax2.grid(True)  

        # Mostrar la figura con los dos subgráficos
        plt.tight_layout()
        plt.show()
    
    
    
    # def show_quote_curve(self, time_interval:int) -> None:
    #     """ shows the available requests in the plan over time"""
    #     units, scale =  self.adjust_time_unitsx(time_interval)
        
    #     # dado que el rate es una función escalón, no tiene sentido obtener más valores que la unida del rate t`0
    #     if len(self.quote_frequency)>0:
    #         time_values = np.arange(0, time_interval, self.quote_frequency[0])
    #     else:
    #         time_values = None

    #     if time_values is not None:
    #         # Calculate the values of capacity of the rate to be represented
    #         capacity = self.quote_function(time_values)
    #         # Create the plot
    #         print(f"This are the time values:{time_values}")
    #         print(f"This are the capacity values:,{capacity}")
    #         fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))

    #         # Gráfico principal (la curva completa)
    #         ax1.step(time_values, capacity, where='post')
    #         ax1.fill_between(time_values[:-1], capacity[:-1], step='post', color='green', alpha=0.3)  # Rellenar el tamaño bajo la curva
    #         ax1.set_ylim(0, max(capacity) + 1)  #
    #         ax1.set_xlabel(f'Time ({units})')
    #         ax1.set_ylabel('Requests')
    #         ax1.set_title(f'Quote curve of plan {self.name}. ({self.quote_value[0]}  req / {self.quote_frequency[0]} sec)')
    #         ax1.grid(True)  # Agregar un grid

    #         # Calcular la intersección con la función en x=60
    #         x_value = 60
    #         y_value = self.quote_function(x_value)

    #         # Dibujar la línea roja que termina en la intersección con la función
    #         ax1.axvline(x=x_value, ymin=0, ymax=y_value/max(capacity), color='red', linestyle='--')
    #         ax1.axhline(y=y_value, xmin=0, xmax=x_value/max(time_values), color='red', linestyle='--')

    #         # Mostrar los valores de x e y para la línea roja sin que intersecten con los ejes
    #         ax1.text(x_value, -0.2, f'x={x_value}', fontsize=12, ha='center')
    #         ax1.text(-1, y_value + 0.2, f'y={y_value}', fontsize=12, va='center')

    #         # Subgráfico (solo los primeros 20 segundos)
    #         units, scale =  self.adjust_time_unitsx(time_interval)
    #         ax2.step(time_values[:11], capacity[:11], where='post')
    #         ax2.fill_between(time_values[:11], capacity[:11], step='post', color='green', alpha=0.3)  # Rellenar elSetBranch bajo la curva
    #         # Dibujar círculos.masks en cada punto del gráfico
    #         ax2.plot(time_values[:11], capacity[:11], 'o', markersize=3, color='green')

    #         ax2.set_ylim(0, max(capacity[:11]) + 1)  # Forzar el eje Y para que comience en 0
    #         ax2.set_xlabel(f'Time ({units})')
    #         ax2.set_ylabel('Requests')
    #         ax2.set_title(f'First {10*self.__t[0]} seconds')
    #         # Establecer las ubicaciones del grid en el eje x
    #         ax2.set_xticks(time_values[:11])
    #         ax2.grid(True)

    #         # Mostrar la figura con los dos subgráficos
    #         plt.tight_layout()
    #         plt.show()
            
    #     else:
    #         print("time_values is None")
        
       

    def show_quote_curve(self, time_interval: int = None) -> None:
        """ shows the available requests in the plan over time"""
        if time_interval is None:
            time_interval = max(self.quote_frequency)
            
        units, scale =  self.adjust_time_unitsx(time_interval)
        
        if len(self.quote_frequency) > 0:
            fig, ax = plt.subplots(figsize=(8, 8))
            patches = []
            colors = [(0, 1, 0), (0, 0, 1)]  # Define the colors in RGB

            for i, (quote_value, quote_frequency) in enumerate(zip(self.quote_value, self.quote_frequency)):
                time_values = np.arange(0, time_interval + 1, quote_frequency)
                capacity = quote_value + quote_value * (time_values // quote_frequency)

                print(f"This are the time values:{time_values}")
                print(f"This are the capacity values:,{capacity}")

                color= colors[i]  # Generate a random color
                ax.step(time_values, capacity, where='post')
                ax.fill_between(time_values, capacity, step='post', color=color, alpha=0.1)

                patch = mpatches.Patch(color=color, label=f'{quote_value} req / {quote_frequency} sec')
                patches.append(patch)

                ax.set_ylim(0, max(capacity) + 1)
                ax.set_xlabel(f'Time ({units})')
                ax.set_ylabel('Requests')
                ax.set_title(f'Quote curve of plan {self.name}.')
                ax.grid(True)

            ax.legend(handles=patches)
            plt.tight_layout()
            plt.show()
        else:
            print("The plan has no quotes.")


    
            
            

    
    
    


    # def maximum_disruption_period(self) -> int:
    #     """
    #     Calculates the maximum disruption period based on the quote, rate, quote_unit, and rate_unit variables.

    #     :return: The maximum disruption period.
    #     :rtype: int
    #     """
    #     assert self.__quote is not None and self.__rate is not None and self.__quote_unit is not None and self.__rate_unit is not None, "Variables quote, rate, quote_unit, and rate_unit must be defined before maximum_disruption_period is called"

    #     tt = (self.__quote / self.__rate) * self.__rate_unit
    #     tq = self.__quote_unit
    #     return tq - tt

    # def max_time_to_consume_at(self, rate: int) -> int:
        
    #     tt =(self.__quote / rate) * self.__rate_unit

    #     return tt
    

    # def maximum_quote(self) -> float:
    #     return self.__quote * self.__max_number_of_subscriptions
    
    # def maximum_rate(self) -> float:
    #     return self.__rate * self.__max_number_of_subscriptions

    # def cost(self, time: int, requests: int) -> float:
    #     C_0=self.__price
    #     C_1=self.__overage_cost
    #     plan_capacity = self.capacity(time)

    #     if requests > plan_capacity:
    #         return -1
    #     return C_0 * (math.ceil(time/self.__billing_unit)) + heaviside(requests-self.capacity(time))*C_1*(requests-self.capacity(time))

    # def cost_effective_threshold(self, plan)-> int:
    #     assert self.__price <= plan.price, "The price of plan " + plan.name + " must be greater than plan " + self.__name

    #     threshold = self.__quote + math.floor((plan.price - self.__price)/self.__overage_cost)
    #     return threshold





