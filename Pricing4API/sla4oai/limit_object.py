"""
This module provides the LimitObject class for the SLA4OAI model.
"""

from typing import Any, Dict, List

from .cost_object import CostObject
from .period_object import PeriodObject


class LimitObject:
    """
    Represents a limit within an SLA.
    """

    def __init__(self, data: Dict[str, Dict[str, Any]]) -> None:
        """
        Initializes a limit object.

        Args:
            data (Dict[str, Dict[str, Any]]): A dictionary containing limit data.

        Returns:
            None
        """
        self._metrics: List[tuple] = [
            (key, dict(value.items()))
            for key, values in data.items()
            for value in values
        ]

        for _, value in self._metrics:
            self._max: int = value.get("max", 0)
            self._custom: bool = value.get("custom", False)
            self._period: PeriodObject = PeriodObject(value.get("period", {}))
            self._cost: CostObject = CostObject(value.get("cost", {}))

    def __repr__(self) -> str:
        """
        Returns a string representation of the LimitObject.

        The string representation includes the values of the 'max', 'custom',
        'period', and 'cost' attributes.

        Returns:
            str: A string representation of the LimitObject.
        """
        return f"""LimitObject(\n
                    max={self._max},\n
                    custom={self._custom},\n
                    period={self._period},\n
                    cost={self._cost}\n
                )"""

    def get_max(self) -> int:
        """
        Returns the maximum value of the limit.

        Returns:
            int: The maximum value of the limit.
        """
        return self._max

    def get_custom(self) -> bool:
        """
        Returns whether the limit is custom.

        Returns:
            bool: Whether the limit is custom.
        """
        return self._custom

    def get_period(self) -> PeriodObject:
        """
        Returns the period of the limit.

        Returns:
            PeriodObject: The period of the limit.
        """
        return self._period

    def get_cost(self) -> CostObject:
        """
        Returns the cost of the limit.

        Returns:
            CostObject: The cost of the limit.
        """
        return self._cost

    def get_metrics(self) -> List[tuple]:
        """
        Returns the metrics of the limit.

        Returns:
            List[tuple]: The metrics of the limit.
        """
        return self._metrics
