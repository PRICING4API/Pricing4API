"""
This module provides the ConfigurationsObject class for the SLA4OAI model.
"""

from typing import Any, Dict


class ConfigurationsObject:
    """
    Represents the configurations of an SLA.
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initializes a configurations object.

        Args:
            data (Dict[str, Any]): Data for initializing the configurations.

        Returns:
            None
        """
        self._configurations: Dict[str, Any] = data

    def __repr__(self) -> str:
        """
        Returns a string representation of the ConfigurationsObject.

        Returns:
            str: A string representation of the ConfigurationsObject.
        """
        return f"ConfigurationsObject({self._configurations})"

    def get_configurations(self) -> Dict[str, Any]:
        """
        Returns the configurations of the SLA.

        Returns:
            Dict[str, Any]: The configurations of the SLA.
        """
        return self._configurations
