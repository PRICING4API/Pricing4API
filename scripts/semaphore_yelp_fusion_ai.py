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

# Función para realizar una llamada a la API de Yelp AI Chat
async def llamada_api(n, client, url, data, start_time):
    global errores_429, errores_200

    headers = {
        'Authorization': f'Bearer {yelp_api_key}',
        'Content-Type': 'application/json'
    }

    try:
        call_time = time.time() - start_time
        print(f"[{n}] Llamada iniciada en {call_time:.2f} segundos")

        # Convertir el cuerpo a JSON manualmente y enviarlo como 'data'
        response = await client.post(url, headers=headers, data=json.dumps(data))

        call_time = time.time() - start_time
        print(f"[{n}] Llamada completada en {call_time:.2f} segundos con estado {response.status_code}")

        # Procesar la respuesta
        if response.status_code == 200:
            respuesta_json = response.json()
            print(f"[{n}] ✅ Respuesta de la IA: {respuesta_json.get('reply', 'Sin respuesta')}")
            errores_200 += 1
        elif response.status_code == 429:
            print(f"[{n}] ❌ Error 429: Límite de tasa excedido")
            errores_429 += 1
        else:
            print(f"[{n}] ❌ Error {response.status_code}: {response.text}")

    except httpx.RequestError as exc:
        print(f"[{n}] ⚠️ Error de conexión: {exc}")

# Función para liberar permisos periódicamente
async def liberador_permisos(semaforo, intervalo_s, permisos_por_intervalo):
    """Libera permisos cada cierto tiempo respetando las cuotas de la API de Yelp."""
    while True:
        for _ in range(permisos_por_intervalo):
            semaforo.release()
        await asyncio.sleep(intervalo_s)

# Controlador principal
async def controlador(intervalo_s, total_llamadas, permisos_por_intervalo, url, data, start_time):
    semaforo = asyncio.Semaphore(0)
    asyncio.create_task(liberador_permisos(semaforo, intervalo_s, permisos_por_intervalo))

    async with httpx.AsyncClient() as client:
        tareas = []
        for i in range(total_llamadas):
            await semaforo.acquire()
            tareas.append(asyncio.create_task(llamada_api(i, client, url, data, start_time)))

        await asyncio.gather(*tareas)

# Configuración del semáforo
INTERVALO_S = 0
PERMISOS_POR_INTERVALO = 1
TOTAL_LLAMADAS = 1  # Número de llamadas a realizar
URL = "https://api.yelp.com/ai/chat/v2"

# Datos para la solicitud (ajústalos según tu caso)
DATA = {
    "query": "¿Puedes recomendarme un buen restaurante italiano en Sevilla?",
    "user_context": {
        "locale": "es_ES",
        "latitude": 37.3891,
        "longitude": -5.9845
    }
}

# Ejecución
start_time = time.time()
asyncio.run(controlador(INTERVALO_S, TOTAL_LLAMADAS, PERMISOS_POR_INTERVALO, URL, DATA, start_time))
end_time = time.time()

# Resumen final
print(f"\n⏱️ Tiempo total: {end_time - start_time:.2f} segundos")
print(f"✅ Total de respuestas 200: {errores_200}")
print(f"❌ Total de errores 429: {errores_429}")
