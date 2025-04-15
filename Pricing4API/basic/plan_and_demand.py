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

    def has_enough_capacity(self, demand: 'Demand') -> bool:
        """
        Checks if the plan has enough capacity to fulfill the given demand.

        Args:
            demand (Demand): The demand to check against the plan.

        Returns:
            bool: True if the plan can fulfill the demand, False otherwise.
        """
        # Match the demand rate to the plan rate's time unit
        plan_rate = self.bounded_rate.rate
        demand_rate = demand.bounded_rate.rate

        # Convert the demand rate to match the plan rate's time unit
        adjusted_demand_rate = plan_rate.convert_to_my_time_unit(demand_rate)

        # Check if the demand's rate fits within the plan's rate
        if adjusted_demand_rate.consumption_unit > plan_rate.consumption_unit:
            print("The demand's rate is too fast for the plan.")

            # Check if the demand's quota fits within the plan's quota
            plan_quotas = self.bounded_rate.quota
            demand_quotas = demand.bounded_rate.quota

            if plan_quotas and demand_quotas:
                plan_quotas = plan_quotas if isinstance(plan_quotas, list) else [plan_quotas]
                demand_quotas = demand_quotas if isinstance(demand_quotas, list) else [demand_quotas]

                for plan_quota in plan_quotas:
                    for demand_quota in demand_quotas:
                        # Compare quota time units
                        plan_quota_ms = plan_quota.consumption_period.to_milliseconds()
                        demand_quota_ms = demand_quota.consumption_period.to_milliseconds()

                        if (
                            demand_quota.consumption_unit <= plan_quota.consumption_unit
                            and demand_quota_ms >= plan_quota_ms
                        ):
                            print(f"The demand's quota {demand_quota} fits within the plan's quota {plan_quota}. The demand could be fulfilled at a slower rate.")
                            return True

            print("The demand's total consumption exceeds the plan's quota. Cannot fulfill the demand.")
            return False
        elif adjusted_demand_rate.consumption_unit < plan_rate.consumption_unit:
            print("The demand's rate is slower than the plan's rate. The demand can be fulfilled but will operate at a slower rate.")
        else:
            print("The demand's rate matches the plan's rate.")

        # Match the largest quota time unit
        plan_quotas = self.bounded_rate.quota
        demand_quotas = demand.bounded_rate.quota

        if plan_quotas:
            # Ensure plan_quotas is a list for uniform processing
            plan_quotas = plan_quotas if isinstance(plan_quotas, list) else [plan_quotas]
            demand_quotas = demand_quotas if isinstance(demand_quotas, list) else [demand_quotas]

            for plan_quota in plan_quotas:
                for demand_quota in demand_quotas:
                    # Compare quota time units
                    plan_quota_ms = plan_quota.consumption_period.to_milliseconds()
                    demand_quota_ms = demand_quota.consumption_period.to_milliseconds()

                    if demand_quota_ms >= plan_quota_ms and demand_quota.consumption_unit <= plan_quota.consumption_unit:
                        # Demand's quota is smaller or equal and has the same or larger time unit
                        print(f"The demand's quota {demand_quota} is within the plan's quota {plan_quota}. Skipping total consumption check.")
                        continue

                    # Convert the quota period to milliseconds
                    quota_period_ms = plan_quota.consumption_period.to_milliseconds()

                    # Convert the demand rate's period to milliseconds
                    demand_rate_period_ms = demand_rate.consumption_period.to_milliseconds()

                    # Calculate the total consumption of the demand over the plan's quota period
                    demand_total_consumption = (
                        demand_rate.consumption_unit * (quota_period_ms / demand_rate_period_ms)
                    )

                    # Check if the demand's total consumption exceeds the plan's quota
                    if demand_total_consumption > plan_quota.consumption_unit:
                        print(f"The demand's total consumption ({demand_total_consumption}) exceeds the plan's quota ({plan_quota.consumption_unit}). Not possible.")
                        return False
            print("The demand's total consumption fits within the plan's quota.")

        print("The plan can fulfill the demand.")
        return True

class Demand():
    def __init__(self, rate: Rate, quota: Union[Quota, List[Quota], None] = None, N = None):
        """
        Initializes a Demand instance, acting as a constructor for BoundedRate.

        Args:
            rate (Rate): The rate object for the demand.
            quota (Union[Quota, List[Quota], None], optional): The quota(s) for the demand. Defaults to None.
        """
        if N is not None:
            self.rate = Rate(rate.consumption_unit * N, rate.consumption_period)
            self.quota = None if quota is None else (quota if isinstance(quota, list) else [quota])
            # Multiply the quota or quotas by N, keeping the same time period
            if self.quota is not None:
                self.quota = [
                    Quota(q.consumption_unit * N, q.consumption_period) for q in self.quota
                ]
        else:
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
    
    def multiply_by(self, n: int):
        """
        Multiplies the demand by a given factor, as if it were multiple users.
        
        Args:
            n (int): The factor to multiply the demand by.
            
        Returns:
            Demand: A new Demand instance with the multiplied rate and quota. (Bounded Rate)
        """
        
        if n <= 0:
            raise ValueError("The number of users must be a positive integer.")
        
        return Demand(rate=self.rate, quota=self.quota, N=n)

# Example usage
if __name__ == "__main__":

    
    
    

    # Create a BoundedRate instance for testing
    plan_limits = BoundedRate(Rate(1, "2s"), Quota(1800, "1h"))
    demand_fits = Demand(rate=Rate(100, "1min"), quota=Quota(1000, "1day"))
    # Create a Plan instance
    plan = Plan("Test Plan", plan_limits, cost=100, overage_cost=10, max_number_of_subscriptions=1, billing_period="1 month")

    # Test the consume method
    #plan.consume(demand, "2h")
    
    plan.has_enough_capacity(demand_fits)  # Should return True



