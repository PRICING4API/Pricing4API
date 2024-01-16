from matplotlib import pyplot as plt
from Pricing4API.plan import Plan
import pandas as pd


class Pricing:
    def __init__(self, name: str, plans: list, billing_object: str):
        self.__name = name
        self.__plans = sorted(plans, key=lambda plan: plan.price)
        self.__billing_object = billing_object
        
        

    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def plans(self) -> list:
        return self.__plans
    
    @property
    def billing_object(self) -> str:
        return self.__billing_object
    
    def add_plan(self, plan: Plan) -> None:
        self.__plans.append(plan)

    
    def link_plans(self) -> None:
        for i in range(len(self.plans)-1):
            self.plans[i].setNext(self.plans[i+1])
            self.plans[i+1].setPrevious(self.plans[i])
        if len(self.plans) > 0:
            self.plans[-1].setNext(None)
            self.plans[0].setPrevious(None)


  
    def create_table(self) -> pd.DataFrame:
        # Create an empty list to store the dictionaries for each row
        rows = []

        # Add information from each plan to the list
        for plan in self.__plans:
            row = {self.__name: plan.name, 'Rate': plan.rate,
            'Rate Unit': plan.rate_unit , 'Quote': plan.quote,
            'Quote Unit': plan.quote_unit, 'Price': plan.price,
            'Billing Unit': plan.billing_unit, 'Overage Cost': plan.overage_cost,
            'Max Number of Subscriptions': plan.max_number_of_subscriptions}
            rows.append(row)

        # Create a DataFrame from the list of dictionaries
        df = pd.DataFrame(rows)

        # Show the table
        return df.transpose()
    
    def show_more_table(self, df: pd.DataFrame) -> pd.DataFrame:
        df.loc['Unit Base Cost'] = [plan.unit_base_cost for plan in self.plans]
        df.loc['Overage Quote'] = [plan.overage_quote for plan in self.plans]
        df.loc['Cost with Overage Quote'] = [plan.cost_with_overage_quote for plan in self.plans]
        df.loc['Upgrade Quote'] = [plan.upgrade_quote for plan in self.plans]
        df.loc['Downgrade Quote'] = [plan.downgrade_quote for plan in self.plans]
        df.loc['T_m'] = [plan.t_m for plan in self.plans]

        return df

            
    

    def plot_curve_family_max_capacity(self):
        plt.figure(figsize=(8, 6))  # Tamaño de la figura

        for plan in self.plans:
            t_values = range(0, 2592000*2)  # Rango de tiempo
            C_values = [plan.capacity(t) for t in t_values]

            plt.plot(t_values, C_values, label=plan.name)  # Agregar una etiqueta para cada gráfica

        plt.xlabel('t')
        plt.ylabel('C')
        plt.title('Maximum Capacity vs Time')
        plt.legend()  # Mostrar leyenda con los nombres de los planes
        plt.show()
    
    