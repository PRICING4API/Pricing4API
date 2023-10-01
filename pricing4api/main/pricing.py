
from pricing4api.main.plan import *
import pandas as pd

class Pricing:
    def __init__(self, name: str, plans: list):
        self.__name = name
        self.__plans = sorted(plans, key=lambda plan: plan.price)
        
        

    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def plans(self) -> list:
        return self.__plans
    
    def link_plans(self) -> None:
        for i in range(len(self.plans)-1):
            self.plans[i].setNext(self.plans[i+1])
            self.plans[i+1].setPrevious(self.plans[i])
        if len(self.plans) > 0:
            self.plans[-1].setNext(None)
            self.plans[0].setPrevious(None)


  
    def create_table(self) -> pd.DataFrame:
        # Crear una lista vacía para almacenar los diccionarios de cada fila
        rows = []

        # Agregar información de cada plan a la lista
        for plan in self.__plans:
            row = {self.__name: plan.name, 'Rate': plan.rate,
            'Rate Unit': plan.rate_unit , 'Quote': plan.quote,
            'Quote Unit': plan.quote_unit, 'Price': plan.price,
            'Billing Unit': plan.billing_unit, 'Overage Cost': plan.overage_cost,
            'Max Number of Subscriptions': plan.max_number_of_subscriptions}
            rows.append(row)

        # Crear un DataFrame a partir de la lista de diccionarios
        df = pd.DataFrame(rows)

        # Mostrar la tabla
        return df.transpose()
    
    





    
    
    



    
        


    