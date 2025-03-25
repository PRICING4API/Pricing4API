import yaml
from Pricing4API.main.plan import Plan
from Pricing4API.ancillary.limit import Limit
from Pricing4API.ancillary.time_unit import TimeDuration, TimeUnit

def load_plan(yaml_string: str) -> Plan:
    """
    Convierte un DSL en YAML a un objeto Plan de Pricing4API.
    
    Args:
        yaml_string (str): YAML en formato string.

    Returns:
        Plan: Objeto de Pricing4API representando las cuotas y rate unitario (si existe).
    """
    data = yaml.safe_load(yaml_string)

    api_name = data.get("name", "Unnamed API")
    limits_section = data.get("limits", {})
    
    unitary_rate_section = limits_section.get("unitary_rate")
    quotas_section = limits_section.get("quotas", {})

    unitary_rate = None
    quotas = []

    # Procesar el unitary_rate si existe
    if unitary_rate_section:
        period = unitary_rate_section.get("period", {})
        period_value = period.get("value")
        period_unit = period.get("unit")

        if not (period_value and period_unit):
            raise ValueError("Faltan valores en el unitary_rate.")

        time_duration = TimeDuration(int(period_value), TimeUnit[period_unit.upper()])
        unitary_rate = Limit(1, time_duration)  # Siempre es 1 porque es un rate unitario explícito.

    # Procesar las quotas
    for endpoint, methods in quotas_section.items():
        for method, limits in methods.items():
            for limit in limits:
                max_requests = limit.get("max")
                period = limit.get("period", {})
                period_value = period.get("value")
                period_unit = period.get("unit")

                if not (max_requests and period_value and period_unit):
                    raise ValueError(f"Faltan valores en la cuota definida para {endpoint} {method}")

                time_duration = TimeDuration(int(period_value), TimeUnit[period_unit.upper()])
                quotas.append(Limit(max_requests, time_duration))

    # Crear objeto Plan
    plan = Plan(
        name=api_name,
        billing=(0.0, TimeDuration(1, TimeUnit.MONTH)),  # Mockeado, ya que no lo necesitan
        unitary_rate=unitary_rate,
        quotes=quotas
    )

    return plan

def load_plan_simple(yaml_string: str) -> Plan:
    """
    Carga un plan simplificado desde un YAML plano sin rutas ni métodos HTTP.
    
    Args:
        yaml_string (str): Definición en YAML con claves directas: 'unitary_rate' o 'quotas' bajo 'limits'.
    
    Returns:
        Plan: Objeto Plan de Pricing4API.
    """
    data = yaml.safe_load(yaml_string)

    api_name = data.get("name", "Unnamed API")
    limits_section = data.get("limits", {})

    unitary_rate = None
    quotas = []

    # Procesar unitary_rate si existe
    if "unitary_rate" in limits_section:
        period = limits_section["unitary_rate"].get("period", {})
        period_value = period.get("value")
        period_unit = period.get("unit")

        if not (period_value and period_unit):
            raise ValueError("Faltan valores en 'unitary_rate'.")

        duration = TimeDuration(int(period_value), TimeUnit[period_unit.upper()])
        unitary_rate = Limit(1, duration)

    # Procesar quotas si existen
    if "quotas" in limits_section:
        for limit in limits_section["quotas"]:
            max_requests = limit.get("max")
            period = limit.get("period", {})
            period_value = period.get("value")
            period_unit = period.get("unit")

            if not (max_requests and period_value and period_unit):
                raise ValueError("Faltan valores en una cuota.")

            duration = TimeDuration(int(period_value), TimeUnit[period_unit.upper()])
            quotas.append(Limit(max_requests, duration))

    plan = Plan(
        name=api_name,
        billing=(0.0, TimeDuration(1, TimeUnit.MONTH)),  # Mockeado
        unitary_rate=unitary_rate,
        quotes=quotas
    )

    return plan

