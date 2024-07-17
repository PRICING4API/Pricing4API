"""
This module provides the PeriodObject class for the SLA4OAI model.
"""

from typing import Any, Dict


class PeriodObject:
    """
    Represents a period within an SLA.
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initializes a period object.

        Args:
            data (Dict[str, Any]): Data for initializing the period.

        Returns:
            None
        """
        self._amount: int = data.get("amount", 0)
        self._unit: str = data.get("unit", "")

    def __repr__(self) -> str:
        return f"PeriodObject({self._amount}, {self._unit})"

    def get_amount(self) -> int:
        """
        Returns the amount of the period.

        Returns:
            int: The amount of the period.
        """
        return self._amount

    def get_unit(self) -> str:
        """
        Returns the unit of the period.

        Returns:
            str: The unit of the period.
        """
        return self._unit
