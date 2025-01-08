import unittest
from Pricing4API.pricing import Pricing
from Pricing4API.plan import Plan

class TestPricingAdditional(unittest.TestCase):
    
    def setUp(self):
        self.plans = [
            Plan("Basic", (5.0, 1, None), (2, 50), [(100, 1)]),
            Plan("Premium", (15.0, 1, None), (2, 50), [(300, 1)])
        ]
        self.pricing = Pricing("Test Pricing", self.plans, "GB")

    def test_initialization_with_plans(self):
        self.assertEqual(len(self.pricing.plans), 2)
        self.assertEqual(self.pricing.name, "Test Pricing")

    def test_property_getters(self):
        self.assertEqual(self.pricing.billing_object, "GB")
        self.assertEqual([plan.name for plan in self.pricing.plans], ["Basic", "Premium"])

    def test_add_plan_and_order(self):
        new_plan = Plan("Enterprise", (20.0, 1, None), (2, 50), [(500, 1)])
        self.pricing.add_plan(new_plan)
        self.assertEqual(self.pricing.plans[-1].name, "Enterprise")  # Asumiendo ordenación por precio

    def test_link_plans(self):
        # Primero, asegurarse de que la lista de planes tenga más de un plan
        basic_plan = Plan("Basic", (5.0, 1, None), (2, 50), [(100, 1)])
        premium_plan = Plan("Premium", (15.0, 1, None), (2, 50), [(300, 1)])
        enterprise_plan = Plan("Enterprise", (20.0, 1, None), (2, 50), [(500, 1)])
        
        pricing = Pricing("Test Pricing", [basic_plan, premium_plan, enterprise_plan], "GB")
        pricing.link_plans()

    
        # Verificar que los planes están correctamente enlazados
        self.assertIsNone(pricing.plans[0].previous_plan, "El primer plan debería tener 'previous' como None")
        self.assertEqual(pricing.plans[0].next_plan, premium_plan, "El siguiente plan de 'Basic' debería ser 'Premium'")
        
        self.assertEqual(pricing.plans[1].previous_plan, basic_plan, "El plan anterior a 'Premium' debería ser 'Basic'")
        self.assertEqual(pricing.plans[1].next_plan, enterprise_plan, "El siguiente plan de 'Premium' debería ser 'Enterprise'")
        
        self.assertEqual(pricing.plans[2].previous_plan, premium_plan, "El plan anterior a 'Enterprise' debería ser 'Premium'")
        self.assertIsNone(pricing.plans[2].next_plan, "El último plan debería tener 'next' como None")
        
        # Caso con un solo plan
        single_pricing = Pricing("Single Plan Pricing", [basic_plan], "GB")
        single_pricing.link_plans()
        
        self.assertIsNone(single_pricing.plans[0].previous_plan, "Con un solo plan, 'previous' debería ser None")
        self.assertIsNone(single_pricing.plans[0].next_plan, "Con un solo plan, 'next' debería ser None")


# Para ejecutar las pruebas
if __name__ == "__main__":
   
   unittest.main()