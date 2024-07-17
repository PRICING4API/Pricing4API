"""
This module provides the ContextObject class for the SLA4OAI model.
"""

from typing import Any, Dict

from .validity_object import ValidityObject


class ContextObject:
    """
    Represents the context of an SLA.
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initializes a context object.

        Args:
            data (Dict[str, Any]): Data for initializing the context.

        Returns:
            None
        """
        self._id: str = data.get("id", "")
        self._version: str = data.get("version", "")
        self._api: str = data.get("api", "")
        self._type: str = data.get("type", "")
        self._provider: str = data.get("provider", "")
        self._consumer: str = data.get("consumer", "")
        self._validity: ValidityObject = ValidityObject(data.get("validity", {}))

    def __repr__(self) -> str:
        """
        Returns a string representation of the ContextObject.

        The string representation includes the values of the id, version, api, type,
        provider, consumer, and validity attributes.

        Returns:
            str: A string representation of the ContextObject.
        """
        return f"""ContextObject(\n
                    id={self._id},\n
                    version={self._version},\n
                    api={self._api},\n
                    type={self._type},\n
                    provider={self._provider},\n
                    consumer={self._consumer},\n
                    validity={self._validity}\n
                )"""

    def get_id(self):
        """
        Returns the ID of the context.

        Returns:
            str: The ID of the context.
        """
        return self._id

    def get_version(self):
        """
        Returns the version of the context.

        Returns:
            str: The version of the context.
        """
        return self._version

    def get_api(self):
        """
        Returns the API of the context.

        Returns:
            str: The API of the context.
        """
        return self._api

    def get_type(self):
        """
        Returns the type of the context.

        Returns:
            str: The type of the context.
        """
        return self._type

    def get_provider(self):
        """
        Returns the provider of the context.

        Returns:
            str: The provider of the context.
        """
        return self._provider

    def get_consumer(self):
        """
        Returns the consumer of the context.

        Returns:
            str: The consumer of the context.
        """
        return self._consumer

    def get_validity(self):
        """
        Returns the validity of the context.

        Returns:
            ValidityObject: The validity of the context.
        """
        return self._validity
