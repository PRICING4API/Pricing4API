import asyncio
import os
import time
import httpx
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

# Variables globales para contar errores
errores_429 = 0
errores_200 = 0

# Clave secreta de Stripe desde el entorno
stripe_api_key = os.getenv('STRIPE_SECRET_KEY')

# Función para realizar una llamada a la API
async def llamada_api(n, client, url, params, start_time):
    """Realiza una llamada real a la API de Stripe usando un cliente compartido."""
    global errores_429, errores_200

    headers = {
        'Accept': '*/*',
        'Authorization': f'Bearer {stripe_api_key}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        call_time = time.time() - start_time
        print(f"[{n}] Llamada iniciada en {call_time:.2f} segundos")

        # Realizar la solicitud a Stripe
        response = await client.get(url, headers=headers, params=params)

        call_time = time.time() - start_time
        print(f"[{n}] Llamada completada en {call_time:.2f} segundos con estado {response.status_code}")

        if response.status_code == 200:
            productos = response.json().get('data', [])
            print(f"[{n}] ✅ Productos encontrados: {len(productos)}")
            for producto in productos:
                print(f"    🛍️ {producto['name']} - ID: {producto['id']}")
            errores_200 += 1
        elif response.status_code == 429:
            print(f"[{n}] ❌ Error 429: Límite de tasa excedido")
            errores_429 += 1
        else:
            print(f"[{n}] ❌ Error en la llamada: {response.status_code} - {response.text}")
            print(f"Cabeceras: {response.headers}")
    except httpx.RequestError as exc:
        print(f"[{n}] ⚠️ Error de conexión: {exc}")

# Función para liberar permisos periódicamente
async def liberador_permisos(semaforo, intervalo_s, permisos_por_intervalo):
    """Libera un número fijo de permisos cada intervalo de tiempo."""
    for _ in range(permisos_por_intervalo):
        semaforo.release()
    while True:
        await asyncio.sleep(intervalo_s)
        for _ in range(permisos_por_intervalo):
            semaforo.release()

# Controlador principal
async def controlador(intervalo_s, total_llamadas, permisos_por_intervalo, url, params, start_time):
    """Controla las llamadas asegurando que el rate limit se respete."""
    semaforo = asyncio.Semaphore(0)
    asyncio.create_task(liberador_permisos(semaforo, intervalo_s, permisos_por_intervalo))

    async with httpx.AsyncClient() as client:
        tareas = []
        for i in range(total_llamadas):
            await semaforo.acquire()
            tareas.append(asyncio.create_task(llamada_api(i, client, url, params, start_time)))

        await asyncio.gather(*tareas)

# Configuración
INTERVALO_S = 5  # Intervalo de tiempo entre lotes de llamadas
PERMISOS_POR_INTERVALO = 100  # Llamadas permitidas por intervalo
TOTAL_LLAMADAS = 10  # Número total de llamadas para simular
URL = "https://api.stripe.com/v1/products"  # Endpoint real de Stripe

# Parámetros de la solicitud (puedes ajustarlos según tus necesidades)
PARAMS = {
    "limit": 3  # Ejemplo: Obtener solo 3 productos
}

# Ejecución
start_time = time.time()
asyncio.run(controlador(INTERVALO_S, TOTAL_LLAMADAS, PERMISOS_POR_INTERVALO, URL, PARAMS, start_time))
end_time = time.time()

# Resumen final
print(f"\n⏱️ Tiempo total: {end_time - start_time:.2f} segundos")
print(f"✅ Total de respuestas 200: {errores_200}")
print(f"❌ Total de errores 429: {errores_429}")
