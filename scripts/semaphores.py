import asyncio
import time
import httpx

async def llamada_api(n, url, params):
    """Realiza una llamada real a la API de DBLP"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            print(f"[{n}] Llamada completada con estado {response.status_code}")
            if response.status_code == 200:
                print(f"[{n}] Respuesta:")  # Muestra un fragmento de la respuesta
            else:
                print(f"[{n}] Error en la llamada: {response.status_code}")
        except httpx.RequestError as exc:
            print(f"[{n}] Error de conexión: {exc}")

async def liberador_permisos(semaforo, intervalo_s, permisos_por_intervalo):
    """Libera un número fijo de permisos cada intervalo de tiempo"""
    # Libera permisos inmediatamente en la primera iteración
    for _ in range(permisos_por_intervalo):
        semaforo.release()
    while True:
        await asyncio.sleep(intervalo_s)  # Espera el intervalo definido (100 ms)
        for _ in range(permisos_por_intervalo):  # Libera los permisos necesarios
            semaforo.release()

async def controlador(intervalo_s, total_llamadas, permisos_por_intervalo, url, params):
    """Controla las llamadas asegurando que el rate limit se respete"""
    semaforo = asyncio.Semaphore(0)  # Semáforo inicial con 0 permisos
    asyncio.create_task(liberador_permisos(semaforo, intervalo_s, permisos_por_intervalo))  # Libera permisos periódicamente

    tareas = []
    for i in range(total_llamadas):
        await semaforo.acquire()  # Espera a obtener un permiso del semáforo
        tareas.append(asyncio.create_task(llamada_api(i, url, params)))  # Lanza la llamada API

    # Espera a que todas las tareas se completen
    await asyncio.gather(*tareas)

# Configuración del simulador
INTERVALO_S = 0.1  # Intervalo de tiempo entre lotes de llamadas
PERMISOS_POR_INTERVALO = 10  # Llamadas permitidas por intervalo
TOTAL_LLAMADAS = 10  # Número total de llamadas para simular
URL = "https://dblp.org/search/publ/api"  # Endpoint de ejemplo
PARAMS = {
    "q": "machine learning",  # Consulta de ejemplo
    "h": 10,  # Número de resultados por página
    "format": "json"  # Formato de la respuesta
}

start_time = time.time()

# Ejecuta el controlador
asyncio.run(controlador(INTERVALO_S, TOTAL_LLAMADAS, PERMISOS_POR_INTERVALO, URL, PARAMS))
end_time = time.time()
print(f"Tiempo total: {end_time - start_time:.2f} segundos")
