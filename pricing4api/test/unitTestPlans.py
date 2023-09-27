import unittest
from pricing4api.main.plan import *
from pricing4api.main.pricing import *



s_day = 3600 * 24
s_month = 3600 * 24 * 30

Plan1 = Plan('Basic', 10, 1, 50, s_day, 0, s_month, 0.001)
Plan2 = Plan('Pro', 10, 1, 40000, s_month, 9.95, s_month, 0.001)
Plan3 = Plan('Ultra', 10, 1, 100000, s_month, 79.95, s_month, 0.00085)
Plan4 = Plan('Mega', 50, 1, 300000, s_month, 199.95, s_month, 0.00005)

plans = [Plan1, Plan2, Plan3, Plan4]
pricing= Pricing("SendGrid",plans)


# Tiempo
t = 24*60*60*30

class UnitTestPlans(unittest.TestCase):

    def test_capacity(self):
        for plan in plans:
            tqList = [t, t*2, t*3, t*4, t*5]
            for tq in tqList:
                assert plan.capacity(tq-1) <= plan.capacity(tq) < plan.capacity(tq+1), f"Error: Capacity condition not satisfied for tq = {tq} and plan = {plan.name}"


    def test_max_time_to_consume_at(self):
        for plan in plans:
            for rate in range(int(plan.quote / plan.quote_unit)+1, int(plan.rate) + 1):
                tt = (plan.quote / rate) * plan.rate_unit
                assert plan.max_time_to_consume_at(rate) == tt, f"Error: max_time_to_consume_at condition not satisfied for rate = {rate} and plan = {plan.name}"
                

    def test_disruption_period(self):
        for plan in plans:
            tt = (plan.quote / plan.rate) * plan.rate_unit
            tq = plan.quote_unit
            assert plan.maximum_disruption_period() == tq-tt, f"Error: maximum_disruption_period condition not satisfied for plan = {plan.name}"


    def test_cost(self):
        for plan in plans:
            assert plan.cost(plan.quote_unit, plan.quote) == plan.price, f"Error: cost condition not satisfied for plan = {plan.name}"


    def test_cost_effective_threshold(self):

        assert Plan1.cost_effective_threshold(Plan2)==9999, f"Error: cost_effective_threshold condition not satisfied for Plan2"
        assert Plan2.cost_effective_threshold(Plan3)==110000, f"Error: cost_effective_threshold condition not satisfied for Plan3"
        assert Plan3.cost_effective_threshold(Plan4)==241176, f"Error: cost_effective_threshold condition not satisfied for Plan4"
        
    ##Cambiar casos de pruebas
if __name__ == '__main__':
    unittest.main()

