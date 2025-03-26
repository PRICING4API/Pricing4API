import asyncio
import os
import time
import httpx
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

# Cargar variables de entorno
load_dotenv()

# Obtener credenciales de Bitbucket
BITBUCKET_USERNAME = os.getenv("BITBUCKET_USERNAME")
BITBUCKET_APP_PASSWORD = os.getenv("BITBUCKET_APP_KEY")

# Función para realizar una llamada a la API con Basic Auth
async def llamada_api(n, client, url, start_time):
    """Realiza una llamada real a la API usando un cliente compartido."""
    try:
        call_time = time.time() - start_time
        print(f"[{n}] Llamada iniciada en {call_time:.2f} segundos")

        # Hacer la petición con autenticación Basic Auth
        response = await client.get(url)

        call_time = time.time() - start_time
        print(f"[{n}] Llamada completada en {call_time:.2f} segundos con estado {response.status_code}")

        if response.status_code == 200:
            print(f"[{n}] Respuesta OK")
            print(response.json())
        elif response.status_code == 429:
            print(f"[{n}] Error 429: Rate limit exceeded")
            print(response.text)
            print(response.headers)
        else:
            print(f"[{n}] Error en la llamada: {response.status_code} - {response.text}")
    except httpx.RequestError as exc:
        print(f"[{n}] Error de conexión: {exc}")

# Función para liberar permisos periódicamente
async def liberador_permisos(semaforo, intervalo_s, permisos_por_intervalo):
    """Libera permisos periódicamente, asegurando que la primera llamada no espere."""
    # 🚀 **Liberar un permiso inicial** para evitar la espera en la primera ejecución
    for _ in range(permisos_por_intervalo):
        semaforo.release()

    while True:
        await asyncio.sleep(intervalo_s)
        for _ in range(permisos_por_intervalo):
            semaforo.release()

# Controlador principal
async def controlador(intervalo_s, total_llamadas, permisos_por_intervalo, url, start_time):
    """Controla las llamadas asegurando que el rate limit se respete."""
    semaforo = asyncio.Semaphore(0)
    asyncio.create_task(liberador_permisos(semaforo, intervalo_s, permisos_por_intervalo))

    async with httpx.AsyncClient() as client:  # Instanciamos el cliente una sola vez
        tareas = []
        for i in range(total_llamadas):
            await semaforo.acquire()
            tareas.append(asyncio.create_task(llamada_api(i, client, url, start_time)))

        await asyncio.gather(*tareas)

# Configuración
INTERVALO_S = 2  # Intervalo de tiempo entre lotes de llamadas
PERMISOS_POR_INTERVALO = 10  # Llamadas permitidas por intervalo
TOTAL_LLAMADAS = 101  # Número total de llamadas para simular
# Endpoint de prueba (listar repos en un workspace)
WORKSPACE = "bitbucket"
URL = f"https://api.bitbucket.org/2.0/repositories/jespern"

# Ejecutar prueba
start_time = time.time()
asyncio.run(controlador(INTERVALO_S, TOTAL_LLAMADAS, PERMISOS_POR_INTERVALO, URL, start_time))
end_time = time.time()
print(f"Tiempo total: {end_time - start_time:.2f} segundos")
