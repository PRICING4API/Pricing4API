from typing import List
import plotly.graph_objects as go

from Pricing4API.ancillary.limit import Limit
from Pricing4API.ancillary.time_unit import TimeDuration, TimeUnit
from Pricing4API.main.plan import Plan

def compare_plans(plans: List, time_interval: TimeDuration):
    """
    Compara las curvas de capacidad de una lista de planes de forma interactiva utilizando Plotly.

    Parameters:
        plans (list): Lista de planes a comparar.
        time_interval (TimeDuration): Intervalo de tiempo para generar las curvas.
    """
    # Definir una lista de colores únicos (excluyendo azul, rojo y naranja)
    predefined_colors = [
        "green", "purple", "brown", "pink", "gray", "olive", "cyan", "magenta", "teal", "lime"
    ]

    if len(plans) > len(predefined_colors):
        raise ValueError("No hay suficientes colores disponibles para todos los planes.")

    # Crear la figura interactiva
    fig = go.Figure()

    # Generar las curvas de cada plan con colores únicos
    for plan, color in zip(plans, predefined_colors):
        debug_values = plan.show_available_capacity_curve(
            time_interval, debug=True
        )  # Obtener los datos en modo debug
        times_ms, capacities = zip(*debug_values)

        # Convertir los tiempos al formato especificado por el usuario
        original_times = [t / time_interval.unit.to_milliseconds() for t in times_ms]

        # Añadir la curva al gráfico interactivo
        fig.add_trace(go.Scatter(
            x=original_times,
            y=capacities,
            mode='lines+markers',
            line=dict(color=color, shape='hv'),  # 'hv' mantiene el estilo escalonado
            name=f"{plan.name} ({color})"
        ))

    # Configurar los ejes y el diseño
    fig.update_layout(
        title="Comparación de curvas de capacidad",
        xaxis_title=f"Tiempo ({time_interval.unit.value})",
        yaxis_title="Capacidad",
        legend_title="Planes",
        template="plotly_white"
    )

    # Mostrar la gráfica interactiva (funciona en Deepnote)
    fig.show()
    
    
if __name__ == "__main__":
    
    Github = Plan("Github", (0.0, TimeDuration(1, TimeUnit.MONTH)), 0.0, Limit(1, TimeDuration(720, TimeUnit.MILLISECOND)),[Limit(5000, TimeDuration(1, TimeUnit.HOUR))])
    Zenhub = Plan("Zenhub", (0.0, TimeDuration(1, TimeUnit.MONTH)), 0.0, Limit(1, TimeDuration(600, TimeUnit.MILLISECOND)),[Limit(100, TimeDuration(1, TimeUnit.MINUTE)), Limit(5000, TimeDuration(1, TimeUnit.HOUR))])
    
    compare_plans([Github, Zenhub], TimeDuration(1, TimeUnit.HOUR))
