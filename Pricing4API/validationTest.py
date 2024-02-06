
from src.plan import Plan
from src.pricing import Pricing
from src.utils import format_time

from matplotlib import pyplot as plt
import numpy as np

s_second = 1
s_minute= 60
s_hour = 3600
s_day = 3600 * 24
s_month = 3600 * 24 * 30

# Plan(name: str, billing: tuple[float, int, Optional[float]] = None, rate: tuple[int, int] = None, quote: list[tuple[int, int]] = None, max_number_of_subscriptions: int = 1, **kwargs)

LDBLP=[]
PlanProDBLP= Plan('Pro', (9.99, 1, None), (1, 2*s_second), [(20, s_minute), (1000, s_minute*60)])
LDBLP.append(PlanProDBLP)
PricingDBLP = Pricing('DBLP', LDBLP, 'queries')





if __name__ == '__main__':
    # PlanProDBLP.show_rate_curve(90)
    # PlanProDBLP.show_quote_curve()
    print(PlanProDBLP.limits)

    