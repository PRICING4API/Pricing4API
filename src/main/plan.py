import math
from matplotlib import pyplot as plt
import numpy as np

from src.utils import heaviside




# pyreverse: Plan -> Pricing
class Plan:
    s_month = 3600 * 24 * 30

    def __init__(self, name: str, rate: int, rate_unit: int, quote: int,
                 quote_unit: int, price: float, billing_unit: int = s_month,
                 overage_cost: int = 0, max_number_of_subscriptions: int = 1):

        self.__name = name
        self.__rate = rate
        self.__rate_unit = rate_unit
        self.__quote = quote
        self.__quote_unit = quote_unit
        self.__price = price
        self.__billing_unit = billing_unit
        self.__overage_cost = overage_cost
        self.__max_number_of_subscriptions = max_number_of_subscriptions
        self.__next_plan = self
        self.__previous_plan = self
        
        assert quote_unit > rate_unit, "Quote should be defined on a unit of time greater than rate"


    
    

    
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
        return self.__price / self.__quote
    
  
    @property
    def overage_quote(self):
        if self.__max_number_of_subscriptions == 1:
            return 0
        return math.floor((self.__price / self.__overage_cost) + self.__quote)

    @property
    def cost_with_overage_quote(self):
        if self.__price == 0.0:
            return "--"
        return (self.__price + self.__overage_cost * (self.overage_quote - self.__quote))

    @property
    def upgrade_quote(self):
        siguiente_plan = self.__next_plan
        if siguiente_plan is None:
            return 0
        elif self.__overage_cost == 0:
            return 0
        return math.floor(self.__quote +(siguiente_plan.price-self.__price)/self.__overage_cost)
    
    @property
    def downgrade_quote(self):
        anterior_plan = self.previous_plan
        if anterior_plan is None:
            return 0
        elif self.__overage_cost == 0:
            return 0
        
        return math.floor(self.__quote +(self.price-anterior_plan.price)/self.__overage_cost)
    
    @property
    def t_m(self):
        return self.__quote / self.__rate
    

    @property
    def planes_para_actualizar(self):
        return self.upgrade_quote/self.__quote
   
    

    # Getters and Setters
    @property
    def name(self):
        return self.__name

    @property
    def rate(self):
        return self.__rate

    @property
    def rate_unit(self):
        return self.__rate_unit


    @property
    def quote(self):
        return self.__quote

    @property
    def quote_unit(self):
        return self.__quote_unit


    @property
    def price(self):
        return self.__price

    @property
    def billing_unit(self):
        return self.__billing_unit

    @property
    def overage_cost(self):
        return self.__overage_cost

    @property
    def max_number_of_subscriptions(self):
        return self.__max_number_of_subscriptions

    
    	
    
    
    def capacity(self, time: int) -> float:
        assert self.__quote is not None and self.__rate is not None and self.__quote_unit is not None and self.__rate_unit is not None, "Variables quote, rate, quote_unit, and rate_unit must be defined before capacity is called"

        T = time - math.floor(time / self.__quote_unit) * self.__quote_unit
        tt = (self.__quote / self.__rate) * self.__rate_unit  # t*
        A = math.ceil((time - tt) / self.__quote_unit) * self.__quote
        B = heaviside(tt - T) * (T / self.__rate_unit) * self.__rate
        return A + B
    

    def maximum_disruption_period(self) -> int:
        assert self.__quote is not None and self.__rate is not None and self.__quote_unit is not None and self.__rate_unit is not None, "Variables quote, rate, quote_unit, and rate_unit must be defined before maximum_disruption_period is called"

        tt = (self.__quote / self.__rate) * self.__rate_unit
        tq = self.__quote_unit
        return tq - tt

    def max_time_to_consume_at(self, rate: int) -> int:
        
        tt =(self.__quote / rate) * self.__rate_unit

        return tt
    
    
    def getRate(self, time: int) -> float:
        return self.__rate * time / self.__rate_unit

    #Se descartará
    def getQuote(self, time: int) -> float:
        return math.ceil(time/self.__quote_unit)*self.__quote
    
    def cost(self, time: int, requests: int) -> float:
        C_0=self.__price
        C_1=self.__overage_cost
        plan_capacity = self.capacity(time)

        if requests > plan_capacity:
            return -1
        return C_0 * (math.ceil(time/self.__billing_unit)) + heaviside(requests-self.capacity(time))*C_1*(requests-self.capacity(time))

    def cost_effective_threshold(self, plan)-> int:
        assert self.__price<=plan.price, "El precio del plan " + plan.name + " debe ser mayor que el plan " + self.__name

        threshold = self.__quote + math.floor((plan.price - self.__price)/self.__overage_cost)
        return threshold

    def plot_rate(self, total_seconds : int) -> None:
        time_values = np.linspace(0, total_seconds, 10000)
        rate_values = [self.getRate(time) for time in time_values]

        plt.plot(time_values, rate_values)
        plt.xlabel('Time (seconds)')
        plt.ylabel('Rate')
        plt.title('Rate over Time')
        plt.show()
        
    def plot_quote(self, total_seconds : int) -> None:
        time_values = np.linspace(0, total_seconds, 10000)
        rate_values = [self.getQuote(time) for time in time_values]

        plt.plot(time_values, rate_values)
        plt.xlabel('Time (seconds)')
        plt.ylabel('Quote')
        plt.title('Quote over Time')
        plt.show()

# def test_plot_cost():

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
