import asyncio
import os
import time
import httpx
import json
from dotenv import load_dotenv
import requests

# Función para obtener el access token de Spotify
def return_access_token():
    """Obtiene un token de acceso usando las credenciales de Spotify."""
    load_dotenv()

    SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

    AUTH_ENDPOINT = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET
    }

    response = requests.post(AUTH_ENDPOINT, headers=headers, data=data)
    response.raise_for_status()  # Asegura que la solicitud no falló
    access_token = response.json()['access_token']

    # Imprimir el token para Postman
    print(f"\n🔑 Access Token (para Postman):\n{access_token}\n")
    return access_token

# Función para realizar una llamada a la API de Spotify
async def llamada_api(n, client, url, params, access_token, start_time):
    """Realiza una llamada a la API de Spotify usando un cliente compartido."""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    try:
        call_time = time.time() - start_time
        print(f"[{n}] Llamada iniciada en {call_time:.2f} segundos")

        response = await client.get(url, headers=headers, params=params)

        call_time = time.time() - start_time
        print(f"[{n}] Llamada completada en {call_time:.2f} segundos con estado {response.status_code}")

        if response.status_code == 200:
            print("Respuesta exitosa:")
        elif response.status_code == 429:
            print(f"[{n}] Error 429: Rate limit exceeded")
            print(response.headers.get("Retry-After", "No Retry-After header found"))
        else:
            print(f"[{n}] Error en la llamada: {response.status_code} - {response.text}")
    except httpx.RequestError as exc:
        print(f"[{n}] Error de conexión: {exc}")

# Función para liberar permisos periódicamente
async def liberador_permisos(semaforo, intervalo_s, permisos_por_intervalo):
    """Libera un número fijo de permisos cada intervalo de tiempo."""
    while True:
        for _ in range(permisos_por_intervalo):
            semaforo.release()
        await asyncio.sleep(intervalo_s)

# Controlador principal
async def controlador(intervalo_s, total_llamadas, permisos_por_intervalo, url, params, access_token, start_time):
    """Controla las llamadas asegurando que el rate limit se respete."""
    semaforo = asyncio.Semaphore(0)
    asyncio.create_task(liberador_permisos(semaforo, intervalo_s, permisos_por_intervalo))

    async with httpx.AsyncClient() as client:
        tareas = []
        for i in range(total_llamadas):
            await semaforo.acquire()
            tareas.append(asyncio.create_task(llamada_api(i, client, url, params, access_token, start_time)))

        await asyncio.gather(*tareas)

# Configuración del semáforo y API
INTERVALO_S = 0.2  # Intervalo de tiempo entre lotes de llamadas
PERMISOS_POR_INTERVALO = 50  # Llamadas permitidas por intervalo
TOTAL_LLAMADAS = 100  # Número total de llamadas para simular
URL = "https://api.spotify.com/v1/playlists/3cEYpjA9oz9GiPac4AsH4n"  # Endpoint de la playlist

# Parámetros de la solicitud (puedes ajustarlos según tus necesidades)
PARAMS = {
}

# Ejecución
access_token = return_access_token()  # Obtiene y muestra el access token
start_time = time.time()
asyncio.run(controlador(INTERVALO_S, TOTAL_LLAMADAS, PERMISOS_POR_INTERVALO, URL, PARAMS, access_token, start_time))
end_time = time.time()

# Resumen final
print(f"\nTiempo total: {end_time - start_time:.2f} segundos")
