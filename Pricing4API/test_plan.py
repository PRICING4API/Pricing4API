import random
from typing import List, Tuple
import unittest
import numpy as np
from .plan import Plan
from .pricing import Pricing

s_second = 1
s_minute= 60
s_hour = 3600
s_day = 3600 * 24
s_month = 3600 * 24 * 30

#DBLP
LDBLP=[]

LDBLP.append(Plan('Pro', (9.95, s_month, None), (1, 2*s_second), [(20, s_minute), (100, s_hour)]))

PricingDBLP = Pricing('DBLP', LDBLP, 'queries')
PricingDBLP.link_plans()

#SendGrid
ListSendGrid=[]

ListSendGrid.append(Plan('Basic', (0.0, s_month, 0.001), (10, s_second), [(1500, s_month)]))
ListSendGrid.append(Plan('Pro', (9.95, s_month, 0.001), (10, s_second), [(40000, s_month)], 10))
ListSendGrid.append(Plan('Ultra', (79.95, s_month, 0.00085), (10, s_second), [(100000, s_month)], 10))
ListSendGrid.append(Plan('Mega', (199.95, s_month, 0.00005), (50, s_second), [(300000, s_month)], 50))

PricingSendGrid = Pricing('SendGrid', ListSendGrid, 'mails')
PricingSendGrid.link_plans()


def pass_msg(msg:str)->str:

    return("\033[32m!" + msg + "\033[0m")

def error_msg(msg)->str:

    return("\033[31m!" + msg + "\033[0m")

def test_min_time(list_c_t: List[Tuple[int, int]], plan: 'Plan'):
    print("Testing min_time! " + plan.name)

    try:
        for capacity, exp_time in list_c_t:
            actual_time = plan.min_time(capacity)
            assert actual_time == exp_time, f"Error: Minimum time to reach {capacity} is: {actual_time} should be equal to {exp_time}"        # Si llega aquí, significa que no se lanzó ninguna AssertionError

        print(pass_msg(f"Las pruebas de min_time de {plan.name} pasaron satisfactoriamente!"))

    except AssertionError as e:

        print(f"\033[31m{e}\033[0m")




def test_min_time_automated(plan: 'Plan'):

    print("Testing min_time by using accumulated capacity! " + plan.name)

    try:

        # Test the min_time function comparing it with the recursive version of capacity

        inconsistency_found = False

        num_tests = 12000

        t_values = range(0, num_tests)
        for time in t_values:

            accum_capacity  = plan.available_capacity(time, len(plan.limits) - 1)

            m_time = plan.min_time(accum_capacity)

            #dado con min_time te devuelve el suelo del tiempo, hay que ser cuidadoso al comparar

            # los instnataneos de tiempo que no sean múltiplos del rate hay que pasarlos al múltoplo próximo más cercano por debajo

            t_aux= (time//plan.limits[0][1])*plan.limits[0][1]

            #también hay que ser cuidados con la capacidad entre múltiplos de t* + la quota

            if (m_time % (plan.compute_t_ast()[1]!=0 + plan.limits[0][1]) and t_aux != m_time): #si el tiempo mínimo es múltiplo de t* y no es múltiplo de rate

                inconsistency_found = True

                message=f"Inconsistency found: accum_capacity(t={int(time)})={int(accum_capacity)}, min_time(C={int(accum_capacity)})={int(m_time)}(taux={int(t_aux)}"

                print(error_msg(message))

        if inconsistency_found == False:

            print(pass_msg(f"Min-time function passed the {num_tests} on {plan.name} automatically generated!"))

    except AssertionError as e:

        print(f"\033[31m{e}\033[0m")





list_c_t = [(0, 0), (1, 0), (2, 2), (3, 4), (4, 6), (5, 8), (20, 38), (21, 60)] # (capacity, time) for DBLP
list_t_c = [(0, 1), (1, 1), (2, 2), (3, 2), (4, 3), (5, 3), (38, 20), (39, 20), (40, 20), (41, 20), (60,21), (98, 40), (99, 40)] # (time, capacity) for DBLP

class TestPlanMethods(unittest.TestCase):    

    def test_min_time_SendGrid(self):
        c_values= random.sample(range(1, 100), 10)
        # According to the Plans of SendGrid
        self.assertEqual(PricingSendGrid.plans[0].min_time(PricingSendGrid.plans[0].limits[0][0]), 0.0)
        self.assertEqual(PricingSendGrid.plans[0].min_time(PricingSendGrid.plans[0].limits[1][0]), 149.0)
        self.assertEqual(PricingSendGrid.plans[1].min_time(PricingSendGrid.plans[1].limits[0][0]), 0.0)
        self.assertEqual(PricingSendGrid.plans[1].min_time(PricingSendGrid.plans[1].limits[1][0]), 3999.0)
        self.assertEqual(PricingSendGrid.plans[2].min_time(PricingSendGrid.plans[2].limits[0][0]), 0.0)
        self.assertEqual(PricingSendGrid.plans[2].min_time(PricingSendGrid.plans[2].limits[1][0]), 9999.0)
        self.assertEqual(PricingSendGrid.plans[3].min_time(PricingSendGrid.plans[3].limits[0][0]), 0.0)
        self.assertEqual(PricingSendGrid.plans[3].min_time(PricingSendGrid.plans[3].limits[1][0]), 5999.0)
        for plans in PricingSendGrid.plans:
            for c in c_values:
                self.assertLessEqual(plans.min_time(c), plans.min_time(c+1))


    def test_min_time_DBLP(self):
        test_min_time(list_c_t, PricingDBLP.plans[0])
        


    def test_min_time_DBLP2(self):
        c_values= random.sample(range(1, 100), 10)
        for plans in PricingDBLP.plans:
            # According to the PlanProDBLP
            self.assertEqual(plans.min_time(plans.limits[0][0]), 0.0) # The minimum time is 0 to consume 1 query
            self.assertEqual(plans.min_time(plans.limits[1][0]), 38.0) # The minimum time is 38 to consume 20 queries
            self.assertEqual(plans.min_time(plans.limits[2][0]), 278.0) # The minimum time is 278 to consume 100 queries
            for c in c_values:
                self.assertLessEqual(plans.min_time(c), plans.min_time(c+1))
    
    def test_min_time_automated_DBLP(self):
        test_min_time_automated(PricingDBLP.plans[0])
    

    # def test_min_time_automated_SendGrid(self):
    #     for plans in PricingSendGrid.plans:
    #         test_min_time_automated(plans)
    

    def test_capacity_DBLP(self):
        for time, exp_capacity in list_t_c:
            actual_capacity = PricingDBLP.plans[0].available_capacity(time, len(PricingDBLP.plans[0].limits) - 1)
            self.assertEqual(actual_capacity, exp_capacity, f"Error: Capacity in t = {time} should be equal to {exp_capacity} but it is {actual_capacity}")
    

    def test_capacity_SendGrid(self):
        t_values= random.sample(range(1, 10000000), 100)
        for plans in PricingSendGrid.plans: 
            for t in t_values:
                self.assertLessEqual(plans.available_capacity(t, len(plans.limits) - 1), plans.available_capacity(t+1, len(plans.limits) - 1))
                

    


if __name__ == '__main__':

    # Revisar compute_t_ast
    # for plans in PricingDBLP.plans:
    #     print(plans.compute_t_ast())
    # for plans in PricingSendGrid.plans:
    #     print(plans.compute_t_ast())


    unittest.main()