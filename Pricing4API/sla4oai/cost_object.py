"""
This module provides the CostObject class for the SLA4OAI model.
"""

from typing import Any, Dict

from .overage_object import OverageObject


class CostObject:
    """
    Represents cost information within an SLA.
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initializes a cost object.

        Args:
            data (Dict[str, Any]): Data for initializing the cost.

        Returns:
            None
        """
        self._overage: OverageObject = OverageObject(data.get("overage", {}))

    def __repr__(self) -> str:
        """
        Returns a string representation of the CostObject.

        The string representation includes the overage value of the CostObject.

        Returns:
            str: A string representation of the CostObject.
        """
        return f"CostObject({self._overage})"

    def get_overage(self):
        """
        Returns the overage of the cost.

        Returns:
            OverageObject: The overage of the cost.
        """
        return self._overage
