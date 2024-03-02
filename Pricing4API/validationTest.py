
from typing import List, Tuple
from plan import Plan
from pricing import Pricing


from matplotlib import pyplot as plt
import numpy as np

s_second = 1
s_minute= 60
s_hour = 3600
s_day = 3600 * 24
s_month = 3600 * 24 * 30

# Plan(name: str, billing: tuple[float, int, Optional[float]] = None, rate: tuple[int, int] = None, quote: list[tuple[int, int]] = None, max_number_of_subscriptions: int = 1, **kwargs)

LDBLP=[]
PlanProDBLP= Plan('Pro', (9.95, s_month, None), (1, 2*s_second), [(20, s_minute), (100, s_minute*60)])
# PlanUltraDBLP= Plan('Ultra', (79.95, 1, 0.00085), (1, 2*s_second), [(20, s_minute), (100000, s_minute*60)],30)
LDBLP.append(PlanProDBLP)
# LDBLP.append(PlanUltraDBLP)
PricingDBLP = Pricing('DBLP', LDBLP, 'queries')
PricingDBLP.link_plans()

ListSendGrid=[]

ListSendGrid.append(Plan('Basic', (0.0, s_month, 0.001), (10, s_second), [(1500, s_month)]))
ListSendGrid.append(Plan('Pro', (9.95, s_month, 0.001), (10, s_second), [(40000, s_month)], 10))
ListSendGrid.append(Plan('Ultra', (79.95, s_month, 0.00085), (10, s_second), [(100000, s_month)], 10))
ListSendGrid.append(Plan('Mega', (199.95, s_month, 0.00005), (50, s_second), [(300000, s_month)], 50))

PricingSendGrid = Pricing('SendGrid', ListSendGrid, 'mails')
PricingSendGrid.link_plans()





def error_msg(msg)->str:

    return("\033[31m!" + msg + "\033[0m")

def pass_msg(msg:str)->str:

    return("\033[32m!" + msg + "\033[0m")

def test_capacity(list_t_c: List[Tuple[int, int]], plan: 'Plan'):

    print("Testing accumulated_capacity! " + plan.name)

    try:
        for time, exp_capacity in list_t_c:
            actual_capacity = plan.available_capacity(time, len(plan.limits) - 1)
            assert actual_capacity == exp_capacity, f"Error({plan.name}): Capacity in t = {time} should be equal to {exp_capacity} but it is {actual_capacity}"
        # Si llega aquí, significa que no se lanzó ninguna AssertionError
       
        print(pass_msg(f"Los tests de capacidad acumulada {plan.name} pasaron satisfactoriamente!"))   

    except AssertionError as e:  

        print(f"\033[31m{e}\033[0m")


def test_min_time(list_c_t: List[Tuple[int, int]], plan: 'Plan'):

    print("Testing min_time! " + plan.name)

    try:
        for capacity, exp_time in list_c_t:
            actual_time = plan.min_time(capacity)
            assert actual_time == exp_time, f"Error: Minimum time to reach {capacity} is: {actual_time} should be equal to {exp_time}"        # Si llega aquí, significa que no se lanzó ninguna AssertionError

        print(pass_msg(f"Las pruebas de min_time de {plan.name} pasaron satisfactoriamente!"))

    except AssertionError as e:

        print(f"\033[31m{e}\033[0m")


t_ast = PlanProDBLP.compute_t_ast()

def test_min_time_automated(plan: 'Plan'):

    print("Testing min_time by using accumulated capacity! " + plan.name)

    try:

        # Test the min_time function comparing it with the recursive version of capacity

        inconsistency_found = False

        num_tests = 12000

        t_values = range(0, num_tests)

        for time in t_values:

            accum_capacity  = plan.available_capacity(time, len(PlanProDBLP.limits) - 1)

            m_time = plan.min_time(accum_capacity)

            #dado con min_time te devuelve el suelo del tiempo, hay que ser cuidadoso al comparar

            # los instnataneos de tiempo que no sean múltiplos del rate hay que pasarlos al múltoplo próximo más cercano por debajo

            t_aux= (time//plan.limits[0][1])*plan.limits[0][1]

            #también hay que ser cuidados con la capacidad entre múltiplos de t* + la quota

            if (m_time % (t_ast[1]!=0 + plan.limits[0][1]) and t_aux != m_time): #si el tiempo mínimo es múltiplo de t* y no es múltiplo de rate

                inconsistency_found = True

                message=f"Inconsistency found: accum_capacity(t={int(time)})={int(accum_capacity)}, min_time(C={int(accum_capacity)})={int(m_time)}(taux={int(t_aux)}"

                print(error_msg(message))

        if inconsistency_found == False:

            print(pass_msg(f"Min-time function passed the {num_tests} on {plan.name} automatically generated!"))

    except AssertionError as e:

        print(f"\033[31m{e}\033[0m")


list_t_c = [(0, 1), (1, 1), (2, 2), (3, 2), (4, 3), (5, 3), (38, 20), (39, 20), (40, 20), (41, 20), (60,21), (98, 40), (99, 40)]

list_c_t = [(0, 0), (1, 0), (2, 2), (3, 4), (4, 6), (5, 8), (20, 38), (21, 60)]


if __name__ == '__main__':
    
    # test_capacity(list_t_c, PlanProDBLP)
    # test_min_time(list_c_t, PlanProDBLP)
    # test_min_time_automated(PlanProDBLP)
    
    # PlanProDBLP.show_available_capacity_curve(120)
    # PlanProDBLP.show_available_capacity_curve(1200)
    # PlanProDBLP.show_available_capacity_curve(2400)
    # PlanProDBLP.show_available_capacity_curve(7200)

    # PricingSendGrid.plans[0].show_available_capacity_curve(s_month)
    # PricingSendGrid.plans[1].show_available_capacity_curve(s_month)

    #PlanProDBLP.show_capacity_areas(120)

    print(PricingSendGrid.show_datasheet())



