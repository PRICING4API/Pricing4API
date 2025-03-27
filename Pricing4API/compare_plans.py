from typing import List
import plotly.graph_objects as go

from Pricing4API.ancillary.limit import Limit
from Pricing4API.ancillary.plans_yaml import create_plan_interactive
from Pricing4API.ancillary.time_unit import TimeDuration, TimeUnit
from Pricing4API.main.plan import Plan
from matplotlib.colors import to_rgba

from Pricing4API.utils import parse_time_string_to_duration


def compare_plans(plans, time_interval, return_fig=False):
    """
    Compara las curvas de capacidad de una lista de planes.

    Parameters:
        plans (list): Lista de planes a comparar.
        time_interval (TimeDuration): Intervalo de tiempo para generar las curvas.
    """
    
    if isinstance(time_interval, str):
            time_interval = parse_time_string_to_duration(time_interval)

    predefined_colors = [
        "green", "purple", "brown", "pink", "gray", "olive", "cyan", "magenta", "teal", "lime"
    ]

    if len(plans) > len(predefined_colors):
        raise ValueError("No hay suficientes colores disponibles para todos los planes.")

    fig = go.Figure()

    for plan, color in zip(plans, predefined_colors):
        debug_values = plan.show_available_capacity_curve(
            time_interval, debug=True
        )
        times_ms, capacities = zip(*debug_values)

        original_times = [t / time_interval.unit.to_milliseconds() for t in times_ms]

        rgba_color = f"rgba({','.join(map(str, [int(c * 255) for c in to_rgba(color)[:3]]))},0.2)"

        fig.add_trace(go.Scatter(
            x=original_times,
            y=capacities,
            mode='lines',
            line=dict(color=color, shape='hv', width=1.3),
            fill='tonexty',
            fillcolor=rgba_color,
            name=f"{plan.name} ({color})"
        ))

    fig.update_layout(
        title="Comparison of Capacity Curves",
        xaxis_title=f"Time ({time_interval.unit.value})",
        yaxis_title="Capacity",
        legend_title="Plans",
        template="plotly_white",
        width=1000,
        height=600
    )

    if return_fig:
        return fig

    fig.show()


def compare_instantaneous_capacity_curves(plans, time_interval, return_fig=False):
    """
    Compara las curvas de capacidad instantánea de una lista de planes.

    Parameters:
        plans (list): Lista de planes a comparar.
        time_interval (TimeDuration): Intervalo de tiempo para generar las curvas.
    """

    predefined_colors = [
        "green", "purple", "brown", "pink", "gray", "olive", "cyan", "magenta", "teal", "lime"
    ]

    if len(plans) > len(predefined_colors):
        raise ValueError("No hay suficientes colores disponibles para todos los planes.")

    fig = go.Figure()

    for plan, color in zip(plans, predefined_colors):
        debug_values = plan.show_instantaneous_capacity_curve(
            time_interval, debug=True
        )
        times_ms, capacities = zip(*debug_values)

        original_times = [t / time_interval.unit.to_milliseconds() for t in times_ms]

        rgba_color = f"rgba({','.join(map(str, [int(c * 255) for c in to_rgba(color)[:3]]))},0.2)"

        fig.add_trace(go.Scatter(
            x=original_times,
            y=capacities,
            mode='lines',
            line=dict(color=color, shape='hv', width=1.3),
            fill='tonexty',
            fillcolor=rgba_color,
            name=f"{plan.name} ({color})"
        ))

    fig.update_layout(
        title="Comparison of Instantaneous Capacity Curves",
        xaxis_title=f"Time ({time_interval.unit.value})",
        yaxis_title="Capacity",
        legend_title="Plans",
        template="plotly_white",
        width=1000,
        height=600
    )

    if return_fig:
        return fig

    fig.show()
    
def interactive_uniformize_by_quota_inputs(plan, time_interval_str):
    """
    Muestra por consola las cuotas disponibles (los límites) y pide al usuario
    que ingrese el índice que desea uniformizar. Luego muestra la curva
    uniformizada para ese límite.
    """
    try:
        ti = parse_time_string_to_duration(time_interval_str)
    except Exception as e:
        print("Error al parsear el intervalo de tiempo:", e)
        return

    print("\n--- Cuotas disponibles ---")
    for idx, limit in enumerate(plan.limits):
        print(f"Índice {idx}: {limit.value} cada {limit.duration}")
    index_str = input("Ingrese el índice del límite a uniformizar: ").strip()
    try:
        idx = int(index_str)
    except:
        print("Índice inválido.")
        return
    try:
        fig = plan.show_quota_uniform_capacity_curve(ti, idx, return_fig=True)
        fig.show()
    except Exception as e:
        print("Error al uniformizar por cuota:", e)


def combined_capacity_curves_inputs(plan, time_interval_str, quota_index=0):
    """
    Combina en una misma gráfica:
      - La curva available (capacidad sin uniformización)
      - La curva uniformizada por unitary_rate (si está definida) o,
        en su defecto, la uniformizada por cuota (usando el índice indicado)
    """
    try:
        ti = parse_time_string_to_duration(time_interval_str)
    except Exception as e:
        print("Error al parsear el intervalo de tiempo:", e)
        return None

    # Obtener la curva available
    fig_avail = plan.show_capacity_curve(ti, return_fig=True, color="green")
    combined_fig = go.Figure()
    for trace in fig_avail.data:
        combined_fig.add_trace(trace)

    # Si el plan tiene unitary_rate, agregamos esa curva; sino, la de cuota
    if plan.unitary_rate:
        try:
            fig_unit = plan.show_uniform_capacity_curve(ti, return_fig=True, color="blue")
            for trace in fig_unit.data:
                combined_fig.add_trace(trace)
        except Exception as e:
            print("Error al agregar la curva uniformizada por unitary_rate:", e)
    else:
        try:
            fig_quota = plan.show_quota_uniform_capacity_curve(ti, quota_index, return_fig=True, color="red")
            for trace in fig_quota.data:
                combined_fig.add_trace(trace)
        except Exception as e:
            print("Error al agregar la curva uniformizada por cuota:", e)

    combined_fig.update_layout(
        title=f"Curvas combinadas - {plan.name}",
        xaxis_title=f"Time ({ti.unit.value})",
        yaxis_title="Capacity",
        template="plotly_white",
        width=1000,
        height=600
    )
    return combined_fig


def interactive_menu(plan):
    """
    Menú interactivo (usando input()) que permite elegir qué curva visualizar:
      1: Curva available (sin uniformización)
      2: Uniformizar por cuota (seleccionando el índice)
      3: Uniformizar por unitary_rate (si está definido)
      4: Combinar curvas en una misma gráfica
    """
    print("Opciones disponibles:")
    print("1: Mostrar curva available (capacidad sin uniformización)")
    print("2: Uniformizar por cuota (seleccionar límite)")
    print("3: Uniformizar por unitary_rate (si está definido)")
    print("4: Combinar curvas (available + uniformización)")
    option = input("Ingrese opción (1/2/3/4): ").strip()
    time_interval_str = input("Ingrese el intervalo de tiempo para la curva (ej. '1h' o '1h1min'): ").strip()

    if option == "1":
        try:
            ti = parse_time_string_to_duration(time_interval_str)
        except Exception as e:
            print("Error al parsear el intervalo de tiempo:", e)
            return
        print("Mostrando curva available:")
        try:
            fig = plan.show_capacity_curve(ti, return_fig=True)
            fig.show()
        except Exception as e:
            print("Error al mostrar la curva available:", e)
    elif option == "2":
        interactive_uniformize_by_quota_inputs(plan, time_interval_str)
    elif option == "3":
        if not plan.unitary_rate:
            print("El plan no tiene unitary_rate definido.")
            return
        try:
            ti = parse_time_string_to_duration(time_interval_str)
        except Exception as e:
            print("Error al parsear el intervalo de tiempo:", e)
            return
        print("Mostrando curva uniformizada por unitary_rate:")
        try:
            fig = plan.show_uniform_capacity_curve(ti, return_fig=True)
            fig.show()
        except Exception as e:
            print("Error al mostrar la curva uniformizada por unitary_rate:", e)
    elif option == "4":
        if not plan.unitary_rate:
            print("El plan no tiene unitary_rate. Se usará uniformización por cuota.")
            print("\n--- Cuotas disponibles ---")
            for idx, limit in enumerate(plan.limits):
                print(f"Índice {idx}: {limit.value} cada {limit.duration}")
            index_str = input("Ingrese el índice del límite a usar para la curva combinada: ").strip()
            try:
                quota_index = int(index_str)
            except:
                print("Índice inválido, se usará 0.")
                quota_index = 0
        else:
            quota_index = 0  # En caso de unitary_rate, se ignora el índice
        fig = combined_capacity_curves_inputs(plan, time_interval_str, quota_index)
        if fig is not None:
            fig.show()
    else:
        print("Opción no reconocida.")




if __name__ == "__main__":

    Github = Plan("Github", (0.0, TimeDuration(1, TimeUnit.MONTH)), 0.0, unitary_rate=None,quotes=[Limit(900, TimeDuration(1, TimeUnit.MINUTE)),Limit(5000, TimeDuration(1, TimeUnit.HOUR))])
    Zenhub = Plan("Zenhub", (0.0, TimeDuration(1, TimeUnit.MONTH)), 0.0, Limit(1, TimeDuration(600, TimeUnit.MILLISECOND)),[Limit(100, TimeDuration(1, TimeUnit.MINUTE)), Limit(5000, TimeDuration(1, TimeUnit.HOUR))])

    interactive_menu(Github)