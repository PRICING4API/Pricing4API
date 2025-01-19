import asyncio
import os
import time
import httpx
from dotenv import load_dotenv
import requests

# Función para obtener el access token
def return_access_token():
    """Obtiene un token de acceso usando las credenciales de Amadeus."""
    load_dotenv()

    AMADEUS_CLIENT_ID = os.getenv('AMADEUS_CLIENT_ID')
    AMADEUS_CLIENT_SECRET = os.getenv('AMADEUS_CLIENT_SECRET')

    AUTH_ENDPOINT = "https://test.api.amadeus.com/v1/security/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": AMADEUS_CLIENT_ID,
        "client_secret": AMADEUS_CLIENT_SECRET
    }

    response = requests.post(AUTH_ENDPOINT, headers=headers, data=data)
    response.raise_for_status()  # Asegura que la solicitud no falló
    return response.json()['access_token']

# Función para realizar una llamada a la API
async def llamada_api(n, client, url, params, access_token, start_time):
    """Realiza una llamada real a la API usando un cliente compartido."""
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    try:
        call_time = time.time() - start_time
        print(f"[{n}] Llamada iniciada en {call_time:.2f} segundos")

        response = await client.get(url, headers=headers, params=params)

        call_time = time.time() - start_time
        print(f"[{n}] Llamada completada en {call_time:.2f} segundos con estado {response.status_code}")

        if response.status_code == 200:
            print(f"[{n}] Respuesta: ")
        elif response.status_code == 429:
            print(f"[{n}] Error 429: Rate limit exceeded")
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
async def controlador(intervalo_s, total_llamadas, permisos_por_intervalo, url, params, access_token, start_time):
    """Controla las llamadas asegurando que el rate limit se respete."""
    semaforo = asyncio.Semaphore(0)
    asyncio.create_task(liberador_permisos(semaforo, intervalo_s, permisos_por_intervalo))

    async with httpx.AsyncClient() as client:  # Instanciamos el cliente una sola vez
        tareas = []
        for i in range(total_llamadas):
            await semaforo.acquire()
            tareas.append(asyncio.create_task(llamada_api(i, client, url, params, access_token, start_time)))

        await asyncio.gather(*tareas)

# Configuración
INTERVALO_S = 0.1  # Intervalo de tiempo entre lotes de llamadas
PERMISOS_POR_INTERVALO = 1  # Llamadas permitidas por intervalo
TOTAL_LLAMADAS = 40  # Número total de llamadas para simular
URL = "https://test.api.amadeus.com/v2/shopping/flight-offers"  # Endpoint real
PARAMS = {'originLocationCode': 'MAD', 'destinationLocationCode': 'SVQ', 'departureDate': '2025-01-15', 'returnDate': '2025-01-17', 'adults': 1, 'max': 1}

# Ejecución

access_token = return_access_token()
start_time = time.time()
asyncio.run(controlador(INTERVALO_S, TOTAL_LLAMADAS, PERMISOS_POR_INTERVALO, URL, PARAMS, access_token, start_time))
end_time = time.time()
print(f"Tiempo total: {end_time - start_time:.2f} segundos")
