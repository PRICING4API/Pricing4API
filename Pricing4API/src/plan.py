import math
from matplotlib import pyplot as plt
import numpy as np
from src.utils import heaviside
from typing import Optional


# pyreverse: Plan -> Pricing

class RateFunction:
    def __init__(self, rate_value: int, rate_unit: int):
        self.r = rate_value
        self.tr = rate_unit

    def __call__(self, time_instant: int) -> int:
       # c= math.floor(time_instant/self.tr) +1 
        c= (np.floor(time_instant/self.tr)+1) * self.r
        return c
    
class Plan:
    s_month = 3600 * 24 * 30

    def __init__(self, name: str, billing: tuple[float, int, Optional[float]] = None,
                rate: tuple[int, int] = None, quote: list[tuple[int, int]] = None, max_number_of_subscriptions: int = 1, **kwargs):
        
        """
    Initializes a new instance of the class.
    
    Args:
        name (str): Name of the plan.
        rate (int): The number of possible requests for a plan within a certain time frame.
        rate_unit (int): The time unit of the rate.
        quote (int): The number of possible requests for a plan within a certain time frame.
        quote_unit (int): The time unit of the quote.
        price (float): The subscription price of a plan.
        billing_unit (int, optional): The payment frequency. Defaults to one month.
        overage_cost (int, optional): The price per additional request. Defaults to 0.
        max_number_of_subscriptions (int, optional): The maximum number of subscriptions. Defaults to 1.
    
    Raises:
        AssertionError: If the quote unit is not greater than the rate unit.
    """
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

            
        
        if quote is not None:
            for q in quote:
                self.__q.append(q[0])
                self.__t.append(q[1])
        
        self.__max_number_of_subscriptions = max_number_of_subscriptions

        #Linking plan objects
        self.__next_plan = self
        self.__previous_plan = self

        self.__m=len(self.__q)-1
        self.__t_ast=self.compute_t_ast()
        
        # assert quote_unit > self.__rate_unit, "Quote should be defined on a unit of time greater than rate"

    
    
    def rate_at(self, time: int):
        return   self.rate_function(time)

    @property 
    def rate_frequency(self):
        return self.__t[0]
    
    @property 
    def rate_value(self):
        return self.__q[0]
    
    @property
    def next_plan(self):
        return self.__next_plan
    
    def setNext(self, plan: "Plan"):
        self.__next_plan = plan
    
    @property
    def previous_plan(self):
        return self.__previous_plan
    
    def setPrevious(self, plan: "Plan"):
        self.__previous_plan = plan
    
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
    

    # @property
    # def planes_para_actualizar(self):
    #     return self.upgrade_quote/self.__quote
   
    

    # Getters and Setters
    @property
    def name(self):
        return self.__name
    
    @property
    def price(self):
        return self.__price
    
    # @property
    # def rate(self):
    #     return self.__q[0]
    
    # @property
    # def rate_unit(self):
    #     return self.__t[0]
    
    # @property
    # def quote(self):
    #     return self.__q[1:-1]
    
    # @property
    # def quote_unit(self) -> int:
    #     return self.__t[1:-1]

    # @property
    # def max_number_of_subscriptions(self):
    #     return self.__max_number_of_subscriptions

    # def capacity(self, time: int) -> float:
    #     """
    #     Calculates the capacity based on the given time.

    #     Parameters:
    #         time (int): The time value for which to calculate the capacity.

    #     Returns:
    #         float: The calculated capacity value.

    #     Raises:
    #         AssertionError: If the variables quote, rate, quote_unit, and rate_unit are not defined before calling the capacity function.
    #     """
    #     assert self.__quote is not None and self.__rate_unit is not None and self.__quote_unit is not None and self.__rate_unit is not None, "Variables quote, rate, quote_unit, and rate_unit must be defined before capacity is called"

    #     T = time - math.floor(time / self.__quote_unit) * self.__quote_unit
    #     tt = (self.__quote / self.__rate) * self.__rate_unit  # t*
    #     A = math.ceil((time - tt) / self.__quote_unit) * self.__quote
    #     B = heaviside(tt - T) * (T / self.__rate_unit) * self.__rate
    #     return A + B

    def compute_t_ast(self):
        t_ast = [0]
        for i in range(1,self.__m+1):
            t_ast.append(self.min_time(self.__q[i],i_initial=i-1))
        return t_ast

    def max_capacity(self, t):
        t_ast = self.__t_ast

        C=0
        i=self.__m

        while i>0:
            n_i=math.floor(t/self.__t[i])
            
            C+=n_i*self.__q[i]
            t-=n_i*self.__t[i]

            if t<t_ast[i]:
                i-=1
            else:
                C+=self.__q[i]
                return C
            
        C+=t*self.__q[0]/self.__t[0]
        return C
    
    def min_time(self, C, i_initial=None):
    
        if i_initial is None:
            i_initial = self.__m
        
        #Inicialización
        T=0
        i= i_initial

        #Iteración i
        while i>0:
            nu=math.floor(C/self.__q[i])

            #Cálculo de delta
            delta= C==nu*self.__q[i]

            #Cálculo n_i
            n_i=(C!=0)*(nu-delta)

            #Traslación del origen
            T+=n_i*self.__t[i]
            C-=n_i*self.__q[i]

            #Actualización de i
            i-=1
        
        #Iteración i=0
        T+=C * self.__t[0]/self.__q[0]

        return T
    

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

"""
        plt.plot(time_values, resultados, label='requests', color='b')
        #plt.plot(t / escala, f_t, label='f(t) = t')
        # Personaliza el gráfico (opcional)
        plt.title(f'Capacity curve of plan {self.name} due to rate')
        plt.xlabel(f'Time ({units})')
        #plt.ylabel('f(c)')
        #plt.grid(True)
        #plt.legend()

        # Muestra el gráfico
        plt.show()
"""

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

    
    
    # def getRate(self, time: int) -> float:
    #     return self.__rate * time / self.__rate_unit

    # #Se descartará
    # def getQuote(self, time: int) -> float:
    #     return math.ceil(time/self.__quote_unit)*self.__quote
    
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

    # def plot_rate(self, total_seconds : int) -> None:
    #     time_values = np.linspace(0, total_seconds, 10000)
    #     rate_values = [self.getRate(time) for time in time_values]

    #     plt.plot(time_values, rate_values)
    #     plt.xlabel('Time (seconds)')
    #     plt.ylabel('Rate')
    #     plt.title('Rate over Time')
    #     plt.show()
        
    # def plot_quote(self, total_seconds : int) -> None:
    #     time_values = np.linspace(0, total_seconds, 10000)
    #     rate_values = [self.getQuote(time) for time in time_values]

    #     plt.plot(time_values, rate_values)
    #     plt.xlabel('Time (seconds)')
    #     plt.ylabel('Quote')
    #     plt.title('Quote over Time')
    #     plt.show()
#


#  def test_plot_cost():

#     t_max = 10
#     req_max = 1000
#     n = 1000
#     n_levels = 10

#     t_vec = np.linspace(0, t_max, n)
#     req_vec = np.linspace(0, req_max, n)

#     t_surf, req_surf = np.meshgrid(t_vec, req_vec)

#     t_q = 7
#     t_r = 1
#     r = 100
#     q = 500
#     p_v = 1
#     p_0 = 100

#     t_star = q / r * t_r

#     A = lambda t: np.ceil((t - t_star) / t_q) * q
#     T = lambda t: t - np.floor(t / t_q) * t_q
#     B = lambda t: np.heaviside(t_star - T(t), 0) * T(t) / t_r * r
#     Max_Capacity = lambda t: A(t) + B(t)

#     g = lambda t, req: p_v * (req - Max_Capacity(t))
#     Cost = lambda t, req: p_0 + np.heaviside(req - Max_Capacity(t), 0) * g(t, req)

#     fig = plt.figure()
#     ax = fig.add_subplot(111, projection='3d')
#     z_values = Cost(t_surf, req_surf)
#     z_values = np.where(np.isfinite(z_values), z_values, 0)
#     surf = ax.plot_surface(t_surf, req_surf, z_values, edgecolor='none', alpha=0.3, cmap='coolwarm')
#     fig.colorbar(surf)
    
#     ax.set_box_aspect([1, 1, 0.5])
    

#     ax.contour(t_surf, req_surf, z_values, zdir='z', offset=-10, cmap='coolwarm')
#     ax.contour(t_surf, req_surf, z_values, zdir='x', offset=-10, cmap='coolwarm')
#     ax.contour(t_surf, req_surf, z_values, zdir='y', offset=1000, cmap='coolwarm')

#     ax.set(xlim=(-10, t_max+10), ylim=(10, req_max+10), zlim=(-10, np.max(z_values)+10),
#     xlabel='t (days)', ylabel='Requests', zlabel='Cost')

#     plt.show()
