

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
        
    def __str__(self):
        return f"Demand(rate={self.rate}, quota={self.quota})"

    def show_capacity(self, time_interval: Union[str, TimeDuration]):
        """
        Shows the capacity curve for the demand.

        Args:
            time_interval (Union[str, TimeDuration]): The time interval for the capacity curve.
        """
        if isinstance(time_interval, str):
            time_interval = parse_time_string_to_duration(time_interval)

        return self.bounded_rate.show_capacity(time_interval)
    
    def multiply_by(self, n:int):
        """
        Multiplies the demand by a given factor, as if it were multiple users.
        
        Args:
            n (int): The factor to multiply the demand by.
            
        Returns:
            Demand: A new Demand instance with the multiplied rate and quota. (Bounded Rate)
        """
        
        if n <= 0:
            raise ValueError("The number of users must be a positive integer.")
        
        if self.quota is None:
            return Demand(Rate(self.rate.consumption_unit * n, self.rate.consumption_period), None)
        
        else:
            new_rate = Rate(self.rate.consumption_unit * n, self.rate.consumption_period)
            new_quota = [Quota(q.consumption_unit * n, q.consumption_period) for q in self.quota]
            
            return Demand(new_rate, new_quota)

# Example usage
if __name__ == "__main__":
    # Create a Rate instance
    rate = Rate(1, "5s")
    quota = Quota(200, "2h")

    # Create a Demand instance
    demand = Demand(rate=rate, quota=quota)
    
    new_demand = demand.multiply_by(3)
    print(new_demand)  # Output: Demand(rate=Rate(value=3, time_unit='5s'), quota=[Quota(value=600, time_unit='2h')])
    
    
    

    # Create a BoundedRate instance for testing
    plan_limits = BoundedRate(Rate(10, "1s"), Quota(900, "1h"))

    # Create a Plan instance
    plan = Plan("Test Plan", plan_limits, cost=100, overage_cost=10, max_number_of_subscriptions=1, billing_period="1 month")

    # Test the consume method
    #plan.consume(demand, "2h")
            
        