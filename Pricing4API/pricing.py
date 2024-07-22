from matplotlib import pyplot as plt
from .plan import Plan
from .utils import format_time
import pandas as pd


class Pricing:
    def __init__(self, name: str, plans: list, billing_object: str):
        self.__name = name
        self.__plans = sorted(plans, key=lambda plan: plan.price)
        self.__billing_object = billing_object
        
        

    @property
    def name(self) -> str:
        """
        Getter for the name of the pricing object.
        """
        return self.__name
    
    @property
    def plans(self) -> list:
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

        # Add information from each plan to the list
        for plan in self.__plans:
            
            column = {'': plan.name, 
                f'Rate ({self.__billing_object}/{format_time(plan.rate_frequency)})': plan.rate_value,
                #'Rate Unit': format_time(plan.rate_frequency), 
                'Quota': plan.quote_value,
                'Quota Unit': [format_time(freq) for freq in plan.quote_frequency],
                f'Base Cost ($/{format_time(plan.billing_unit)})': plan.price,
                #'Billing Unit': format_time(plan.billing_unit), 
                f'Unit Overage Cost ($/{self.__billing_object})': plan.overage_cost,
                'Max Number of Subscriptions': plan.max_number_of_subscriptions}
            columns.append(column)
            

        # Create a DataFrame from the list of dictionaries
        df = pd.DataFrame(columns)


        # Show the table
        return df.transpose()
    
    def show_more_table(self, df: pd.DataFrame) -> pd.DataFrame:
        for plan in self.plans:
            df.loc[f'Unit Base Cost ($/{self.__billing_object})'] = [plan.unit_base_cost for plan in self.plans]
            df.loc[f'New subscription threshold ({self.__billing_object}/{format_time(plan.billing_unit)})'] = [plan.overage_quote for plan in self.plans]
            # df.loc['Cost with Overage Quote'] = [plan.cost_with_overage_quote for plan in self.plans]
            df.loc[f'Upgrade plan threshold ({self.__billing_object}/{format_time(plan.billing_unit)})'] = [plan.upgrade_quote for plan in self.plans]
            df.loc[f'Downgrade plan threshold ({self.__billing_object}/{format_time(plan.billing_unit)})'] = [plan.downgrade_quote for plan in self.plans]
            earliest_coolingdown_threshold_value = [format_time(plan.earliest_coolingdown_threshold) for plan in self.plans]
            df.loc['Coolingdown threshold'] = earliest_coolingdown_threshold_value
            max_unavailability_time= [format_time(plan.max_unavailability_time) for plan in self.plans]
            max_unavailability_percentage = [plan.max_unavailability_percentage for plan in self.plans]
            df.loc['Max Unavailability'] = max_unavailability_time
            df.loc['Max Unavailability (%)'] = max_unavailability_percentage

        return df

    def show_datasheet(self) -> None:
        df = self.create_table()
        df = self.show_more_table(df)
        print(df)

    def compareTo(self, other_pricing) -> None:
        """
        Compare the pricing object with another pricing object.
        """
        if self.__name == other_pricing.name:
            df = self.create_table()
            df = self.show_more_table(df)
            df_other = other_pricing.create_table()
            df_other = other_pricing.show_more_table(df_other)
            print(df == df_other)
        else:
            print('The pricing objects are different.')
            
    

    # def plot_curve_family_max_capacity(self):
    #     plt.figure(figsize=(8, 6))  # Tamaño de la figura

    #     for plan in self.plans:
    #         t_values = range(0, plan.quote_unit)  # Rango de tiempo
    #         C_values = [plan.capacity(t) for t in t_values]

    #         plt.plot(t_values, C_values, label=plan.name)  # Agregar una etiqueta para cada gráfica

    #     plt.xlabel('t')
    #     plt.ylabel('C')
    #     plt.title('Maximum Capacity vs Time')
    #     plt.legend()  # Mostrar leyenda con los nombres de los planes
    #     plt.show()
    
    