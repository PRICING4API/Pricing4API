"""
This module provides the RatesObject class for the SLA4OAI model.
"""

from typing import Any, Dict, List

from .path_object import PathObject
from .limit_object import LimitObject


class RatesObject:
    """
    Represents the rates of an SLA.
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initializes a rates object.

        Args:
            data (Dict[str, Any]): Data for initializing the rates.

        Returns:
            None
        """
        self._paths: Dict[str, PathObject] = {
            key: PathObject(data.get(key, {})) for key in data.keys()
        }

    def __repr__(self) -> str:
        return f"RatesObject({self._paths})"

    def get_paths(self) -> List[str]:
        """
        Returns a list of all the paths in the rates object.

        Returns:
            List[str]: A list of all the paths in the rates object.
        """
        return list(self._paths.keys())

    def get_methods_by_path(self, path: str) -> List[str]:
        """
        Returns a list of methods available for a given path.

        Args:
            path (str): The path for which to retrieve the methods.

        Returns:
            List[str]: A list of methods available for the given path.
        """
        return list(self._paths.get(path, {}).get_operations().keys())

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
