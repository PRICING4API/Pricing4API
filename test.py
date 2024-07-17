from Pricing4API.plan import Plan
from Pricing4API.pricing import Pricing


s_second = 1
s_minute = 60
s_hour = 3600
s_day = 3600 * 24
s_month = 3600 * 24 * 30

ListSendGrid = []

ListSendGrid.append(
    Plan("Basic", (0.0, s_month, 0.001), (10, s_second), [(1500, s_month)])
)
ListSendGrid.append(
    Plan("Pro", (9.95, s_month, 0.001), (10, s_second), [(40000, s_month)], 10)
)
ListSendGrid.append(
    Plan("Ultra", (79.95, s_month, 0.00085), (10, s_second), [(100000, s_month)], 10)
)
ListSendGrid.append(
    Plan("Mega", (199.95, s_month, 0.00005), (50, s_second), [(300000, s_month)], 50)
)

PricingSendGrid = Pricing("SendGrid", ListSendGrid, "mails")
PricingSendGrid.link_plans()


print(f"ListSendGrid: {ListSendGrid}")
print(f"PricingSendGrid: {PricingSendGrid.show_datasheet()}")
