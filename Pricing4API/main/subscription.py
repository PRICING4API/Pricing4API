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
import plotly.graph_objects as go


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
        

    async def api_usage_simulator_async(self, time_simulation: TimeDuration):
        """
        Simula el uso de la API durante un tiempo definido utilizando un limitador asíncrono.
        Maneja múltiples cuotas simultáneamente sin reiniciar `__accumulated_requests`.
        """
        # Configuración inicial
        start_time = time.time()
        end_time = start_time + time_simulation.to_seconds()
        total_llamadas_teoricas = int(self.plan.available_capacity(time_simulation, len(self.plan.limits) - 1))
        logging.info(f"Inicio de la simulación para {total_llamadas_teoricas} llamadas en un intervalo de {time_simulation.value} {time_simulation.unit.name}")

        semaforo = asyncio.Semaphore(0)
        quota_states = {limit: {'requests': 0, 'reset_time': start_time + limit.duration.to_seconds()} for limit in self.plan.limits}
        self.__requests_log = []
        self.__429_requests = []
        self.__accumulated_requests = 0
        cooling_down = asyncio.Event()
        cooling_down.clear()  # Inicialmente no estamos en cooling down

        # Función para gestionar permisos
        async def gestionar_permisos_y_cuotas():
            rate_value = self.plan.rate_value
            rate_wait_period = self.plan.rate_wait_period.to_seconds()
            while time.time() < end_time:
                # Comprobar límites de las cuotas
                for limit, state in quota_states.items():
                    if state['requests'] >= limit.value:
                        now = time.time()
                        reset_time = state['reset_time']
                        if now < reset_time:
                            wait_time = reset_time - now
                            logging.info(f"Quota for {limit.value} calls per {limit.duration.value, limit.duration.unit.name} exceeded. Waiting {wait_time:.2f} seconds for reset.")
                            await asyncio.sleep(wait_time)
                        # Resetear la cuota específica
                        state['requests'] = 0
                        state['reset_time'] = time.time() + limit.duration.to_seconds()

                # Liberar permisos solo si no estamos en cooling down
                if not cooling_down.is_set():
                    for _ in range(rate_value):
                        semaforo.release()
                    await asyncio.sleep(rate_wait_period)
                    logging.info(f"Released {rate_value} permissions after {rate_wait_period} seconds.")

        # Función para realizar una solicitud
        async def realizar_llamada(n):
            async with httpx.AsyncClient() as client:
                try:
                    await semaforo.acquire()
                    if cooling_down.is_set():
                        logging.info(f"Task {n} is waiting for cooling down to end.")
                        await cooling_down.wait()  # Espera activa por el cooling down

                    # Capturar el tiempo antes de enviar la solicitud
                    timestamp_sent = time.time()
                    response = await client.get(self.url)

                    # Calcular el tiempo desde el inicio del simulador
                    elapsed_time = timestamp_sent - start_time
                    self.__requests_log.append((response.status_code, elapsed_time))

                    if response.status_code == 429:
                        retry_after = float(response.headers.get('Retry-After', self.plan.rate_wait_period.to_seconds()))
                        self.__429_requests.append((n + 1, retry_after))
                        logging.info(f"Request {n + 1} exceeded rate limit. Retry-After: {retry_after} seconds. Entering cooling down.")
                        cooling_down.set()  # Activar cooling down
                        await asyncio.sleep(retry_after)  # Pausar durante el cooling down
                        cooling_down.clear()  # Reiniciar después del cooling down
                    elif response.status_code == 200:
                        self.__accumulated_requests += 1
                        # Incrementar contador para cada cuota
                        for limit, state in quota_states.items():
                            state['requests'] += 1
                        logging.info(f"Valid request ({n + 1}) to {self.url}")
                    else:
                        logging.warning(f"Request {n + 1} failed with status code: {response.status_code}")

                except httpx.RequestError as e:
                    logging.error(f"Error en la solicitud: {e}")

        # Tarea para controlar el tiempo de simulación
        async def controlador_tiempo():
            await asyncio.sleep(time_simulation.to_seconds())  # Espera el tiempo definido
            logging.info("Tiempo de simulación alcanzado. Cancelando tareas.")
            # Cancelar todas las tareas
            for task in tasks:
                task.cancel()
            permisos_task.cancel()

        # Crear tareas
        permisos_task = asyncio.create_task(gestionar_permisos_y_cuotas())  # Inicia el manejo de permisos y cuotas
        tasks = [asyncio.create_task(realizar_llamada(i)) for i in range(total_llamadas_teoricas)]
        tiempo_task = asyncio.create_task(controlador_tiempo())  # Controla el tiempo límite

        # Esperar a que todas las tareas finalicen
        await asyncio.gather(permisos_task, *tasks, tiempo_task, return_exceptions=True)

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
        fig = go.Figure()

        # Graficar la curva ideal
        fig.add_trace(go.Scatter(
            x=ideal_times,
            y=ideal_capacities,
            mode='lines',
            line=dict(color='blue', shape='hv', width=1.3),
            name='Capacidad Ideal'
        ))

        # Graficar la curva real
        fig.add_trace(go.Scatter(
            x=real_times,
            y=real_capacities,
            mode='lines',
            line=dict(color='red', shape='hv', width=1.3),
            name='Capacidad Real'
        ))

        # Configuración de la gráfica
        fig.update_layout(
            title='Curvas de Capacidad: Ideal vs Real',
            xaxis_title='Tiempo (s)',
            yaxis_title='Capacidad',
            legend_title='Curvas',
            template='plotly_white',
            width=1000,
            height=600
        )

        fig.show()

    def demand_curve_vs_ideal_capacity(self):
        """
        Genera y visualiza una gráfica comparando la curva de demanda con la curva de capacidad ideal.
        """
        # Convertir requests_log directamente a puntos de la curva de demanda
        demand_points = [(x[1], i + 1) for i, x in enumerate(self.requests_log) if x[0] == 200]

        subscription_time = time.time() - self.subscription_time
        subscription_time = TimeDuration(subscription_time, TimeUnit.SECOND)
        # Generar puntos de la curva ideal
        ideal_points = self.plan.generate_ideal_capacity_curve(subscription_time=subscription_time)

        # Extraer ejes para la curva ideal
        ideal_times = [point[0] for point in ideal_points]
        ideal_capacities = [point[1] for point in ideal_points]

        # Extraer ejes para la curva de demanda
        demand_times = [point[0] for point in demand_points]
        demand_capacities = [point[1] for point in demand_points]

        # Crear la gráfica
        fig = go.Figure()

        # Graficar la curva ideal
        fig.add_trace(go.Scatter(
            x=ideal_times,
            y=ideal_capacities,
            mode='lines',
            line=dict(color='green', shape='hv', width=1.3),
            fill='tonexty',
            fillcolor='rgba(0, 255, 0, 0.3)',
            name='Capacidad Ideal'
        ))

        # Graficar la curva de demanda
        fig.add_trace(go.Scatter(
            x=demand_times,
            y=demand_capacities,
            mode='lines+markers',
            line=dict(color='blue', shape='hv', width=1.3, dash='dash'),
            marker=dict(color='blue', size=5),
            name='Demanda Real'
        ))

        # Configuración de la gráfica
        fig.update_layout(
            title='Curva de Demanda vs Capacidad Ideal',
            xaxis_title='Tiempo (segundos)',
            yaxis_title='Capacidad Acumulada',
            legend_title='Curvas',
            template='plotly_white',
            width=1000,
            height=600
        )

        fig.show()



                    
                
if __name__ == "__main__":
    plan_dblp = Plan('DBLP', (0.0, TimeDuration(1, TimeUnit.MONTH)), overage_cost=None, 
                     unitary_rate=Limit(1, TimeDuration(1, TimeUnit.SECOND)), quotes=[Limit(3, TimeDuration(4, TimeUnit.SECOND)), Limit(5, TimeDuration(1, TimeUnit.MINUTE))], max_number_of_subscriptions=1)
    
    dblp_subscription = Subscription(plan_dblp, 'https://dblp.org/search/publ/api')
    
    # Simulación de uso de la API
    
    time_simulation = (TimeDuration(2.5, TimeUnit.MINUTE))
    
    df = asyncio.run(dblp_subscription.api_usage_simulator_async(time_simulation))
    
    print(df)
    
    print(dblp_subscription.requests_429)
    print(dblp_subscription.requests_log)
    print(dblp_subscription.accumulated_requests)
    print(dblp_subscription.subscription_time)
    
    dblp_subscription.demand_curve_vs_ideal_capacity()











