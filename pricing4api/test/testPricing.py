from pricing4api.main.pricing import *
from pricing4api.main.plan import *
from pricing4api.main.load import *

s_second = 1
s_minute= 60
s_day = 3600 * 24
s_month = 3600 * 24 * 30

#PRICING SENDGRID
PricingSendGrid = Pricing('SendGrid', [])
#ADD PLANS TO PRICING SENDGRID
PricingSendGrid.add_plan(Plan('Basic', 10, s_second, 1500, s_month, 0, s_month, 0.001))
PricingSendGrid.add_plan(Plan('Pro', 10, s_second, 40000, s_month, 9.95, s_month, 0.001, 30))
PricingSendGrid.add_plan(Plan('Ultra', 10, s_second, 100000, s_month, 79.95, s_month, 0.00085, 30))
PricingSendGrid.add_plan(Plan('Mega', 50, s_second, 300000, s_month, 199.95, s_month, 0.00005, 30))


#PRICING SHORTENERS
PricingShortener = Pricing('Shortener', [])
#ADD PLANS TO PRICING SHORTENERS
PricingShortener.add_plan(Plan('Basic', 10, s_minute, 1000, s_day, 0, s_month, 0.001))
PricingShortener.add_plan(Plan('Pro', 30, s_minute, 15000, s_day, 5.00, s_month, 0.001, 30))
PricingShortener.add_plan(Plan('Ultra', 3, s_second, 50000, s_day, 25.00, s_month, 0.0001, 30))


#PRICING FOOTBALL
PricingFootball = Pricing('Football', [])
#ADD PLANS TO PRICING FOOTBALL
PricingFootball.add_plan(Plan('Basic', 30, s_minute, 100, s_month, 0, s_month, 0.001))
PricingFootball.add_plan(Plan('Pro', 300, s_minute, 7500, s_month, 19.00, s_month, 0.001, 30))
PricingFootball.add_plan(Plan('Ultra', 450, s_minute, 75000, s_month, 29.00, s_month, 0.00085, 30))
PricingFootball.add_plan(Plan('Mega', 900, s_minute, 150000, s_month, 39.00, s_month, 0.00005, 30))


#PRICING AIRPORT
PricingAirport = Pricing('Airport', [])
#ADD PLANS TO PRICING AIRPORT
PricingAirport.add_plan(Plan('Basic', 30, s_minute, 2000, s_month, 0, s_month, 0.005))
PricingAirport.add_plan(Plan('Pro', 375, s_minute, 10000, s_month, 25.00, s_month, 0.004, 30))
PricingAirport.add_plan(Plan('Ultra', 400, s_minute, 20000, s_month, 75.00, s_month, 0.003, 30))


#LINK PLANS
PricingSendGrid.link_plans()
PricingShortener.link_plans()
PricingFootball.link_plans()
PricingAirport.link_plans()



if __name__ == '__main__':
    print(PricingSendGrid.create_table())
    print('\n')
    print(PricingShortener.create_table())
    print('\n')
    print(PricingFootball.create_table())
    print('\n')
    print(PricingAirport.create_table())
