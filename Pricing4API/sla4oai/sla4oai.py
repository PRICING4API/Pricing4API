"""
This module provides the SLA (Service Level Agreement) model for OAI (OpenAPI Initiative).
"""

from typing import Any, Dict

from .configurations_object import ConfigurationsObject
from .context_object import ContextObject
from .guarantees_object import GuaranteesObject
from .infrastructure_object import InfrastructureObject
from .metrics_object import MetricsObject
from .plans_object import PlansObject
from .pricing_object import PricingObject
from .quotas_object import QuotasObject
from .rates_object import RatesObject
from ..utils import time_unit_to_seconds


class SLA4OAI:
    """
    Represents an SLA (Service Level Agreement) for OpenAPI.
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initializes an SLA object.

        Args:
            data (Dict[str, Any]): Data for initializing the SLA.

        Returns:
            None
        """
        self._context: ContextObject = ContextObject(data.get("context", {}))
        self._infrastructure: InfrastructureObject = InfrastructureObject(
            data.get("infrastructure", {})
        )
        self._pricing: PricingObject = PricingObject(data.get("pricing", {}))
        self._metrics: MetricsObject = MetricsObject(data.get("metrics", {}))
        self._plans: PlansObject = PlansObject(data.get("plans", {}))
        self._quotas: QuotasObject = QuotasObject(data.get("quotas", {}))
        self._rates: RatesObject = RatesObject(data.get("rates", {}))
        self._guarantees: GuaranteesObject = GuaranteesObject(
            data.get("guarantees", {})
        )
        self._configuration: ConfigurationsObject = ConfigurationsObject(
            data.get("configuration", {})
        )

    def __repr__(self) -> str:
        """
        Returns a string representation of the object.

        Returns:
            str: String representation of the object.
        """
        return f"""SLA4OAI(\n
                context={self._context},\n
                infrastructure={self._infrastructure},\n
                pricing={self._pricing},\n
                metrics={self._metrics},\n
                plans={self._plans},\n
                quotas={self._quotas},\n
                rates={self._rates},\n
                guarantees={self._guarantees},\n
                configuration={self._configuration}\n
            )"""

    def get_context(self):
        """
        Returns the context of the SLA.

        Returns:
            ContextObject: The context of the SLA.
        """
        return self._context

    def get_infrastructure(self):
        """
        Returns the infrastructure of the SLA.

        Returns:
            InfrastructureObject: The infrastructure of the SLA.
        """
        return self._infrastructure

    def get_pricing(self):
        """
        Returns the pricing of the SLA.

        Returns:
            PricingObject: The pricing of the SLA.
        """
        return self._pricing

    def get_metrics(self):
        """
        Returns the metrics of the SLA.

        Returns:
            MetricsObject: The metrics of the SLA.
        """
        return self._metrics

    def get_plans(self):
        """
        Returns the plans of the SLA.

        Returns:
            PlansObject: The plans of the SLA.
        """
        return self._plans

    def get_quotas(self):
        """
        Returns the quotas of the SLA.

        Returns:
            QuotasObject: The quotas of the SLA.
        """
        return self._quotas

    def get_rates(self):
        """
        Returns the rates of the SLA.

        Returns:
            RatesObject: The rates of the SLA.
        """
        return self._rates

    def get_guarantees(self):
        """
        Returns the guarantees of the SLA.

        Returns:
            GuaranteesObject: The guarantees of the SLA.
        """
        return self._guarantees

    def get_configuration(self):
        """
        Returns the configuration of the SLA.

        Returns:
            ConfigurationsObject: The configuration of the SLA.
        """
        return self._configuration

    def get_billing(self, endpoint: str | None = None, method: str | None = None, plan_name: str | None = None):
        """
        Returns the billing of the SLA to Plan.

        Returns:
            Tuple[float, int, Optional[float]]: The billing of the SLA.
        """
        cost = self.get_pricing().get_cost()
        time = time_unit_to_seconds(self.get_pricing().get_billing())
        overage_cost = self.get_plans().get_plan_by_name(plan_name).get_quotas().get_limit_by_method(endpoint, method)[0].get_cost().get_overage().get_cost() if endpoint and method and plan_name else 0

        return (cost, time, overage_cost)

    def get_rate(self):
        """
        Returns the rate of the SLA.

        Returns:
            float: The rate of the SLA.
        """
        return self.get_rates()
