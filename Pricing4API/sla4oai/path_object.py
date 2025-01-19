"""
This module provides the PathObject class for the SLA4OAI model.
"""

from typing import Any, Dict

from .operation_object import OperationObject


class PathObject:
    """
    Represents a path within an SLA.
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initializes a path object.

        Args:
            data (Dict[str, Any]): Data for initializing the path.

        Returns:
            None
        """
        self._operations: Dict[str, OperationObject] = {
            key: OperationObject({key: data.get(key, {})}) for key in data.keys()
        }

    def __repr__(self) -> str:
        return f"PathObject({self._operations})"

    def get_operations(self) -> Dict[str, OperationObject]:
        """
        Returns the operations of the path.

        Returns:
            Dict[str, OperationObject]: The operations of the path.
        """
        return self._operations
