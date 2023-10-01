from collections import namedtuple
from typing import Any, List
import pandas as pd


Pricings= namedtuple('Pricing', 'Pricing_Name, Name, Rate, Rate_Unit, Quote, Quote_Unit, Price, Billing_Unit, Overage_Costs')


def load_pricings(filename):
    df = pd.read_csv(filename)
    pricings = []
    for row in df.itertuples(index=False):
        pricing = Pricings(*row)
        pricings.append(pricing)
    return pricings
    

def filtra(ls:List[Any], filtro:str)-> List[Any]:
    
    lista=[(t.Pricing_Name, t.Name) for t in ls if filtro in t.Pricing_Name]
    return lista

