"""
This module provides the PlansObject class for the SLA4OAI model.
"""

from typing import Any, Dict, List

from .plan_object import PlanObject
from .pricing_object import PricingObject


class PlansObject:
    """
    Represents the plans of an SLA.
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initializes a plans object.

        Args:
            data (Dict[str, Any]): Data for initializing the plans.

        Returns:
            None
        """
        self._plan: Dict[str, PlanObject] = {
            plan_name: PlanObject(plan_data) for plan_name, plan_data in data.items()
        }

    def __repr__(self) -> str:
        return f"PlansObject({self._plan})"

    def get_plans(self) -> Dict[str, PlanObject]:
        """
        Returns the plans.

        Returns:
            Dict[str, PlanObject]: The plans.
        """
        return self._plan

    def get_plan_by_name(self, plan_name: str) -> PlanObject:
        """
        Returns a plan by its name.

        Args:
            plan_name (str): The name of the plan.

        Returns:
            PlanObject: The plan.
        """
        return self._plan[plan_name]

    def get_names_of_plans(self) -> List[str]:
        """
        Returns the names of the plans.

        Returns:
            List[str]: The names of the plans.
        """
        return list(self._plan.keys())

    def get_pricing_by_plan(self, plan_name: str) -> PricingObject:
        """
        Returns the pricing of a plan.

        Args:
            plan_name (str): The name of the plan.

        Returns:
            PricingObject: The pricing of the plan.
        """
        return self._plan[plan_name].get_pricing()
