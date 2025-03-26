import asyncio
import os
import time
import httpx
import json
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

# Clave de la API de Yelp desde el entorno
yelp_api_key = os.getenv('YELP_API_KEY')

# Variables globales para contar errores y almacenar respuestas
errores_429 = 0
errores_200 = 0

# Función para realizar una llamada a la API de Yelp
async def llamada_api(n, client, url, params, start_time):
    global errores_429, errores_200

    headers = {
        'Authorization': f'Bearer {yelp_api_key}',
        'Content-Type': 'application/json'
    }

    try:
        call_time = time.time() - start_time
        print(f"[{n}] Llamada iniciada en {call_time:.2f} segundos")

        # Realizar la solicitud a Yelp
        response = await client.get(url, headers=headers, params=params)

        call_time = time.time() - start_time
        print(f"[{n}] Llamada completada en {call_time:.2f} segundos con estado {response.status_code}")


        # Contar errores y éxitos
        if response.status_code == 200:
            negocios = response.json().get('businesses', [])
            print(f"[{n}] Negocios encontrados: {len(negocios)}")
            errores_200 += 1
        elif response.status_code == 429:
            print(f"[{n}] Error 429: Límite de tasa excedido")
            errores_429 += 1
        else:
            print(f"[{n}] Error {response.status_code}: {response.text}")

    except httpx.RequestError as exc:
        print(f"[{n}] Error de conexión: {exc}")


# Función para liberar permisos periódicamente
async def liberador_permisos(semaforo, intervalo_s, permisos_por_intervalo):
    for _ in range(permisos_por_intervalo):
        semaforo.release()
    while True:
        await asyncio.sleep(intervalo_s)
        for _ in range(permisos_por_intervalo):
            semaforo.release()

# Controlador principal
async def controlador(intervalo_s, total_llamadas, permisos_por_intervalo, url, params, start_time):
    semaforo = asyncio.Semaphore(0)
    asyncio.create_task(liberador_permisos(semaforo, intervalo_s, permisos_por_intervalo))

    async with httpx.AsyncClient() as client:
        tareas = []
        for i in range(total_llamadas):
            await semaforo.acquire()
            tareas.append(asyncio.create_task(llamada_api(i, client, url, params, start_time)))

        await asyncio.gather(*tareas)

# Configuración
INTERVALO_S = 0.1
PERMISOS_POR_INTERVALO = 1
TOTAL_LLAMADAS = 500
URL = "https://api.yelp.com/v3/businesses/search"

# Parámetros de la solicitud (ajustables según necesidades)
PARAMS = {
    "term": "cafe",
    "location": "Madrid",
    "limit": 3
}

# Ejecución
start_time = time.time()
asyncio.run(controlador(INTERVALO_S, TOTAL_LLAMADAS, PERMISOS_POR_INTERVALO, URL, PARAMS, start_time))
end_time = time.time()


# Resumen final
print(f"\nTiempo total: {end_time - start_time:.2f} segundos")
print(f"Total de respuestas 200: {errores_200}")
print(f"Total de errores 429: {errores_429}")
