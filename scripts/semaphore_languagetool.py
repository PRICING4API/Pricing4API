import asyncio
import os
import time
import httpx
from dotenv import load_dotenv

# Cargar las variables de entorno (si usas una API Key, aunque en este caso no es necesaria)
load_dotenv()

# Variables globales para contar errores
errores_429 = 0
errores_200 = 0

# Función para realizar una llamada a la API (POST en lugar de GET)
async def llamada_api(n, client, url, data, start_time):
    """Realiza una llamada real a la API usando un cliente compartido."""
    global errores_429, errores_200

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        call_time = time.time() - start_time
        print(f"[{n}] Llamada iniciada en {call_time:.2f} segundos")

        # Realizar la llamada POST con los datos
        response = await client.post(url, headers=headers, data=data)

        call_time = time.time() - start_time
        print(f"[{n}] Llamada completada en {call_time:.2f} segundos con estado {response.status_code}")

        if response.status_code == 200:
            print(f"[{n}] Respuesta aceptada")
            errores_200 += 1
            print(f"Respuesta: {response.json()}")
        elif response.status_code == 429:
            print(f"[{n}] Error 429: Rate limit exceeded")
            errores_429 += 1
        else:
            print(f"[{n}] Error en la llamada: {response.status_code} - {response.text}")
            print(f"Cabeceras: {response.headers}")
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
async def controlador(intervalo_s, total_llamadas, permisos_por_intervalo, url, data, start_time):
    """Controla las llamadas asegurando que el rate limit se respete."""
    semaforo = asyncio.Semaphore(0)
    asyncio.create_task(liberador_permisos(semaforo, intervalo_s, permisos_por_intervalo))

    async with httpx.AsyncClient() as client:
        tareas = []
        for i in range(total_llamadas):
            await semaforo.acquire()
            tareas.append(asyncio.create_task(llamada_api(i, client, url, data, start_time)))

        await asyncio.gather(*tareas)

# Configuración de la API de LanguageTool
INTERVALO_S = 1  # Intervalo de tiempo entre lotes de llamadas
PERMISOS_POR_INTERVALO = 1  # Llamadas permitidas por intervalo
TOTAL_LLAMADAS = 21  # Número total de llamadas para simular
URL = "https://api.languagetool.org/v2/check"  # Endpoint real

# Datos para el cuerpo de la solicitud POST
DATA = {
    "text": "Este es un texto de pruba con errores.",  # Texto a revisar
    "language": "es"  # Idioma del texto
}

# Ejecución
start_time = time.time()
asyncio.run(controlador(INTERVALO_S, TOTAL_LLAMADAS, PERMISOS_POR_INTERVALO, URL, DATA, start_time))
end_time = time.time()

print(f"\nTiempo total: {end_time - start_time:.2f} segundos")
print(f"Total de respuestas 200: {errores_200}")
print(f"Total de errores 429: {errores_429}")
