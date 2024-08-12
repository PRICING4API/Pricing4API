from ..plan import Plan
from ..pricing import Pricing

plans = []

name = "Amadeus hardcode Test"
billing = (0.0, 3600*24*30, 0.0)
rate = (10, 1)
quota = [(2400, 3600)]
plan_test = Plan(name, billing, rate, quota)

name = "Amadeus hardcode Production"
billing = (0.0, 3600*24*30, 0.015)
rate = (40, 1)
quota = [(2400, 3600)]
plan_prod = Plan(name, billing, rate, quota)

plans.append(plan_test)
plans.append(plan_prod)

pricing = Pricing("Amadeus", plans, "requests")
pricing.link_plans()

pricing.show_datasheet()