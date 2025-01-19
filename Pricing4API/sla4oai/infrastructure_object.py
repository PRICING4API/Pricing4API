"""
This module provides the InfrastructureObject class for the SLA4OAI model.
"""

from typing import Any, Dict


class InfrastructureObject:
    """
    Represents the infrastructure of an SLA.
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initializes an infrastructure object.

        Args:
            data (Dict[str, Any]): Data for initializing the infrastructure.

        Returns:
            None
        """
        self._supervisor: str = data.get("supervisor", "")
        self._monitor: str = data.get("monitor", "")

    def __repr__(self) -> str:
        """
        Returns a string representation of the InfrastructureObject.

        The returned string includes the values of the supervisor and monitor attributes.

        Returns:
            str: A string representation of the InfrastructureObject.
        """
        return f"""InfrastructureObject(\n
                    supervisor={self._supervisor},\n
                    monitor={self._monitor}\n
                )"""

    def get_supervisor(self) -> str:
        """
        Returns the supervisor of the infrastructure.

        Returns:
            str: The supervisor of the infrastructure.
        """
        return self._supervisor

    def get_monitor(self) -> str:
        """
        Returns the monitor of the infrastructure.

        Returns:
            str: The monitor of the infrastructure.
        """
        return self._monitor
