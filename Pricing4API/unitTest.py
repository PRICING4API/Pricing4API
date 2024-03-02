import unittest
from Pricing4API.plan import Plan
from Pricing4API.pricing import Pricing
from Pricing4API.utils import format_time

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


list_t_c = [(0, 1), (1, 1), (2, 2), (3, 2), (4, 3), (5, 3), (38, 20), (39, 20), (40, 20), (41, 20), (60,21), (98, 40), (99, 40)]

t =[0,1,2,3,4,5,6,37,38,39,40,41,60,61,118,119,120,121,998,999,1000,1001,1002,3597,3598,3599,3600,3601,3602]


class TestCapacityDBLP(unittest.TestCase):

    def test_capacityDBLP(self):

        for time, exp_capacity in list_t_c:

            actual_capacity = PlanProDBLP.available_capacity(time, len(PlanProDBLP.limits) - 1)

            self.assertEqual(actual_capacity, exp_capacity, f"Error: Capacity in t = {time} should be equal to {exp_capacity} but it is {actual_capacity}")

 

class TestMinTimeDBLP(unittest.TestCase):

    

    for tiempo in t:

        result = PlanProDBLP.available_capacity(tiempo, len(PlanProDBLP.limits) - 1)

        print(f"tiempo={tiempo}, result={result}")

class TestAvailableCapacityDBLP(unittest.TestCase):

    def test_available_capacity(self):
        # Test with integer inputs
        self.assertEqual(PlanProDBLP.available_capacity(60, len(PlanProDBLP.limits) - 1), PlanProDBLP.available_capacity("1m", len(PlanProDBLP.limits) - 1))
        self.assertEqual(PlanProDBLP.available_capacity(60*60, len(PlanProDBLP.limits) - 1), PlanProDBLP.available_capacity("1h", len(PlanProDBLP.limits) - 1))
        self.assertEqual(PlanProDBLP.available_capacity(60*60*24, len(PlanProDBLP.limits) - 1), PlanProDBLP.available_capacity("1d", len(PlanProDBLP.limits) - 1))
            

if __name__ == '__main__':

    unittest.main()


