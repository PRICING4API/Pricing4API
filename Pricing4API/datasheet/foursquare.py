from ..plan import Plan
from ..pricing import Pricing

plans = []

name = "FourSquare hardcode Free"
billing = (0.0, 3600*24*30, 0.0)
rate = (500, 3600)
quota = [(5000, 3600)]
plan_test = Plan(name, billing, rate, quota)

plans.append(plan_test)

pricing = Pricing("FourSquare", plans, "requests")
pricing.link_plans()

pricing.show_datasheet()