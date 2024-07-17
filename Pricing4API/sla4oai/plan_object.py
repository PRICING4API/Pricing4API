"""
This module provides the PlanObject class for the SLA4OAI model.
"""

from typing import Any, Dict

from .configurations_object import ConfigurationsObject
from .guarantees_object import GuaranteesObject
from .pricing_object import PricingObject
from .quotas_object import QuotasObject
from .rates_object import RatesObject


class PlanObject:
    """
    Represents a specific plan within an SLA.
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initializes a plan object.

        Args:
            data (Dict[str, Any]): Data for initializing the plan.

        Returns:
            None
        """
        self._configuration: ConfigurationsObject = ConfigurationsObject(
            data.get("configuration", {})
        )
        self._availability: str = data.get("availability", "")
        self._pricing: PricingObject = PricingObject(data.get("pricing", {}))
        self._quotas: QuotasObject = QuotasObject(data.get("quotas", {}))
        self._rates: RatesObject = RatesObject(data.get("rates", {}))
        self._guarantees: GuaranteesObject = GuaranteesObject(
            data.get("guarantees", {})
        )

    def __repr__(self) -> str:
        return f"""PlanObject(\n
                configuration={self._configuration},\n
                availability={self._availability},\n
                pricing={self._pricing},\n
                quotas={self._quotas},\n
                rates={self._rates},\n
                guarantees={self._guarantees}\n
            )"""

    def get_configuration(self) -> ConfigurationsObject:
        """
        Returns the configuration object.

        Returns:
            ConfigurationsObject: The configuration object.
        """
        return self._configuration

    def get_availability(self) -> str:
        """
        Returns the availability of the plan.

        Returns:
            str: The availability of the plan.
        """
        return self._availability

    def get_pricing(self) -> PricingObject:
        """
        Returns the pricing object.

        Returns:
            PricingObject: The pricing object.
        """
        return self._pricing

    def get_quotas(self) -> QuotasObject:
        """
        Returns the quotas object.

        Returns:
            QuotasObject: The quotas object.
        """
        return self._quotas

    def get_rates(self) -> RatesObject:
        """
        Returns the rates object.

        Returns:
            RatesObject: The rates object.
        """
        return self._rates

    def get_guarantees(self) -> GuaranteesObject:
        """
        Returns the guarantees object.

        Returns:
            GuaranteesObject: The guarantees object.
        """
        return self._guarantees
