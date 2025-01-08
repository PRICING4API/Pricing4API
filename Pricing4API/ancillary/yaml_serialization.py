import yaml
from Pricing4API.ancillary.limit import Limit
from Pricing4API.ancillary.time_unit import TimeDuration, TimeUnit
from Pricing4API.main.new_plan import Plan
from Pricing4API.main.new_pricing import Pricing


class PricingYamlHandler:
    @staticmethod
    def parse_time_unit(unit: TimeUnit) -> str:
        """
        Converts an internal TimeUnit Enum to its YAML representation.
        """
        unit_map = {
            TimeUnit.MILLISECOND: "millisecond",
            TimeUnit.SECOND: "second",
            TimeUnit.MINUTE: "minute",
            TimeUnit.HOUR: "hour",
            TimeUnit.DAY: "day",
            TimeUnit.WEEK: "week",
            TimeUnit.MONTH: "month",
            TimeUnit.YEAR: "year",
        }
        return unit_map.get(unit, unit.value)  # Default to enum value if not in the map

    @staticmethod
    def pricing_constructor(loader, node):
        """
        YAML Constructor: Converts YAML into a Pricing instance.
        """
        fields = loader.construct_mapping(node, deep=True)
        pricing_name, pricing_data = next(iter(fields.items()))

        # Extract metrics (billing object)
        metrics = pricing_data["metrics"]["name"]

        # Extract plans
        plans = []
        for plan_name, plan_data in pricing_data["plans"].items():
            # Extract pricing
            cost = plan_data["cost"]
            billing_value = plan_data["billing_cycle"]["unit"].lower()
            billing_period = plan_data["billing_cycle"]["value"]

            try:
                billing_unit = TimeUnit[billing_value.upper()]
            except KeyError:
                raise ValueError(f"Invalid billing unit: {billing_value}. Expected one of {[e.value for e in TimeUnit]}")

            # Extract unitary_rate (handle missing case)
            unitary_rate_field = plan_data.get("unitary_rate", {}).get("/*", {}).get("all", {}).get("requests", {}).get("period", None)
            if unitary_rate_field:
                unitary_rate = Limit(1, TimeDuration(unitary_rate_field["value"], TimeUnit[unitary_rate_field["unit"].upper()]))
            else:
                unitary_rate = None  # Or a default value, e.g., Limit(0, TimeDuration(0, TimeUnit.SECOND))

            # Extract quotas
            quotas = [
                Limit(
                    quota["max"],
                    TimeDuration(quota["period"]["value"], TimeUnit[quota["period"]["unit"].upper()])
                )
                for quota in plan_data["quotas"]["/*"]["all"]["requests"]
            ]

            # Extract overage
            overage = plan_data.get("overage", {})
            overage_cost = overage.get("cost", None)

            # Extract max_number_of_subscriptions
            max_number_of_subscriptions = plan_data.get("max_number_of_subscriptions", 1)

            # Create Plan instance
            plan = Plan(
                name=plan_name,
                billing=(cost, TimeDuration(billing_period, billing_unit)),
                overage_cost=overage_cost,
                unitary_rate=unitary_rate,
                quotes=quotas,
                max_number_of_subscriptions=max_number_of_subscriptions,
            )
            plans.append(plan)

        # Create Pricing instance
        return Pricing(name=pricing_name, plans=plans, billing_object=metrics)


    @staticmethod
    def pricing_representer(dumper, data):
        """
        YAML Representer: Converts a Pricing instance into YAML.
        """
        def plan_to_yaml(plan):
            """
            Helper to convert a Plan instance into a dictionary representation for YAML.
            """
            return {
                "cost": plan.price,
                "billing_cycle": {
                    "value": plan.billing_unit.value,
                    "unit": PricingYamlHandler.parse_time_unit(plan.billing_unit.unit),
                },
                "unitary_rate": {
                    "/*": {
                        "all": {
                            "requests": {
                                "period": {
                                    "value": plan.limits[0].duration.value,
                                    "unit": PricingYamlHandler.parse_time_unit(plan.limits[0].duration.unit),
                                }
                            }
                        }
                    }
                },
                "quotas": {
                    "/*": {
                        "all": {
                            "requests": [
                                {
                                    "max": limit.value,
                                    "period": {
                                        "value": limit.duration.value,
                                        "unit": PricingYamlHandler.parse_time_unit(limit.duration.unit),
                                    }
                                } for limit in plan.limits[1:]
                            ]
                        }
                    }
                },
                "overage": {
                    "cost": plan.overage_cost,
                },
                "max_number_of_subscriptions": plan.max_number_of_subscriptions,
            }

        return dumper.represent_mapping("!Pricing", {
            data.name: {
                "metrics": {
                    "name": data.billing_object,
                },
                "plans": {
                    plan.name: plan_to_yaml(plan) for plan in data.plans
                },
            }
        })

    @staticmethod
    def load():
        """
        Registers the custom YAML constructor and representer for the Pricing class.
        """
        yaml.add_constructor("!Pricing", PricingYamlHandler.pricing_constructor, Loader=yaml.SafeLoader)
        yaml.add_representer(Pricing, PricingYamlHandler.pricing_representer, Dumper=yaml.SafeDumper)
