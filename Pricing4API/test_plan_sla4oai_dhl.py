import yaml

from .sla4oai.sla4oai import SLA4OAI
from .plan import Plan
from .pricing import Pricing
from .utils import time_unit_to_seconds


def read_dhl_yaml(yaml_file):
    with open(yaml_file, "r", encoding="UTF-8") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


yaml_file = "Pricing4API/sla4oai-models/dhl_locationFinderUnified_sla4oai.yaml"

data = read_dhl_yaml(yaml_file)

sla = SLA4OAI(data)
plans = []

endpoint = "/*"
method = "all"

plans_name = sla.get_plans().get_names_of_plans()

for plan_name in plans_name:

    billing = sla.get_billing(endpoint, method, plan_name)

    rate_test = None

    request_rate_test = (
        sla.get_plans()
        .get_plan_by_name(plan_name)
        .get_rates()
        .get_limit_by_method("/*", "all")[0]
        .get_max()
    )

    time_rate_test = time_unit_to_seconds(
        sla.get_plans()
        .get_plan_by_name(plan_name)
        .get_rates()
        .get_limit_by_method("/*", "all")[0]
        .get_period()
        .get_unit()
    )

    rate_test = (request_rate_test, time_rate_test)

    quotas_test = [(sla.get_plans().get_plan_by_name(plan_name).get_quotas().get_max_by_path_and_method(endpoint, method), time_unit_to_seconds(sla.get_plans().get_plan_by_name(plan_name).get_quotas().get_period_by_path_and_method(endpoint, method).get_unit()))]

    plan_test = Plan(plan_name, billing, rate_test, quotas_test)
    plans.append(plan_test)

dhl_hardcoded_name = "dhl hardcode Free"
dhl_hardcoded_billing = (0.0, 3600*24*30, 0.0)
dhl_hardcoded_rate = (500, 3600*24)
dhl_hardcoded_quota = [(500, 3600*24)]
dhl_hardcoded_plan_test = Plan(dhl_hardcoded_name, dhl_hardcoded_billing, dhl_hardcoded_rate, dhl_hardcoded_quota)

plans.append(dhl_hardcoded_plan_test)

pricing = Pricing("dhl", plans, "requests")
pricing.link_plans()

pricing.show_datasheet()

pricing_test_1 = Pricing("dhl", [dhl_hardcoded_plan_test], "requests")
pricing_test_2 = Pricing("dhl", [plans[0]], "requests")

pricing_test_1.compareTo(pricing_test_2)