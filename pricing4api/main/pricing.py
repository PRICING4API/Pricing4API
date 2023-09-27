
from pricing4api.main.plan import *
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
        df = pd.read_csv('data/Pricings.csv', delimiter=',')
        return df.transpose()
    
    




    
    
    



    
        


    