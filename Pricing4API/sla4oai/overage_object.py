"""
This module provides the OverageObject class for the SLA4OAI model.
"""

from typing import Any, Dict


class OverageObject:
    """
    Represents overage information within an SLA.
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initializes an overage object.

        Args:
            data (Dict[str, Any]): Data for initializing the overage.

        Returns:
            None
        """
        self._overage: int = data.get("excess", 0)
        self._cost: float = data.get("cost", 0.0)

    def __repr__(self) -> str:
        return f"OverageObject({self._overage}, {self._cost})"

    def get_overage(self) -> int:
        """
        Returns the overage value.

        Returns:
            int: The overage value.
        """
        return self._overage

    def get_cost(self) -> float:
        """
        Returns the cost of the overage.

        Returns:
            float: The cost of the overage.
        """
        return self._cost
