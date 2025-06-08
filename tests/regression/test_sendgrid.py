from Pricing4API.basic.bounded_rate import Rate, Quota, BoundedRate
from Pricing4API.basic.plan_and_demand import Plan
from Pricing4API.basic.pricing import Pricing

RATE_PRO = Rate(10, "1s")
RATE_ULTRA = Rate(10, "1s")
RATE_MEGA = Rate(50, "1s")

QUOTA_PRO = Quota(40000, "1month")
QUOTA_ULTRA = Quota(100000, "1month")
QUOTA_MEGA = Quota(300000, "1month")

OVERAGE_PRO = 0.001
OVERAGE_ULTRA = 0.00085
OVERAGE_MEGA = 0.0005

PLAN_PRO = Plan("Pro", BoundedRate(RATE_PRO, QUOTA_PRO), cost=9.95, overage_cost=OVERAGE_PRO, max_number_of_subscriptions=1, billing_period="1month")
PLAN_ULTRA = Plan("Ultra", BoundedRate(RATE_ULTRA, QUOTA_ULTRA), cost=79.95, overage_cost=OVERAGE_ULTRA, max_number_of_subscriptions=1, billing_period="1month")
PLAN_MEGA = Plan("Mega", BoundedRate(RATE_MEGA, QUOTA_MEGA), cost=199.95, overage_cost=OVERAGE_MEGA, max_number_of_subscriptions=1, billing_period="1month")

SENDGRID_PRICING = Pricing([PLAN_PRO, PLAN_ULTRA, PLAN_MEGA])

# ---- GROUND TRUTH ----

# RATE VALUE AT SECOND 0

def test_rate_value_at_second_0():
    assert PLAN_PRO.bounded_rate.capacity_at("0s") == PLAN_PRO.bounded_rate.rate.consumption_unit
    assert PLAN_ULTRA.bounded_rate.capacity_at("0s") == PLAN_ULTRA.bounded_rate.rate.consumption_unit
    assert PLAN_MEGA.bounded_rate.capacity_at("0s") == PLAN_MEGA.bounded_rate.rate.consumption_unit


def test_capacity_at_limits():
    assert PLAN_PRO.bounded_rate.capacity_during("1month") == PLAN_PRO.max_included_quota
    assert PLAN_ULTRA.bounded_rate.capacity_during("1month") == PLAN_ULTRA.max_included_quota
    assert PLAN_MEGA.bounded_rate.capacity_during("1month") == PLAN_MEGA.max_included_quota
    




