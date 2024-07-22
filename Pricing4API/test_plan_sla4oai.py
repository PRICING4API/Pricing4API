import yaml

from .sla4oai.sla4oai import SLA4OAI
from .plan import Plan
from .pricing import Pricing
from .utils import time_unit_to_seconds


def read_amadeus_yaml(yaml_file):
    with open(yaml_file, "r", encoding="UTF-8") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


yaml_file = "Pricing4API/sla4oai-models/amadeus-sla4oai.yaml"

data = read_amadeus_yaml(yaml_file)

sla = SLA4OAI(data)
plans = []

endpoint = "/v2/shopping/hotel-offers"
method = "get"

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

amadeus_hardcoded_name = "Amadeus hardcode Test"
amadeus_hardcoded_billing = (0.0, 3600*24*30, 0.0)
amadeus_hardcoded_rate = (10, 1)
amadeus_hardcoded_quota = [(2400, 3600)]
amadeus_hardcoded_plan_test = Plan(amadeus_hardcoded_name, amadeus_hardcoded_billing, amadeus_hardcoded_rate, amadeus_hardcoded_quota)

amadeus_hardcoded_name = "Amadeus hardcode Production"
amadeus_hardcoded_billing = (0.0, 3600*24*30, 0.015)
amadeus_hardcoded_rate = (40, 1)
amadeus_hardcoded_quota = [(2400, 3600)]
amadeus_hardcoded_plan_prod = Plan(amadeus_hardcoded_name, amadeus_hardcoded_billing, amadeus_hardcoded_rate, amadeus_hardcoded_quota)

plans.append(amadeus_hardcoded_plan_test)
plans.append(amadeus_hardcoded_plan_prod)

pricing = Pricing("Amadeus", plans, "requests")
pricing.link_plans()

pricing.show_datasheet()