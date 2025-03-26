import asyncio
import os
import time
import httpx
from dotenv import load_dotenv
import requests

# Cargar las variables de entorno
load_dotenv()

# Variables globales para contar errores
errores_429 = 0
errores_200 = 0

# Función para realizar una llamada a la API
async def llamada_api(n, client, url, params, start_time):
    """Realiza una llamada real a la API usando un cliente compartido."""
    global errores_429, errores_200

    api_key = os.getenv('DHL_API_KEY')
    if api_key is None:
        raise ValueError("DHL_API_KEY no está definida en las variables de entorno.")

    headers = {
        'Accept': '*/*',
        'DHL-API-Key': api_key
    }

    try:
        call_time = time.time() - start_time
        print(f"[{n}] Llamada iniciada en {call_time:.2f} segundos")

        response = await client.get(url, headers=headers, params=params)

        call_time = time.time() - start_time
        print(f"[{n}] Llamada completada en {call_time:.2f} segundos con estado {response.status_code}")

        if response.status_code == 200:
            print(f"[{n}] Respuesta aceptada")
            errores_200 += 1
        elif response.status_code == 429:
            print(f"[{n}] Error 429: Rate limit exceeded")
            errores_429 += 1
        else:
            print(f"[{n}] Error en la llamada: {response.status_code} - {response.text}")
    except httpx.RequestError as exc:
        print(f"[{n}] Error de conexión: {exc}")

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

    async with httpx.AsyncClient() as client:  # Instanciamos el cliente una sola vez
        tareas = []
        for i in range(total_llamadas):
            await semaforo.acquire()
            tareas.append(asyncio.create_task(llamada_api(i, client, url, params, start_time)))

        await asyncio.gather(*tareas)

# Configuración
INTERVALO_S = 1  # Intervalo de tiempo entre lotes de llamadas
PERMISOS_POR_INTERVALO = 1  # Llamadas permitidas por intervalo
TOTAL_LLAMADAS = 100  # Número total de llamadas para simular
URL = "https://api.dhl.com/location-finder/v1/find-by-address"  # Endpoint real
PARAMS = {
    "countryCode": "ES",
    "postalCode": "28001",  # Código postal de Madrid (puedes cambiarlo)
    "radius": 5000          # Radio en metros
}

# Ejecución
start_time = time.time()
asyncio.run(controlador(INTERVALO_S, TOTAL_LLAMADAS, PERMISOS_POR_INTERVALO, URL, PARAMS, start_time))
end_time = time.time()
print(f"Tiempo total: {end_time - start_time:.2f} segundos")
print(f"Total de errores 200: {errores_200}")
print(f"Total de errores 429: {errores_429}")
