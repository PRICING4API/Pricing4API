import requests
import logging
import time
from datetime import datetime
import sqlite3
from plan import Plan

 

class Subscription:

    def __init__(self, plan: Plan, url: str, limiter: bool = True):
        self.__plan = plan
        self.__url = url
        self.__limiter = limiter
        self.__subscription_time = time.time()
        self.__accumulated_requests = 0
        self.__last_request_time = 0

        logging.basicConfig(filename='api_requests.log', level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        logging.info(f"Subscription to {url} started at {self.__subscription_time}")

        conn = sqlite3.connect('api_requests.db')
        self.__c = conn.cursor()

        # Crear la tabla si no existe
        self.__c.execute('''
        CREATE TABLE IF NOT EXISTS http_requests (
            timestamp DATETIME,
            endpoint TEXT,
            response_code INTEGER
        )
        ''')

       # self.__last_usage_start_date = plan.period

    def close(self):
        logging.info(f"Subscription to {self.__url} closed at {self.__subscription_time}")
        self.__c.commit()
        self.__c.close()

 

    def available_request(self, t) -> bool:
        '''Check if a request is available at time t.'''

        if self.__plan.available_capacity(int(t+self.__subscription_time), len(self.__plan.limits)-1) < self.__accumulated_requests:
            return False
        else:
            self.__accumulated_requests += 1
        return True

 

    def make_request(self, method='GET', **kwargs):
        while self.__limiter and not self.available_request(self.__subscription_time):
            time_to_next_request = self.__plan.rate_value - (time.time() - self.__last_request_time)
            time.sleep(max(time_to_next_request, 0))  # Espera hasta que la próxima solicitud esté disponible

        self.__last_request_time = time.time()
        response = requests.request(method, self.__url, **kwargs)
        self.__c.execute('INSERT INTO http_requests (timestamp, endpoint, response_code) VALUES (?, ?, ?)',
            (datetime.now(), self.__url, response.status_code))

        if response.status_code == 200:
            logging.info(f"Petición ({self.__accumulated_requests}) válida a {self.__url}")
        elif response.status_code == 429: 
            logging.warning(f"Petición ({self.__accumulated_requests})a {self.__url} excedió el límite de tasa. ")
        else:
            logging.error(f"Petición ({self.__accumulated_requests})a {self.__url} falló con código de estado: {response.status_code}")

        return response

       

 

PlanDBLP = Plan('DBLP', (9.99, 1, None), (1, 2), [(3, 10)])

DBLPSubscription = Subscription(PlanDBLP,  'https://dblp.org/search/publ/api?q=deep+learning&format=json', True)
for _ in range(30):  # Intentamos hace 30 peticiones
    response= DBLPSubscription.make_request()
data = response.json()  # Interpretar la respuesta JSON

#Guardar (commit) los cambios y cerrar la conexión
DBLPSubscription.close()

# # Imprimir los títulos de las primeras 5 publicaciones encontradas
for publication in data['result']['hits']['hit'][:5]:
    print(publication['info']['title'])
print(response.json())

# # FILEPATH: Untitled-1

 