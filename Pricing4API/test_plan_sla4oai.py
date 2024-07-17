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


yaml_file = "Pricing4API/amadeus.yaml"

data = read_amadeus_yaml(yaml_file)

sla = SLA4OAI(data)
plans = []

billing = sla.get_billing()

plans_name = sla.get_plans().get_names_of_plans()

urls_rate_test = sla.get_plans().get_plan_by_name(plans_name[0]).get_rates().get_paths()

method_rate_test = (
    sla.get_plans()
    .get_plan_by_name(plans_name[0])
    .get_rates()
    .get_methods_by_path(urls_rate_test[0])
)

request_rate_test = (
    sla.get_plans()
    .get_plan_by_name(plans_name[0])
    .get_rates()
    .get_limit_by_method(urls_rate_test[0], method_rate_test[0])[0]
    .get_max()
)

time_rate_test = time_unit_to_seconds(
    sla.get_plans()
    .get_plan_by_name(plans_name[0])
    .get_rates()
    .get_limit_by_method(urls_rate_test[0], method_rate_test[0])[0]
    .get_period()
    .get_unit()
)

rate_test = (request_rate_test, time_rate_test)

urls_quotas_test = (
    sla.get_plans().get_plan_by_name(plans_name[0]).get_quotas().get_paths()
)

quotas_test = [
    (
        sla.get_plans()
        .get_plan_by_name(plans_name[0])
        .get_quotas()
        .get_max_by_path_and_method(url, method),
        time_unit_to_seconds(
            sla.get_plans()
            .get_plan_by_name(plans_name[0])
            .get_quotas()
            .get_period_by_path_and_method(url, method)
        ),
    )
    for url in urls_quotas_test
    for method in sla.get_plans()
    .get_plan_by_name(plans_name[0])
    .get_quotas()
    .get_methods_by_path(url)
]

plan_test = Plan(f"Amadeus-{plans_name[0]}", billing, rate_test, quotas_test)

urls_rate_production = (
    sla.get_plans().get_plan_by_name(plans_name[1]).get_rates().get_paths()
)

method_rate_production = (
    sla.get_plans()
    .get_plan_by_name(plans_name[1])
    .get_rates()
    .get_methods_by_path(urls_rate_production[0])
)

request_rate_production = (
    sla.get_plans()
    .get_plan_by_name(plans_name[1])
    .get_rates()
    .get_limit_by_method(urls_rate_production[0], method_rate_production[0])[0]
    .get_max()
)

time_rate_production = time_unit_to_seconds(
    sla.get_plans()
    .get_plan_by_name(plans_name[1])
    .get_rates()
    .get_limit_by_method(urls_rate_production[0], method_rate_production[0])[0]
    .get_period()
    .get_unit()
)

rate_production = (request_rate_production, time_rate_production)

urls_quotas_production = (
    sla.get_plans().get_plan_by_name(plans_name[1]).get_quotas().get_paths()
)

quotas_production = [
    (
        sla.get_plans()
        .get_plan_by_name(plans_name[1])
        .get_quotas()
        .get_max_by_path_and_method(url, method),
        time_unit_to_seconds(
            sla.get_plans()
            .get_plan_by_name(plans_name[1])
            .get_quotas()
            .get_period_by_path_and_method(url, method)
            .get_unit()
        ),
    )
    for url in urls_quotas_production
    for method in sla.get_plans()
    .get_plan_by_name(plans_name[1])
    .get_quotas()
    .get_methods_by_path(url)
]

plan_production = Plan(
    f"Amadeus-{plans_name[1]}", billing, rate_production, quotas_production
)

plans.append(plan_test)
plans.append(plan_production)

pricing = Pricing("Amadeus", plans, "requests")
pricing.link_plans()

pricing.show_datasheet()
