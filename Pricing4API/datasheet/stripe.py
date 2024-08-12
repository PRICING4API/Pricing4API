from ..plan import Plan
from ..pricing import Pricing

plans = []

name = "Stripe hardcode Free"
billing = (0.0, 3600*24*30, 0.0)
rate = (25, 1)
quota = [(10000, 3600*24*30)]
plan_test = Plan(name, billing, rate, quota)

name = "Stripe hardcode Live"
billing = (0.0, 3600*24*30, 0.0)
rate = (100, 1)
quota = [(10000, 3600*24*30)]
plan_live = Plan(name, billing, rate, quota)

plans.append(plan_test)
plans.append(plan_live)

pricing = Pricing("Stripe", plans, "requests")
pricing.link_plans()

pricing.show_datasheet()