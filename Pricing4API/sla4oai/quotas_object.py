"""
This module provides the QuotasObject class for the SLA4OAI model.
"""

from typing import Any, Dict, List

from .path_object import PathObject
from .limit_object import LimitObject


class QuotasObject:
    """
    Represents the quotas of an SLA.
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initializes a quotas object.

        Args:
            data (Dict[str, Any]): Data for initializing the quotas.

        Returns:
            None
        """
        self._paths: Dict[str, PathObject] = {
            key: PathObject(data.get(key, {})) for key in data.keys()
        }

    def __repr__(self) -> str:
        return f"QuotasObject({self._paths})"

    def get_paths(self) -> List[str]:
        """
        Returns the paths.

        Returns:
            List[str]: The paths.
        """
        return list(self._paths.keys())

    def get_methods_by_path(self, path: str) -> List[str]:
        """
        Returns the methods by path.

        Args:
            path (str): The path.

        Returns:
            List[str]: The methods.
        """
        return list(self._paths.get(path, {}).get_operations().keys())

    def get_max_by_path_and_method(self, path: str, method: str) -> int:
        """
        Returns the max for a given method on a given path.

        Args:
            path (str): The path.
            method (str): The method.

        Returns:
            int: The max for the given method on the given path.
        """
        return (
            self._paths.get(path, {})
            .get_operations()
            .get(method, {})
            .get_limits()[0]
            .get_max()
        )

    def get_period_by_path_and_method(self, path: str, method: str) -> str:
        """
        Returns the period for a given method on a given path.

        Args:
            path (str): The path.
            method (str): The method.

        Returns:
            str: The period for the given method on the given path.
        """
        return (
            self._paths.get(path, {})
            .get_operations()
            .get(method, {})
            .get_limits()[0]
            .get_period()
        )

    def get_limit_by_method(self, path: str, method: str) -> List[LimitObject]:
        """
        Returns the limit for a given method on a given path.

        Args:
            path (str): The path.
            method (str): The method.

        Returns:
            List[LimitObject]: The limit for the given method on the given path.
        """
        return self._paths.get(path, {}).get_operations().get(method, {}).get_limits()
