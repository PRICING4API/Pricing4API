import unittest
from unittest.mock import patch
from plan import Plan
from pricing import Pricing
from optimal_subscription import get_optimal_subscription


s_month = 3600 * 24 * 30

class TestOptimalSubscription(unittest.TestCase):

    def setUp(self):
        # Definir algunos planes de prueba
        self.plans = [
            Plan('Free', (0.0, s_month, None), (10, 1), [(1000, s_month)]),
            Plan('Paid', (10.0, s_month, None), (100, 1), [(10000, s_month)], 5)
        ]
        self.pricing = Pricing('TestPricing', self.plans, 'emails')

    @patch.object(Plan, 'available_capacity')
    def test_base_case(self, mock_available_capacity):
        # Mockear la capacidad disponible para controlar el entorno de prueba
        mock_available_capacity.return_value = 1000
        # Suponer que queremos enviar 500 correos en un mes
        combination, price = get_optimal_subscription(self.plans, 500, s_month)
        self.assertGreaterEqual(combination[0], 1)  # Asegurar que se usa al menos una suscripción del plan gratuito
        self.assertEqual(price, 0.0)  # El precio debe ser cero si solo se usa el plan gratuito


if __name__ == '__main__':
    unittest.main()