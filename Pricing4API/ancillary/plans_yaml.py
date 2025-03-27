import yaml
from Pricing4API.main.plan import Plan
from Pricing4API.ancillary.limit import Limit
from Pricing4API.ancillary.time_unit import TimeDuration, TimeUnit
from Pricing4API.utils import parse_time_string_to_duration

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

def load_plan_from_variables(**kwargs) -> Plan:
    """
    Crea un objeto Plan a partir de argumentos variables.
    
    Args:
        **kwargs: Argumentos variables que incluyen claves como 'name', 'unitary_rate_period',
                  'limit1_period', 'limit1_value', etc.
    
    Returns:
        Plan: Objeto Plan de Pricing4API.
    
    Notas:
        - Los límites se ordenan por granularidad de unidad de tiempo (e.g., horas antes que meses).
        - El rate unitario se asigna si 'unitary_rate_period' está presente.
    """
    api_name = kwargs.get("name", "Unnamed API")
    unitary_rate = None
    quotas = []

    # Procesar unitary_rate si existe
    if "unitary_rate_period" in kwargs:
        period_string = kwargs["unitary_rate_period"]
        time_duration = parse_time_string_to_duration(period_string)
        unitary_rate = Limit(1, time_duration)  # Siempre es 1 para el rate unitario.

    # Procesar límites adicionales (limitN_period y limitN_value)
    limits = []
    for key, value in kwargs.items():
        if key.startswith("limit") and "_period" in key:
            period_string = value
            time_duration = parse_time_string_to_duration(period_string)
            max_requests_key = key.replace("_period", "_value")
            max_requests = kwargs.get(max_requests_key)
            if max_requests is not None:
                limits.append(Limit(int(max_requests), time_duration))  # Crear límite con valor y duración

    # Ordenar límites por granularidad de unidad de tiempo (de menor a mayor)
    limits.sort(key=lambda limit: limit.duration.to_seconds())
    quotas.extend(limits)

    # Crear objeto Plan (se usa un billing mockeado)
    plan = Plan(
        name=api_name,
        billing=(0.0, TimeDuration(1, TimeUnit.MONTH)),
        unitary_rate=unitary_rate,
        quotes=quotas
    )

    return plan

def create_plan_interactive():
    print("=== Creación Interactiva de un Plan (con parse_time_string_to_duration) ===")

    # 1. Nombre del plan
    plan_name = input("Nombre del plan: ").strip()
    if not plan_name:
        plan_name = "UnnamedPlan"

    # 2. ¿Hay un unitary_rate?
    has_unitary = input("¿Deseas incluir un unitary_rate (1 request por X tiempo)? (y/n): ").lower().strip() == 'y'
    unitary_rate = None
    if has_unitary:
        time_str = input("c de tiempo para el unitary_rate (ej: '1s', '1min', '2day'): ").strip()
        try:
            unitary_duration = parse_time_string_to_duration(time_str)
            # Unitary rate: 1 request por 'unitary_duration'
            unitary_rate = Limit(1, unitary_duration)
        except Exception as e:
            print(f"Error parseando la cadena de tiempo para unitary_rate: {e}")
            print("Se omitirá el unitary_rate.")
            unitary_rate = None

    # 3. Definir límites (quotes)
    #    Cada límite = "cantidad" + "cadena de tiempo"
    limits = []
    print("\n=== Definir límites (quotes) ===")
    while True:
        qty_str = input("Cantidad máxima de este límite (int) o escribe 'q' para terminar: ").lower().strip()
        if qty_str == 'q':
            break

        # Intentamos parsear la cantidad
        try:
            limit_qty = int(qty_str)
        except ValueError:
            print("Por favor, ingresa un número entero o 'q' para terminar.")
            continue

        time_str = input("Intervalo de tiempo (ej: '1min', '30s', '1day'): ").strip()
        try:
            limit_duration = parse_time_string_to_duration(time_str)
        except Exception as e:
            print(f"Error parseando la cadena de tiempo para este límite: {e}")
            print("Se omite este límite.")
            continue

        new_limit = Limit(limit_qty, limit_duration)
        limits.append(new_limit)
        print(f" -> Se añadió límite: {limit_qty} cada {limit_duration}")

        add_more = input("¿Agregar otro límite? (y/n): ").lower().strip()
        if add_more != 'y':
            break

    # 4. Billing "mockeado": 0.0 y 1 mes
    billing = (0.0, TimeDuration(1, TimeUnit.MONTH))

    # 5. Crear la instancia de Plan
    plan = Plan(
        name=plan_name,
        billing=billing,
        unitary_rate=unitary_rate,
        quotes=limits
    )

    # 6. Mostrar un resumen
    print(f"\n=== Plan '{plan_name}' creado con éxito ===")
    print(f"  - Nombre: {plan.name}")
    print(f"  - Billing: {plan.billing_unit}")
    if plan.unitary_rate:
        print(f"  - Unitary Rate: 1 request cada {plan.unitary_rate.duration}")
    else:
        print("  - Unitary Rate: Ninguno")
    print("  - Límites:")
    for idx, lim in enumerate(plan.limits, 1):
        print(f"    {idx}. {lim.value} cada {lim.duration}")

    return plan


