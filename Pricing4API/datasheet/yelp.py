from ..plan import Plan
from ..pricing import Pricing

plans = []

name = "Yelp hardcode Free Starter"
billing = (0.0, 3600*24*30, 0.0)
rate = (300, 3600*24)
quota = [(300, 3600*24)]
plan_test = Plan(name, billing, rate, quota)

name = "Yelp hardcode Starter"
billing = (7.99, 3600*24*30, 0.0)
rate = (1000, 3600*24)
quota = [(1000, 3600*24)]
plan_stater = Plan(name, billing, rate, quota)

name = "Yelp hardcode Plus"
billing = (9.99, 3600*24*30, 0.0)
quota = [(1000, 3600*24)]
rate = (1000, 3600*24)
plan_plus = Plan(name, billing, rate, quota)

name = "Yelp hardcode Free Plus"
billing = (0.0, 3600*24*30, 0.0)
quota = [(500, 3600*24)]
rate = (500, 3600*24)
plan_plus_free = Plan(name, billing, rate, quota)

name = "Yelp hardcode Enterprise"
billing = (14.99, 3600*24*30, 0.0)
rate = (1000, 3600*24)
quota = [(1000, 3600*24)]
plan_enterprise = Plan(name, billing, rate, quota)

name = "Yelp hardcode Free Enterprise"
billing = (0.0, 3600*24*30, 0.0)
quota = [(500, 3600*24)]
rate = (500, 3600*24)
plan_enterprise_free = Plan(name, billing, rate, quota)




plans.append(plan_test)
plans.append(plan_stater)
plans.append(plan_plus)
plans.append(plan_plus_free)
plans.append(plan_enterprise)
plans.append(plan_enterprise_free)

pricing = Pricing("Yelp", plans, "requests")
pricing.link_plans()

pricing.show_datasheet()