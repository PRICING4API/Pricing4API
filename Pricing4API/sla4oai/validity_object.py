"""
This module provides the ValidityObject class for the SLA4OAI model.
"""

from typing import Any, Dict


class ValidityObject:
    """
    Represents the validity period of an SLA.
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initializes a validity object.

        Args:
            data (Dict[str, Any]): Data for initializing the validity.

        Returns:
            None
        """
        self._effective_date: str = data.get("effectiveDate", "")
        self._expiration_date: str = data.get("expirationDate", "")

    def __repr__(self) -> str:
        return f"""ValidityObject(\n
                effective_date={self._effective_date},\n
                expiration_date={self._expiration_date}\n
            )"""

    def get_effective_date(self) -> str:
        """
        Returns the effective date of the validity.

        Returns:
            str: The effective date of the validity.
        """
        return self._effective_date

    def get_expiration_date(self) -> str:
        """
        Returns the expiration date of the validity.

        Returns:
            str: The expiration date of the validity.
        """
        return self._expiration_date
