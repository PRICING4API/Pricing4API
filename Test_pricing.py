from pricing import Pricing
from Plans import Plan
from pricing import*
from loads import*


s_day = 3600 * 24
s_month = 3600 * 24 * 30

Plan1 = Plan('Basic', 10, 1, 1500, s_month, 0, s_month, 0.001)
Plan2 = Plan('Pro', 10, 1, 40000, s_month, 9.95, s_month, 0.001, 30)
Plan3 = Plan('Ultra', 10, 1, 100000, s_month, 79.95, s_month, 0.00085, 30)
Plan4 = Plan('Mega', 50, 1, 300000, s_month, 199.95, s_month, 0.00005, 30)

Plan5 = Plan('Basic', 10, 60, 1000, s_day, 0, s_month, 0.001)
Plan6 = Plan('Pro', 30, 60, 15000, s_day, 5.00, s_month, 0.001, 30)
Plan7 = Plan('Ultra', 3, 1, 50000, s_day, 25.00, s_month, 0.0001, 30)




plansSendGrid = [Plan1, Plan2, Plan3, Plan4]
plansShortener = [Plan5, Plan6, Plan7]

SendGrid = Pricing("SendGrid",plansSendGrid)
SendGrid.link_plans()

Shortener = Pricing("Shortener",plansShortener)
Shortener.link_plans()

TableSendGrid = SendGrid.createTable()
#TableShortener = Shortener.createTable()


if __name__ == '__main__':
    print(TableSendGrid)
    print('\n')
    #print(TableShortener)
    
