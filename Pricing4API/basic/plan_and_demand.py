

from typing import List, Union
from Pricing4API.ancillary.time_unit import TimeDuration, TimeUnit
from Pricing4API.basic.bounded_rate import BoundedRate, Rate, Quota
from Pricing4API.utils import parse_time_string_to_duration
from Pricing4API.basic.compare_curves import compare_bounded_rates_capacity


class Plan():
    def __init__(self, name, bounded_rate: BoundedRate, cost, overage_cost, max_number_of_subscriptions, billing_period):
        self.name = name
        self.bounded_rate = bounded_rate
        self.cost = cost
        self.overage_cost = overage_cost
        self.max_number_of_subscriptions = max_number_of_subscriptions
        self.billing_period = billing_period

    def show_capacity(self, time_interval: Union[str, TimeDuration]):
        if isinstance(time_interval, str):
            time_interval = parse_time_string_to_duration(time_interval)
        
        return self.bounded_rate.show_capacity(time_interval)

    def consume(self, demand: 'Demand', time_interval: Union[str, TimeDuration]):
        """
        Consumes demand over a specified time interval, comparing bounded rates.

        Args:
            demand (Demand): The demand to consume.
            time_interval (Union[str, TimeDuration]): The time interval for consumption.
        """
        if isinstance(time_interval, str):
            time_interval = parse_time_string_to_duration(time_interval)

        # Compare the bounded rates of the plan and the demand
        compare_bounded_rates_capacity(
            bounded_rates=[self.bounded_rate, demand.bounded_rate],
            time_interval=time_interval
        )

class Demand():
    def __init__(self, rate: Rate, quota: Union[Quota, List[Quota], None] = None):
        """
        Initializes a Demand instance, acting as a constructor for BoundedRate.

        Args:
            rate (Rate): The rate object for the demand.
            quota (Union[Quota, List[Quota], None], optional): The quota(s) for the demand. Defaults to None.
        """
        self.rate = rate
        self.quota = None if quota is None else (quota if isinstance(quota, list) else [quota])
        self.bounded_rate = BoundedRate(self.rate) if self.quota is None else BoundedRate(self.rate, self.quota)

    def show_capacity(self, time_interval: Union[str, TimeDuration]):
        """
        Shows the capacity curve for the demand.

        Args:
            time_interval (Union[str, TimeDuration]): The time interval for the capacity curve.
        """
        if isinstance(time_interval, str):
            time_interval = parse_time_string_to_duration(time_interval)

        return self.bounded_rate.show_capacity(time_interval)

# Example usage
if __name__ == "__main__":
    # Create a Rate instance
    rate = Rate(1, "5s")
    quota = [Quota(100, "1h"), Quota(200, "2h")]

    # Create a Demand instance
    demand = Demand(rate=rate, quota=quota)

    # Create a BoundedRate instance for testing
    plan_limits = BoundedRate(Rate(10, "1s"), Quota(900, "1h"))

    # Create a Plan instance
    plan = Plan("Test Plan", plan_limits, cost=100, overage_cost=10, max_number_of_subscriptions=1, billing_period="1 month")

    # Test the consume method
    plan.consume(demand, "2h")
            
        