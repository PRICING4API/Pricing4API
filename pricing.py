


import math
from Plans import*
import pandas as pd

class Pricing:
    def __init__(self, name: str, plans: list):
        self.__name = name
        self.__plans = sorted(plans, key=lambda plan: plan.price)
        
        
        
    
    @property
    def name(self):
        return self.__name
    
    @property
    def plans(self):
        return self.__plans
    
    def link_plans(self):
        for i in range(len(self.plans)-1):
            self.plans[i].setNext(self.plans[i+1])
            self.plans[i+1].setPrevious(self.plans[i])
        if len(self.plans) > 0:
            self.plans[-1].setNext(None)
            self.plans[0].setPrevious(None)




    def createTable(self):
        # Leer los datos del archivo CSV
        df = pd.read_csv('Pricing4API/data/Pricings.csv', delimiter=',')

        # Verificar las columnas del DataFrame original
        original_columns = df.columns

        # Transformar los datos de los planes en una lista
        data = []
        for plan in self.plans:
            # Asegurarse de que la lista de datos tenga la misma cantidad de elementos que las columnas originales
            plan_data = [plan.name, plan.price, plan.rate, plan.quote, plan.overage_cost, plan.max_number_of_subscriptions, plan.unit_base_cost, plan.upgrade_quote, plan.downgrade_quote]  # Ajustar el número de columnas aquí
            data.append(plan_data)

        # Crear DataFrame con los datos de los planes y las columnas del archivo CSV
        df_plans = pd.DataFrame(data, columns=original_columns)

        # Concatenar los DataFrames
        df_combined = pd.concat([df, df_plans])

        # Transponer el DataFrame combinado
        df_transposed = df_combined.transpose()

        return df_transposed
    
    




    
    
    



    
        


    