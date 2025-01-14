import asyncio
import logging
import time

import httpx
from matplotlib import pyplot as plt
import pandas as pd
import requests
from Pricing4API.ancillary.limit import Limit
from Pricing4API.ancillary.time_unit import TimeDuration, TimeUnit
from Pricing4API.main.plan import Plan


class Subscription:
    
    def __init__(self, plan: Plan, url: str):
        self.__plan = plan
        self.__url = url
        self.__regulated = True
        self.__subscription_time = time.time()
        self.__accumulated_requests = 0
        self.__requests_log = []
        self.__429_requests = []
        
        
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S', 
                            handlers=[
                                logging.FileHandler('api_requests.log'),
                                logging.StreamHandler()
                            ])
        
        logging.info(f"Subscription to {url} started at {self.__subscription_time}")
    
    
        
    @property
    def plan(self) -> Plan:
        return self.__plan
    
    @property
    def url(self) -> str:
        return self.__url
    
    @property
    def regulated(self) -> bool:
        return self.__regulated
    
    @property
    def subscription_time(self) -> float:
        return self.__subscription_time
    
    @property
    def accumulated_requests(self) -> int:
        return self.__accumulated_requests
    
    @property
    def requests_log(self) -> list:
        return self.__requests_log
    
    @property
    def requests_429(self) -> list:
        return self.__429_requests
        
        
    def regulated(self, regulated: bool) ->bool:
        '''Check if the subscription is regulated by the plan.'''
        self.__regulated = regulated
        
        
    def available_request(self, t) -> bool:
        pos = len(self.__plan.limits) - 1
        
        t_milliseconds = int(t) * 1000
        time_duration = TimeDuration(t_milliseconds, TimeUnit.MILLISECOND)
        
        available_capacity = self.__plan.available_capacity(time_duration, pos)
        if available_capacity < self.__accumulated_requests:
            return False
        else:
            return True
        
        
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

    def api_usage_simulator(self, time_simulation: TimeDuration):
        """
        Simulate API usage for a given time duration. If the quota is exceeded,
        wait until the quota resets and continue.
        """
        RWP = self.plan.rate_wait_period.to_seconds()
        self.__accumulated_requests = 0
        end_time = time.time() + time_simulation.to_seconds()
        responses = []

        while time.time() < end_time:
            elapsed_time = time.time() - self.__subscription_time

            if self.__accumulated_requests >= self.plan.quotes_values[-1]:
                wait_time = self.plan.quotes_frequencies[-1].to_seconds() - elapsed_time
                if wait_time > 0:
                    logging.info(f"Max. Quota reached. Waiting {wait_time} seconds for quota reset...")
                    time.sleep(wait_time)
                     
                self.__accumulated_requests = 0
                self.__subscription_time = time.time()
            response = self.make_request()
            responses.append((response.status_code, response.elapsed.total_seconds()))
            
            if response.status_code == 429:
                self.__429_requests.append((len(responses), response.headers['Retry-After']))
                
        self.__requests_log = responses

        
        for i in range(1, len(self.__requests_log) - 1):
            self.__requests_log[i] = (self.__requests_log[i][0], self.__requests_log[i][1] + self.__requests_log[i-1][1] + RWP)
            
        
        self.__requests_log[self.plan.quotes_values[-1]] = (self.__requests_log[i][0],self.plan.quotes_frequencies[-1].to_seconds() + self.__requests_log[self.plan.quotes_values[-1]][1] )


        df = pd.DataFrame(responses, columns=['Status Code', 'Response Time'])
        return df
    
    
    async def api_usage_simulator_async(self, time_simulation: TimeDuration):
        """
        Simula el uso de la API durante un tiempo definido utilizando un limitador asíncrono.
        Calcula las llamadas permitidas usando `available_capacity` del plan.
        """
        # Configuración inicial
        start_time = time.time()
        end_time = start_time + time_simulation.to_seconds()
        total_llamadas_teoricas = int(self.plan.available_capacity(time_simulation, len(self.plan.limits) - 1))
        logging.info(f"Inicio de la simulación para {total_llamadas_teoricas} llamadas en un intervalo de {time_simulation.value} {time_simulation.unit.name}")

        semaforo = asyncio.Semaphore(0)
        self.__requests_log = []
        self.__429_requests = []
        self.__accumulated_requests = 0
        cooling_down = False  # Bandera para controlar el enfriamiento

        # Función para liberar permisos periódicamente
        async def liberar_permisos():
            rate_value = self.plan.rate_value
            rate_wait_period = self.plan.rate_wait_period.to_seconds()
            for _ in range(rate_value):
                semaforo.release()

            while time.time() < end_time:
                if not cooling_down:  # Solo liberar permisos si no estamos enfriándonos
                    await asyncio.sleep(rate_wait_period)
                    logging.info(f"Waiting {rate_wait_period} seconds to release more permissions.")
                    for _ in range(rate_value):
                        semaforo.release()
                    

        # Función para realizar una solicitud
        async def realizar_llamada(n):
            nonlocal cooling_down
            async with httpx.AsyncClient() as client:
                try:
                    await semaforo.acquire()
                    if time.time() > end_time:  # Si el tiempo de simulación ha terminado
                        return

                    timestamp_sent = time.time() - start_time  # Tiempo acumulado desde el inicio
                    response = await client.get(self.url)
                    self.__requests_log.append((response.status_code, timestamp_sent))

                    if response.status_code == 429:
                        retry_after = float(response.headers.get('Retry-After', self.plan.rate_wait_period.to_seconds()))
                        self.__429_requests.append((n + 1, retry_after))
                        logging.info(f"Request {n + 1} exceeded rate limit. Retry-After: {retry_after} seconds. Entering cooling down.")
                        cooling_down = True
                        await asyncio.sleep(retry_after)  # Pausa durante el enfriamiento
                        cooling_down = False  # Reiniciar después del enfriamiento
                    elif response.status_code == 200:
                        self.__accumulated_requests += 1
                        logging.info(f"Valid request ({n + 1}) to {self.url}")
                    else:
                        logging.warning(f"Request {n + 1} failed with status code: {response.status_code}")

                except httpx.RequestError as e:
                    logging.error(f"Error en la solicitud: {e}")

        # Tarea para controlar el tiempo de simulación
        async def controlador_tiempo():
            while time.time() < end_time:
                await asyncio.sleep(0.1)  # Intervalos cortos para verificar el tiempo
            logging.info("Tiempo de simulación alcanzado. Cancelando tareas.")
            for task in tasks:
                task.cancel()

        # Crear tareas
        asyncio.create_task(liberar_permisos())  # Inicia el liberador de permisos
        tasks = [asyncio.create_task(realizar_llamada(i)) for i in range(total_llamadas_teoricas)]
        tiempo_task = asyncio.create_task(controlador_tiempo())  # Controla el tiempo límite

        # Esperar a que todas las tareas finalicen o se alcance el tiempo límite
        await asyncio.gather(*tasks, return_exceptions=True)
        await tiempo_task  # Esperar a que el controlador de tiempo termine

        # Crear un DataFrame con los resultados
        df = pd.DataFrame(self.__requests_log, columns=['Status Code', 'Timestamp Sent (seconds)'])
        logging.info("Simulación finalizada.")
        return df




    def show_real_capacity_curve_v2(self, mock_429_list=None): # TODO: que dependa del tiempo de suscripción real digamos...
        subscription_time_period = TimeDuration(time.time() - self.__subscription_time, TimeUnit.SECOND)
        ideal_points = self.plan.generate_ideal_capacity_curve()
        if mock_429_list is None:
            errores_429_int =  [(int(x[0]), int(x[1])) for x in self.__429_requests]
        else:
            errores_429_int = [(int(x[0]), int(x[1])) for x in mock_429_list]  # [(1, 300), (2, 300), ...]
        cooling_down_period = errores_429_int[0][1]  # Asumimos que no es adaptativo
        valores_429_aplicables = [x[0] for x in errores_429_int]
        rate_wait_period = self.__plan.rate_frequency.to_seconds()
        rate_value = self.__plan.rate_value

        if not valores_429_aplicables:
            return ideal_points

        retraso_acumulado = 0
        for i, valor in enumerate(valores_429_aplicables):
            if valor == 1:
                ideal_points.insert(0, (0, 0))
                retraso_acumulado = cooling_down_period
                indice_en_ideal_points = next((i for i, x in enumerate(ideal_points) if x[1] == valor), None)
            else:
                indice_en_ideal_points = next((i for i, x in enumerate(ideal_points) if x[1] == valor), None)

            ideal_points[indice_en_ideal_points] = (retraso_acumulado + cooling_down_period, valor)

            if i < len(valores_429_aplicables) - 1 and valor + 1 == valores_429_aplicables[i + 1]:
                if indice_en_ideal_points + 1 < len(ideal_points):
                    ideal_points[indice_en_ideal_points + 1] = (ideal_points[indice_en_ideal_points][0], valor + rate_value)
                else:
                    ideal_points.append((ideal_points[indice_en_ideal_points][0], valor + rate_value))
            else:
                if indice_en_ideal_points + 1 < len(ideal_points):
                    ideal_points[indice_en_ideal_points + 1] = (ideal_points[indice_en_ideal_points][0] + rate_wait_period, valor + rate_value)
                else:
                    ideal_points.append((ideal_points[indice_en_ideal_points][0] + rate_wait_period, valor + rate_value))

            retraso_acumulado = ideal_points[indice_en_ideal_points + 1][0]

            retraso_actual = retraso_acumulado

            ideal_points[indice_en_ideal_points + 2:] = [
                (retraso_actual := retraso_actual + rate_wait_period, x[1])
                for x in ideal_points[indice_en_ideal_points + 2:]
            ]

        return ideal_points
    
    def plot_combined_capacity_curves(self, mock_429_list=None):
        """
        Combina y muestra las curvas de capacidad ideal (azul) y real (rojo).
        """
        # Obtener los puntos ideales
        ideal_points = self.plan.generate_ideal_capacity_curve()
        
        # Obtener los puntos reales, ajustando con errores 429
        real_points = self.show_real_capacity_curve_v2(mock_429_list=mock_429_list)

        # Extraer tiempos y capacidades para ambas curvas
        ideal_times, ideal_capacities = zip(*ideal_points)
        real_times, real_capacities = zip(*real_points)

        # Crear la gráfica
        plt.figure(figsize=(12, 6))

        # Graficar la curva ideal
        plt.step(ideal_times, ideal_capacities, where='post', color='blue', label='Capacidad Ideal')
        
        # Graficar la curva real
        plt.step(real_times, real_capacities, where='post', color='red', label='Capacidad Real')

        # Configuración de la gráfica
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Capacidad')
        plt.title('Curvas de Capacidad: Ideal vs Real')
        plt.grid(True)
        plt.legend()
        plt.show()
        

    def demand_curve_vs_ideal_capacity(self):
        """
        Genera y visualiza una gráfica comparando la curva de demanda con la curva de capacidad ideal.
        """
        # Convertir requests_log directamente a puntos de la curva de demanda
        demand_points = [(x[1], i + 1) for i, x in enumerate(self.requests_log) if x[0] == 200]

        # Generar puntos de la curva ideal
        ideal_points = self.plan.generate_ideal_capacity_curve()

        # Extraer ejes para la curva ideal
        ideal_times = [point[0] for point in ideal_points]
        ideal_capacities = [point[1] for point in ideal_points]

        # Extraer ejes para la curva de demanda
        demand_times = [point[0] for point in demand_points]
        demand_capacities = [point[1] for point in demand_points]

        # Configurar la gráfica
        fig, ax = plt.subplots(figsize=(10, 6))

        # Graficar la curva ideal
        ax.step(ideal_times, ideal_capacities, where='post', color='blue', label='Capacidad Ideal')
        ax.fill_between(ideal_times, 0, ideal_capacities, step='post', color="green", alpha=0.3)

        # Graficar la curva de demanda
        ax.step(demand_times, demand_capacities, where='post', color='red', label='Demanda Real', linestyle='--')
        ax.scatter(demand_times, demand_capacities, color='red', s=10)  # Añadir puntos individuales

        # Etiquetas y título
        ax.set_xlabel('Tiempo (segundos)')
        ax.set_ylabel('Capacidad Acumulada')
        ax.set_ylim(0)
        ax.set_title('Curva de Demanda vs Capacidad Ideal')
        ax.grid(True)
        ax.legend()

        # Mostrar la gráfica
        plt.show()



                    
                
if __name__ == "__main__":
    plan_dblp = Plan('DBLP', (0.0, TimeDuration(1, TimeUnit.MONTH)), overage_cost=None, 
                     unitary_rate=Limit(1, TimeDuration(2, TimeUnit.SECOND)), quotes=[Limit(20, TimeDuration(1, TimeUnit.MINUTE))], max_number_of_subscriptions=1)
    
    dblp_subscription = Subscription(plan_dblp, 'https://dblp.org/search/publ/api')
    
    # Simulación de uso de la API
    
    time_simulation = (TimeDuration(1, TimeUnit.MINUTE))
    
    df = asyncio.run(dblp_subscription.api_usage_simulator_async(time_simulation))
    
    print(df)
    
    print(dblp_subscription.requests_429)
    print(dblp_subscription.requests_log)
    print(dblp_subscription.accumulated_requests)
    print(dblp_subscription.subscription_time)
    
    









