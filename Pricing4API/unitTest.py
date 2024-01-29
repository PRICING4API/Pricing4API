import unittest
from src.plan import Plan
from src.pricing import Pricing
from src.utils import format_time

s_second = 1
s_minute= 60
s_hour = 3600
s_day = 3600 * 24
s_month = 3600 * 24 * 30


#PRICING DBLP
LDBLP=[]
PlanProDBLP= Plan('Pro', (9.99, 1, None), (2, s_second), [(20, s_minute), (1000, s_hour)])
LDBLP.append(PlanProDBLP)
PricingDBLP = Pricing('DBLP', LDBLP, 'queries')

#LINK PLANS
PricingDBLP.link_plans()


#Lista de Pricings
PricingList = [PricingDBLP]


# Tiempo


class UnitTestPlans(unittest.TestCase):

    def test_pricingDBLP(self):
        self.assertEqual(PricingDBLP.plans[0].name, 'Pro', "Plan name should be 'Pro'")
        self.assertEqual(PricingDBLP.plans[0].max_capacity(s_day), 24*1000, f"The capacity should be {24*1000} {PricingDBLP.billing_object}")
        self.assertEqual(PricingDBLP.plans[0].max_capacity(s_month), 30*24*1000, f"The capacity should be {30*24*1000} {PricingDBLP.billing_object}")
        self.assertEqual(PricingDBLP.plans[0].max_capacity(s_hour*12+s_minute*7), 20*7+1000*12, f"The capacity should be {20*7+1000*12} {PricingDBLP.billing_object}")


    
if __name__ == '__main__':
    unittest.main()


