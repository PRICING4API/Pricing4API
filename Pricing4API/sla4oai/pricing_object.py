"""
This module provides the PricingObject class for the SLA4OAI model.
"""

from typing import Any, Dict


class PricingObject:
    """
    Represents the pricing information of an SLA.
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initializes a pricing object.

        Args:
            data (Dict[str, Any]): Data for initializing the pricing.

        Returns:
            None
        """
        self._cost: float = data.get("cost", 0.0)
        self._custom: bool = data.get("custom", False)
        self._currency: str = data.get("currency", "USD")
        self._billing: str = data.get("billing", "monthly")

    def __repr__(self) -> str:
        return f"""PricingObject(\n
                cost={self._cost},\n
                custom={self._custom},\n
                currency={self._currency},\n
                billing={self._billing}\n
            )"""

    def get_cost(self) -> float:
        """
        Returns the cost of the pricing.

        Returns:
            float: The cost of the pricing.
        """
        return self._cost

    def is_custom(self) -> bool:
        """
        Returns whether the pricing is custom or not.

        Returns:
            bool: True if the pricing is custom, False otherwise.
        """
        return self._custom

    def get_currency(self) -> str:
        """
        Returns the currency of the pricing.

        Returns:
            str: The currency of the pricing.
        """
        return self._currency

    def get_billing(self) -> str:
        """
        Returns the billing period of the pricing.

        Returns:
            str: The billing period of the pricing.
        """
        return self._billing
