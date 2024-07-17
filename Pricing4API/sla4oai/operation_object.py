"""
This module provides the OperationObject class for the SLA4OAI model.
"""

from typing import Any, Dict, List

from .limit_object import LimitObject


class OperationObject:
    """
    Represents an operation within an SLA.
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initializes an operation object.

        Args:
            data (Dict[str, Any]): Data for initializing the operation.

        Returns:
            None
        """
        self._limits: List[LimitObject] = [
            LimitObject(values) for values in data.values()
        ]

    def __repr__(self) -> str:
        return f"OperationObject({self._limits})"

    def get_limits(self) -> List[LimitObject]:
        """
        Returns the limits of the operation.

        Returns:
            List[LimitObject]: The limits of the operation.
        """
        return self._limits
