
from src.plan import Plan
from src.pricing import Pricing
from src.utils import format_time

from matplotlib import pyplot as plt
import numpy as np

s_second = 1
s_minute= 60
s_hour = 3600
s_day = 3600 * 24
s_month = 3600 * 24 * 30
# def __init__(self, name: str, billing: tuple[float, int, Optional[float]] = None,
#                 rate: tuple[int, int] = None, quote: list[tuple[int, int]] = None, max_number_of_subscriptions: int = 1, **kwargs):
PlanDBLP = Plan('DBLP', (9.99, 1, None), (2, s_second), [(20, s_minute), (1000, s_minute*60)])
PlanTP1 = Plan('Pro', (0.00, s_month, 0.01), None ,[(45000, s_month)])
PlanTP1 = Plan('Pro', (0.00, s_month, 0.01), None ,[(45000, s_month)])


LDBLP=[]
PlanProDBLP= Plan('Pro', (9.99, 1, None), (1, 2*s_second), [(20, s_minute), (1000, s_hour)])
LDBLP.append(PlanProDBLP)
PricingDBLP = Pricing('DBLP', LDBLP, 'queries')

PlanProDBLP.show_rate_curve(90)
PlanProDBLP.show_rate_curve(900)

PricingMassEmail = Pricing("Mass Email", [
                            Plan('Basic', (5, 1, None), (1, s_hour)),
                            Plan('Pro', (10, 1, None), (2, s_hour))],
                            "Requests")


PricingMassEmail.plans[0].show_rate_curve(3*s_hour)
PricingMassEmail.plans[1].show_rate_curve(3*s_hour)

plans = [PlanDBLP, PlanTP1]

# Tiempo
t = 24*60*60*30

def test_capacity():
    for plan in plans:
        tqList = [t, t*2, t*3, t*4, t*5]
        for tq in tqList:
            assert plan.capacity(tq-1) <= plan.capacity(tq) < plan.capacity(tq+1), f"Error: Capacity condition not satisfied for tq = {tq} and plan = {plan.name}"
            print("\nRequests in a period of tq-1:", plan.name, ":", format_time(tq-1), ":", plan.capacity(tq-1))
            print("\nRequests in a period of tq:", plan.name, ":", format_time(tq), ":", plan.capacity(tq))
            print("\nRequests in a period of tq+1:", plan.name, ":", format_time(tq+1), ":", plan.capacity(tq+1))
            print('#-------------------------------------------------------------------------------------------#')


def test_max_time_to_consume_at():
    for plan in plans:
        print(plan.name)
        print("-----")
        print(plan.max_time_to_consume_at(30)< plan.max_time_to_consume_at(20))
        print(plan.max_time_to_consume_at(40)> plan.max_time_to_consume_at(30))
        print('\n*-------------------------------------------------------------------------------------------*\n')

def test_disruption_period():
    for plan in plans:
        print(plan.name)
        print("-----")
        print(plan.maximum_disruption_period() == plan.quote_unit - plan.max_time_to_consume_at(plan.rate))
        print(plan.maximum_disruption_period() == plan.quote_unit - plan.max_time_to_consume_at(plan.rate)+1)
        print('\n*-------------------------------------------------------------------------------------------*\n')


def test_cost():
    req=[50, 40000, 100000, 300000]
    for r in req:
        for plan in plans:
            assert plan.cost(plan.quote_unit, plan.quote) == plan.price, f"Error: cost condition not satisfied for plan = {plan.name}"
            print("\nNumber of requests:", r)
            print("\nPlan:", plan.name, "-->Price:", plan.price)
            if plan.cost(plan.quote_unit, r)==-1:
                print("\nCost: It is not possible to satisfy the capacity of the plan in the time set because the capacity in", format_time(plan.quote_unit), "is of", plan.capacity(plan.quote_unit), "requests.")    
            print("\nCost:", plan.cost(plan.quote_unit, r))
            print('#-------------------------------------------------------------------------------------------#')


##Graficas de capacidad, rate y quote

def test_plot_capacity():
    print(Plan1.plot_capacity(s_day*2))
    print(Plan2.plot_capacity(s_month*2))
    print(Plan3.plot_capacity(s_month*2))
    print(Plan4.plot_capacity(s_month*2))


def test_plot_rate():
    print(Plan1.plot_rate(s_day*2))
    print(Plan2.plot_rate(s_month*2))
    print(Plan3.plot_rate(s_month*2))
    print(Plan4.plot_rate(s_month*2))


def test_plot_quote():
    print(Plan1.plot_quote(s_day*2))
    print(Plan2.plot_quote(s_month*2))
    print(Plan3.plot_quote(s_month*2))
    print(Plan4.plot_quote(s_month*2))

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

if __name__ == '__main__':
    # test_capacity()
    # test_max_time_to_consume_at()
    # test_disruption_period()
    # test_cost()
    #test_plot_capacity()
    #test_plot_rate()
    #test_plot_quote()
    #test_plot_cost()
    for plan in plans:
        print(plan.max_capacity(s_minute*2))
        print(plan.max_capacity(s_hour))
        print(plan.max_capacity(s_hour+s_minute*2))
    