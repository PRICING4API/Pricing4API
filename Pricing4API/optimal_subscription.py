from collections import deque
import itertools
from Pricing4API.plan import Plan
from Pricing4API.pricing import Pricing
from Pricing4API.utils import format_time

s_second = 1
s_minute= 60
s_hour = 3600
s_day = 3600 * 24
s_month = 3600 * 24 * 30


# Plan(name: str, billing: tuple[float, int, Optional[float]] = None, rate: tuple[int, int] = None, quote: list[tuple[int, int]] = None, max_number_of_subscriptions: int = 1, **kwargs)

ListSendGrid=[]

ListSendGrid.append(Plan('Basic', (0.0, s_month, 0.001), (10, s_second), [(1500, s_month)]))
ListSendGrid.append(Plan('Pro', (9.95, s_month, 0.001), (10, s_second), [(40000, s_month)], 10))
ListSendGrid.append(Plan('Ultra', (79.95, s_month, 0.00085), (10, s_second), [(100000, s_month)], 10))
ListSendGrid.append(Plan('Mega', (199.95, s_month, 0.00005), (50, s_second), [(300000, s_month)], 50))

PricingSendGrid = Pricing('SendGrid', ListSendGrid, 'mails')
PricingSendGrid.link_plans()


def get_optimal_subscription(plans, num_correos, tiempo):
    mejor_combinacion = [0] * len(plans)
    mejor_precio = float('inf')
    max_correos_en_tiempo = sum(plan.max_number_of_subscriptions * plan.available_capacity(tiempo, len(plan.limits) - 1) for plan in plans)
    
    index_plan_gratuito = next((i for i, plan in enumerate(plans) if plan.price == 0.0), -1)
    
    if index_plan_gratuito != 0:
        plans[0], plans[index_plan_gratuito] = plans[index_plan_gratuito], plans[0]

    for sus in range(1, plans[0].max_number_of_subscriptions + 1):
        for rest_sus in itertools.product(*[range(plan.max_number_of_subscriptions + 1) for plan in plans[1:]]):
            suscripciones = [sus] + list(rest_sus)
            precio_actual = sum(sus * plan.price for sus, plan in zip(suscripciones, plans))
            capacidades_tiempo = [plan.available_capacity(tiempo, len(plan.limits) - 1) for plan in plans]
            correos_generados = sum(sus * capacidad for sus, capacidad in zip(suscripciones, capacidades_tiempo))

            if correos_generados >= num_correos:
                if precio_actual < mejor_precio:
                    mejor_precio = precio_actual
                    mejor_combinacion = suscripciones
    
    # Si el número de correos excede la capacidad máxima en una hora
    if num_correos > max_correos_en_tiempo:
        num_correos = max_correos_en_tiempo
        mejor_combinacion, mejor_precio = get_optimal_subscription(plans, num_correos, tiempo)
        print(f"The number of requested emails exceeds the maximum pricing capacity for {format_time(tiempo)}.")
        print(f"The best combination will be calculated for the maximum requests available in {format_time(tiempo)} ({max_correos_en_tiempo})")
    

    # Get the names of the plans
    plan_names = [plan.name for plan in plans]

    # Zip the plan names with the best combination of subscriptions
    plan_subscriptions = zip(plan_names, mejor_combinacion)

    # Format the output
    output = ', '.join(f'{num} {name}' for name, num in plan_subscriptions if num > 0)

    print(f"The best combination is {output} for a total price of {mejor_precio} $")

    return mejor_combinacion, mejor_precio
    # Convertir el precio a la unidad monetaria correcta




