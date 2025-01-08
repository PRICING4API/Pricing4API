"""
    This module provides the basic functionality of a price plan subscription.
"""
import logging
import time
import sqlite3
import requests
from Pricing4API.plan import Plan


class Subscription:

    def __init__(self, plan: Plan, url: str):
        self.__plan = plan
        self.__url = url
        self.__regulated = True
        self.__subscription_time = time.time()
        self.__accumulated_requests = 0

        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S', 
                            handlers=[
                                logging.FileHandler('api_requests.log'),
                                logging.StreamHandler()
                            ])
        
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

    def regulated(self, regulated: bool) ->bool:
        '''Check if the subscription is regulated by the plan.'''
        self.__regulated = regulated

    def available_request(self, t) -> bool:
        '''Check if a request is available at time t.'''
        pos=len(self.__plan.limits)-1
        available_capacity = self.__plan.available_capacity(int(t), pos)
        if available_capacity < self.__accumulated_requests:
            return False
        else:
            return True

 
    
    def make_request(self, method='GET', **kwargs):
        '''
        Make a request to the API. If the subscription is regulated, it will wait until the next request is available.
        '''
        if self.__regulated:
            if self.available_request(time.time() - self.__subscription_time):
                logging.info(f"Waiting {self.__plan.rate_frequency} seconds")
                time.sleep(self.__plan.rate_frequency)
        
        response = requests.request(method, self.__url, **kwargs)
        if response.status_code == 429:
            logging.info(f"Request ({self.__accumulated_requests}) to {self.__url} exceeded the rate limit.")
            if 'Retry-After' in response.headers:
                logging.info(f"The Retry-After header is: {response.headers['Retry-After']} seconds")
            else:
                logging.info(f"The Retry-After header is not present.")
        elif response.status_code == 200:
            logging.info(f"Valid request ({self.__accumulated_requests}) to {self.__url}")
        else:
            logging.info(f"Request ({self.__accumulated_requests}) to {self.__url} failed with status code: {response.status_code}")
        self.__accumulated_requests += 1
        return response



PlanDBLP = Plan('DBLP', (9.99, 1, None), (1, 2), [(20, 60)])
DBLPSubscription = Subscription(PlanDBLP,  'https://dblp.org/search/publ/api')


end = time.time() + 36
logging.info(f"Consuming in a regulated manner, there should be no 429 errors until {end}.")

response = DBLPSubscription.make_request()
while(time.time() < end and response.status_code != 429):
    response = DBLPSubscription.make_request()


DBLPSubscription.regulated(False)
end = time.time() + 10
logging.info("Consuming in an unregulated manner, 429 errors should appear in approximately 10 seconds.")

while(time.time() < end and response.status_code != 429):
    response = DBLPSubscription.make_request()
if response.status_code == 429:
    if 'Retry-After' in response.headers:
        logging.info(f"Actively waiting until {time.time() + int(response.headers['Retry-After'])}")
        time.sleep(int(response.headers['Retry-After']))
    else:
        logging.info(f"Actively waiting 5 minutes, that is, until {time.time() + 5*60}.")
        time.sleep(5*60)

logging.info(f"Consuming again in a regulated manner, there should be no 429 errors.")
DBLPSubscription.regulated(True)
end = time.time() + 2 * PlanDBLP.quote_frequency[-1]
while(time.time() < end):
    DBLPSubscription.make_request()


# FUNCION ANTIGUA

    def make_request(self, method='GET', custom_rate: Limit = None, **kwargs):
        """
        Make a request to the API. If the subscription is regulated, it will wait until the next request is available.
        """
        rate_limit = Limit(self.__plan.rate_value, self.__plan.rate_frequency) if custom_rate is None else custom_rate
        burst_counter = 0
        last_request_time = self.__subscription_time

        while True:
            if self.__regulated:
                current_time = time.time()
                elapsed_time = current_time - last_request_time

                # Si hemos alcanzado el límite del burst, esperar el tiempo necesario
                if burst_counter >= rate_limit.value:
                    remaining_time = rate_limit.duration.to_seconds() - elapsed_time
                    if remaining_time > 0:
                        logging.info(f"Reached burst limit ({rate_limit.value} requests). Waiting {remaining_time:.2f} seconds...")
                        time.sleep(remaining_time)
                    burst_counter = 0  # Reiniciar el contador después de esperar
                    last_request_time = time.time()

            # Realizar la solicitud
            response = requests.request(method, self.__url, **kwargs)
            burst_counter += 1
            self.__accumulated_requests += 1

            # Manejo de respuestas
            if response.status_code == 429:
                logging.info(f"Request ({self.__accumulated_requests}) to {self.__url} exceeded the rate limit.")
                if 'Retry-After' in response.headers:
                    retry_after = float(response.headers['Retry-After'])
                    logging.info(f"Retry-After: {retry_after:.2f} seconds. Waiting...")
                    time.sleep(retry_after)
                else:
                    logging.info("Retry-After header not found. Waiting for rate limit duration...")
                    time.sleep(rate_limit.duration.to_seconds())
            elif response.status_code == 200:
                logging.info(f"Valid request ({self.__accumulated_requests}) to {self.__url}")
            else:
                logging.info(f"Request ({self.__accumulated_requests}) to {self.__url} failed with status code: {response.status_code}")

            # Retornar la respuesta
            return response


# el que funciona

    def make_request(self, method='GET', custom_rate = None, **kwargs):
        '''
        Make a request to the API. If the subscription is regulated, it will wait until the next request is available.
        '''
        
        plan_rate = self.__plan.rate_frequency if custom_rate is None else custom_rate
        if self.__regulated:
            if self.available_request(time.time() - self.__subscription_time):
                if self.__accumulated_requests > 0:
                    logging.info(f"Waiting {plan_rate}")
                    time.sleep(plan_rate.to_seconds())
            else:
                logging.info(f"Waiting {plan_rate}")
                time.sleep(plan_rate.to_seconds())
                logging.info(f"Request ({self.__accumulated_requests}) to {self.__url} may be exceeding the rate limit.")
        
        response = requests.request(method, self.__url, **kwargs)
        if response.status_code == 429:
            logging.info(f"Request ({self.__accumulated_requests + 1}) to {self.__url} exceeded the rate limit.")
            if 'Retry-After' in response.headers:
                logging.info(f"The Retry-After header is: {response.headers['Retry-After']} seconds")
            else:
                logging.info(f"The Retry-After header is not present.")
        elif response.status_code == 200:
            logging.info(f"Valid request ({self.__accumulated_requests + 1}) to {self.__url}")
        else:
            logging.info(f"Request ({self.__accumulated_requests + 1}) to {self.__url} failed with status code: {response.status_code}")
        self.__accumulated_requests += 1
        return response




    

# #Guardar (commit) los cambios y cerrar la conexión
# DBLPSubscription.close()

# # # Imprimir los títulos de las primeras 5 publicaciones encontradas
# for publication in data['result']['hits']['hit'][:5]:
#     print(publication['info']['title'])
# print(response.json())

# # # FILEPATH: Untitled-1

 