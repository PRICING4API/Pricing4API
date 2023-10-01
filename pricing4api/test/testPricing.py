from pricing4api.main.pricing import *
from pricing4api.main.plan import *
from pricing4api.main.load import *



s_day = 3600 * 24
s_month = 3600 * 24 * 30

Plan1 = Plan('Basic', 11, 1, 1500, s_month, 0, s_month, 0.001)
Plan2 = Plan('Pro', 10, 1, 40000, s_month, 9.95, s_month, 0.001, 30)
Plan3 = Plan('Ultra', 10, 1, 100000, s_month, 79.95, s_month, 0.00085, 30)
Plan4 = Plan('Mega', 50, 1, 300000, s_month, 199.95, s_month, 0.00005, 30)

Plan5 = Plan('Basic', 10, 60, 1000, s_day, 0, s_month, 0.001)
Plan6 = Plan('Pro', 30, 60, 15000, s_day, 5.00, s_month, 0.001, 30)
Plan7 = Plan('Ultra', 3, 1, 50000, s_day, 25.00, s_month, 0.0001, 30)

SendGridData=[Plan1, Plan2, Plan3, Plan4]
ShortenerData=[Plan5, Plan6, Plan7]

PricingSendGrid = Pricing('SendGrid', SendGridData)
PricingShortener = Pricing('Shortener', ShortenerData)

SendGridHardCode=PricingSendGrid.create_table()
ShortenerHardCode=PricingShortener.create_table()


if __name__ == '__main__':
    print(SendGridHardCode)
    print('\n')
    print(ShortenerHardCode)
