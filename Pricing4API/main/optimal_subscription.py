import itertools
from Pricing4API.ancillary.time_unit import TimeDuration, TimeUnit

def get_optimal_subscription(pricing, num_requests: int, time: TimeDuration):
    """
    Calcula la mejor combinación de planes para cubrir el número requerido de peticiones en un determinado tiempo.
    
    Args:
        pricing: El objeto Pricing que contiene la lista de planes disponibles.
        num_requests: Número de peticiones que se desean cubrir.
        time: Duración del tiempo en el que se desea realizar las peticiones (TimeDuration).
        
    Returns:
        Una tupla que contiene la mejor combinación de planes y el precio total asociado.
    """
    best_combination = [0] * len(pricing.plans)
    best_price = float('inf')

    # Convertir el tiempo a milisegundos
    time_ms = time.to_milliseconds()

    # Calcular la capacidad máxima de los planes combinados en el tiempo dado
    max_requests_in_time = sum(
        plan.max_number_of_subscriptions * plan.available_capacity(TimeDuration(time_ms, TimeUnit.MILLISECOND), len(plan.limits) - 1)
        for plan in pricing.plans
    )
    
    # Identificar el índice del plan gratuito
    index_free_plan = next((i for i, plan in enumerate(pricing.plans) if plan.price == 0.0), -1)

    # Si hay un plan gratuito, moverlo al primer lugar de la lista
    if index_free_plan != 0:
        pricing.plans[0], pricing.plans[index_free_plan] = pricing.plans[index_free_plan], pricing.plans[0]

    # Iterar sobre todas las posibles combinaciones de suscripciones para encontrar la mejor
    for sus in range(1, pricing.plans[0].max_number_of_subscriptions + 1):
        for rest_sus in itertools.product(*[range(plan.max_number_of_subscriptions + 1) for plan in pricing.plans[1:]]):
            subscriptions = [sus] + list(rest_sus)
            current_price = sum(sub * plan.price for sub, plan in zip(subscriptions, pricing.plans))
            capacities_in_time = [
                plan.available_capacity(TimeDuration(time_ms, TimeUnit.MILLISECOND), len(plan.limits) - 1)
                for plan in pricing.plans
            ]
            generated_requests = sum(sub * capacity for sub, capacity in zip(subscriptions, capacities_in_time))

            # Comprobar si esta combinación cubre el número requerido de peticiones y si tiene un mejor precio
            if generated_requests >= num_requests and current_price < best_price:
                best_price = current_price
                best_combination = subscriptions

    # Verificar si el número de peticiones solicitado excede la capacidad máxima en el tiempo dado
    if num_requests > max_requests_in_time:
        num_requests = max_requests_in_time
        best_combination, best_price = get_optimal_subscription(pricing, num_requests, time)
        print(f"The number of requested emails exceeds the maximum pricing capacity for {time}.")
        print(f"The best combination will be calculated for the maximum requests available in {time} ({max_requests_in_time})")

    # Obtener los nombres de los planes
    plan_names = [plan.name for plan in pricing.plans]

    # Asociar los nombres de los planes con la mejor combinación de suscripciones
    plan_subscriptions = zip(plan_names, best_combination)

    # Formatear la salida
    output = ', '.join(f'{num} {name}' for name, num in plan_subscriptions if num > 0)
    print(f"The best combination is {output} for a total price of {best_price} $")

    return best_combination, best_price

    