from typing import List

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.graph_objects as go
from Pricing4API.ancillary.time_unit import TimeDuration
from Pricing4API.main.plan import Plan
from Pricing4API.utils import format_time_with_unit



class Pricing:
    def __init__(self, name: str, plans: List[Plan], billing_object: str):
        self.__name = name
        self.__plans = sorted(plans, key=lambda plan: plan.price)
        self.__billing_object = billing_object
        
        self.link_plans()
        
        
    @property
    def name(self) -> str:
        """
        Getter for the name of the pricing object.
        """
        return self.__name
    
    @property
    def plans(self) -> List[Plan]:
        """
        Getter for the list of plans.
        """
        return self.__plans
    
    @property
    def billing_object(self) -> str:
        """
        Getter for the billing object.
        """
        return self.__billing_object
    
    def add_plan(self, plan: Plan) -> None:
        """
        Add a plan to the list of plans.
        """
        self.__plans.append(plan)
        
    def link_plans(self) -> None:
        """
        Link plans together in a linked list fashion. If there is more than one plan, each plan is linked to the next and previous plans. If there is only one plan, it is linked to itself.
        """
        if len(self.plans) > 1:
            for i in range(len(self.plans)-1):
                self.plans[i].setNext(self.plans[i+1])
                self.plans[i+1].setPrevious(self.plans[i])
            self.plans[0].setPrevious(None)
            self.plans[-1].setNext(None) 
        else:
            self.plans[0].setNext(None)
            self.plans[0].setPrevious(None)
            
    def create_table(self) -> pd.DataFrame:
        
        # Create an empty list to store the dictionaries for each row
        columns = []
        
        for plan in self.__plans:
            
            column = {'Plan Name': plan.name,
                      'Rate': plan.limits[0],
                      'Quotas': plan.limits[1:],
                      f'Base Cost ($/{plan.billing_unit})': plan.price,
                      'Unit overage cost': plan.overage_cost,
                      'Max number of subscriptions': plan.max_number_of_subscriptions}
            columns.append(column)  
            
        
        df = pd.DataFrame(columns)
        
        return df.transpose()
    
    def show_more_table(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Show a more detailed table with the same information as the original table.
        """
        for plan in self.plans:
            df.loc[f'Unit Base Cost ($/{self.__billing_object})'] = [plan.unit_base_cost for plan in self.plans]
            df.loc[f'New subscription threshold'] = [plan.overage_quote for plan in self.plans]
            df.loc[f'Upgrade plan threshold'] = [plan.upgrade_quote for plan in self.plans]
            df.loc[f'Downgrade plan threshold'] = [plan.downgrade_quote for plan in self.plans]
            df.loc['Earliest Coolingdown threshold'] = [format_time_with_unit(plan.earliest_coolingdown_threshold) for plan in self.plans]
            df.loc['Earliest Coolingdown threshold - v2 and rounded'] = [round(plan.earliest_coolingdown_threshold, 3) for plan in self.plans]
            df.loc['Max Unavailability'] = [format_time_with_unit(plan.max_unavailability_time) for plan in self.plans]
            df.loc['Max Unavailability - v2 and rounded'] = [round(plan.max_unavailability_time, 3) for plan in self.plans]
            df.loc['Max Unavailability Percentage'] = [plan.max_unavailability_percentage for plan in self.plans]
            
        return df
    
    def show_datasheet(self):
        df = self.create_table()    
        df = self.show_more_table(df)
        
        print(df)

    def show_combined_capacity_curves(self, time_interval: TimeDuration) -> None:
        """
        Genera una gráfica combinada de las curvas de capacidad de todos los planes,
        asignando colores únicos a cada uno y mostrando la leyenda correspondiente.
        """
        # Lista de colores predefinidos (excluyendo azul, rojo y naranja)
        predefined_colors = [
            "green", "purple", "brown", "pink", "gray", "olive", "cyan", "magenta", "teal", "lime"
        ]

        if len(self.__plans) > len(predefined_colors):
            raise ValueError("No hay suficientes colores disponibles para todos los planes.")

        fig = go.Figure()

        # Generar gráficas individuales y combinarlas
        for plan, color in zip(self.__plans, predefined_colors):
            # Obtener los datos del plan en modo debug
            debug_data = plan.show_available_capacity_curve(
                time_interval, debug=True
            )
            times_ms, capacities = zip(*debug_data)

            # Convertir los tiempos al formato original especificado
            original_times = [t / time_interval.unit.to_milliseconds() for t in times_ms]

            rgba_color = f"rgba({','.join(map(str, [int(c * 255) for c in mcolors.to_rgba(color)[:3]]))},0.3)"

            # Añadir la línea escalonada al gráfico combinado
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
            title=f'Curvas de capacidad combinadas - {self.__name}',
            xaxis_title=f"Tiempo ({time_interval.unit.value})",
            yaxis_title="Capacidad",
            legend_title="Planes",
            template="plotly_white",
            width=1500,
            height=900
        )

        fig.show()




