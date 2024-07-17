"""
This module provides the GuaranteesObject class for the SLA4OAI model.
"""

from typing import Any, Dict


class GuaranteesObject:
    """
    Represents the guarantees of an SLA.
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initializes a guarantees object.

        Args:
            data (Dict[str, Any]): Data for initializing the guarantees.

        Returns:
            None
        """
        self._guarantees: Dict[str, Any] = data

    def __repr__(self) -> str:
        """
        Returns a string representation of the GuaranteesObject.

        Returns:
            str: A string representation of the GuaranteesObject.
        """
        return f"GuaranteesObject({self._guarantees})"

    def get_guarantees(self):
        """
        Returns the guarantees of the SLA.

        Returns:
            Dict[str, Any]: The guarantees of the SLA.
        """
        return self._guarantees
