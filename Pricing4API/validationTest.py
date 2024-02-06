
from typing import List, Tuple
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

# Plan(name: str, billing: tuple[float, int, Optional[float]] = None, rate: tuple[int, int] = None, quote: list[tuple[int, int]] = None, max_number_of_subscriptions: int = 1, **kwargs)

LDBLP=[]
PlanProDBLP= Plan('Pro', (9.99, 1, None), (1, 2*s_second), [(20, s_minute), (1000, s_minute*60)])
LDBLP.append(PlanProDBLP)
PricingDBLP = Pricing('DBLP', LDBLP, 'queries')






def pass_msg(msg:str)->str:

    return("\033[32m!" + msg + "\033[0m")

def test_capacity(limits: List[Tuple[int, int]], list_t_c: List[Tuple[int, int]], name:str="" ):

    print("Testing recurs_accumulated_capacity! " + name)

    try:
        for time, exp_capacity in list_t_c:
            actual_capacity = PlanProDBLP.recurs_accumulated_capacity(time, len(limits) - 1, limits)
            assert actual_capacity == exp_capacity, f"Error({name}): Capacity in t = {time} should be equal to {exp_capacity} but it is {actual_capacity}"
        # Si llega aquí, significa que no se lanzó ninguna AssertionError
       
        print(pass_msg(f"Los tests de capacidad acumulada {name} pasaron satisfactoriamente!"))   

    except AssertionError as e:  

        print(f"\033[31m{e}\033[0m")


def test_min_time(limits: List[Tuple[int, int]],list_c_t: List[Tuple[int, int]],name:str="" ):

    print("Testing min_time! " + name)

    try:
        for capacity, exp_time in list_c_t:
            actual_time = PlanProDBLP.min_time(capacity, limits)
            assert actual_time == exp_time, f"Error: Minimum time to reach {capacity} is: {actual_time} should be equal to {exp_time}"        # Si llega aquí, significa que no se lanzó ninguna AssertionError

        print(pass_msg(f"Las pruebas de min_time de {name} pasaron satisfactoriamente!"))

    except AssertionError as e:

        print(f"\033[31m{e}\033[0m")


list_t_c = [(0, 1), (1, 1), (2, 2), (3, 2), (4, 3), (5, 3), (38, 20), (39, 20), (40, 20), (41, 20), (60,21), (98, 40), (99, 40)]
list_c_t = [(0, 0), (1, 0), (2, 2), (3, 4), (4, 6), (5, 8), (20, 38), (21, 60)]


if __name__ == '__main__':
    test_capacity(PlanProDBLP.limits, list_t_c, "PlanProDBLP")
    test_min_time(PlanProDBLP.limits, list_c_t, "PlanProDBLP")
    
    print(PlanProDBLP.limits)

    