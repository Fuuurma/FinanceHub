from decimal import Decimal
from django.test import TestCase
from ninja.testing import TestClient
from investments.services.bond_calculator_service import (
    BondCalculatorService,
    BondCalculationResult,
    BondType,
    CouponFrequency,
    to_decimal,
    round_decimal,
)
from investments.api.bonds import router


class BondCalculatorServiceTest(TestCase):
    def setUp(self):
        self.service = BondCalculatorService()

    def test_current_yield_basic(self):
        result = self.service.current_yield(
            face_value=Decimal("1000"),
            coupon_rate=Decimal("0.05"),
            current_price=Decimal("950"),
        )
        self.assertEqual(result, Decimal("5.2632"))

    def test_current_yield_par(self):
        result = self.service.current_yield(
            face_value=Decimal("1000"),
            coupon_rate=Decimal("0.06"),
            current_price=Decimal("1000"),
        )
        self.assertEqual(result, Decimal("6.0"))

    def test_current_yield_premium(self):
        result = self.service.current_yield(
            face_value=Decimal("1000"),
            coupon_rate=Decimal("0.08"),
            current_price=Decimal("1100"),
        )
        self.assertEqual(result, Decimal("7.2727"))

    def test_current_yield_discount(self):
        result = self.service.current_yield(
            face_value=Decimal("1000"),
            coupon_rate=Decimal("0.04"),
            current_price=Decimal("800"),
        )
        self.assertEqual(result, Decimal("5.0"))

    def test_yield_to_maturity_basic(self):
        result = self.service.yield_to_maturity(
            face_value=Decimal("1000"),
            coupon_rate=Decimal("0.05"),
            current_price=Decimal("950"),
            years_to_maturity=10,
        )
        self.assertIsInstance(result, Decimal)
        self.assertNotEqual(result, Decimal("0"))

    def test_yield_to_maturity_short_term(self):
        result = self.service.yield_to_maturity(
            face_value=Decimal("1000"),
            coupon_rate=Decimal("0.03"),
            current_price=Decimal("980"),
            years_to_maturity=2,
        )
        self.assertIsInstance(result, Decimal)

    def test_yield_to_maturity_long_term(self):
        result = self.service.yield_to_maturity(
            face_value=Decimal("1000"),
            coupon_rate=Decimal("0.05"),
            current_price=Decimal("800"),
            years_to_maturity=30,
        )
        self.assertIsInstance(result, Decimal)

    def test_yield_to_call_basic(self):
        result = self.service.yield_to_call(
            face_value=Decimal("1000"),
            coupon_rate=Decimal("0.06"),
            current_price=Decimal("1050"),
            years_to_call=5,
            call_price=Decimal("1020"),
        )
        self.assertIsInstance(result, Decimal)

    def test_zero_coupon_yield_basic(self):
        result = self.service.zero_coupon_yield(
            face_value=Decimal("1000"),
            current_price=Decimal("500"),
            years_to_maturity=10,
        )
        self.assertIsInstance(result, Decimal)
        self.assertGreater(result, Decimal("7"))
        self.assertLess(result, Decimal("8"))

    def test_zero_coupon_yield_short(self):
        result = self.service.zero_coupon_yield(
            face_value=Decimal("1000"),
            current_price=Decimal("950"),
            years_to_maturity=2,
        )
        self.assertIsInstance(result, Decimal)

    def test_treasury_bill_yield_basic(self):
        result = self.service.treasury_bill_yield(
            discount_rate=Decimal("0.02"),
            days_to_maturity=90,
        )
        self.assertIsInstance(result, dict)
        self.assertIn("discount_yield", result)
        self.assertIn("investment_yield", result)

    def test_treasury_bill_yield_short(self):
        result = self.service.treasury_bill_yield(
            discount_rate=Decimal("0.01"),
            days_to_maturity=30,
        )
        self.assertIsInstance(result, dict)

    def test_treasury_bill_yield_long(self):
        result = self.service.treasury_bill_yield(
            discount_rate=Decimal("0.05"),
            days_to_maturity=180,
        )
        self.assertIsInstance(result, dict)

    def test_bond_price_from_ytm(self):
        price = self.service.bond_price(
            face_value=Decimal("1000"),
            coupon_rate=Decimal("0.05"),
            years_to_maturity=10,
            ytm=Decimal("6.0"),
        )
        self.assertIsInstance(price, Decimal)
        self.assertLess(price, Decimal("1000"))

    def test_bond_price_par(self):
        price = self.service.bond_price(
            face_value=Decimal("1000"),
            coupon_rate=Decimal("0.06"),
            years_to_maturity=10,
            ytm=Decimal("6.0"),
        )
        self.assertAlmostEqual(price, Decimal("1000"), places=2)

    def test_calculate_all(self):
        result = self.service.calculate_all(
            face_value=Decimal("1000"),
            coupon_rate=Decimal("0.05"),
            current_price=Decimal("950"),
            years_to_maturity=10,
        )
        self.assertIsInstance(result, BondCalculationResult)
        self.assertIsNotNone(result.current_yield)
        self.assertIsNotNone(result.ytm)
        self.assertIsNotNone(result.bond_price)

    def test_calculate_all_with_frequency(self):
        result = self.service.calculate_all(
            face_value=Decimal("1000"),
            coupon_rate=Decimal("0.05"),
            current_price=Decimal("950"),
            years_to_maturity=10,
            frequency=2,
        )
        self.assertIsInstance(result, BondCalculationResult)

    def test_helper_functions(self):
        self.assertEqual(to_decimal("100"), Decimal("100"))
        self.assertEqual(to_decimal("100.5"), Decimal("100.5"))
        self.assertEqual(to_decimal(100), Decimal("100"))

        result = round_decimal(Decimal("100.555"), 2)
        self.assertEqual(result, Decimal("100.56"))


class BondAPITest(TestCase):
    def setUp(self):
        self.client = TestClient(router)

    def test_get_bond_types(self):
        response = self.client.get("/bonds/types")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("bond_types", data)

    def test_get_formulas(self):
        response = self.client.get("/bonds/formulas")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("current_yield", data)

    def test_calculate_current_yield(self):
        response = self.client.post(
            "/bonds/calculate/current-yield",
            json={
                "face_value": 1000,
                "coupon_rate": 0.05,
                "current_price": 950,
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("current_yield", data)

    def test_calculate_ytm(self):
        response = self.client.post(
            "/bonds/calculate/ytm",
            json={
                "face_value": 1000,
                "coupon_rate": 0.05,
                "current_price": 950,
                "years_to_maturity": 10,
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("ytm", data)

    def test_calculate_zero_coupon_yield(self):
        response = self.client.post(
            "/bonds/calculate/zero-coupon",
            json={
                "face_value": 1000,
                "current_price": 500,
                "years_to_maturity": 10,
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("zero_coupon_yield", data)

    def test_full_calculation(self):
        response = self.client.post(
            "/bonds/calculate",
            json={
                "face_value": 1000,
                "coupon_rate": 0.05,
                "current_price": 950,
                "years_to_maturity": 10,
                "coupon_frequency": "annual",
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("current_yield", data)
        self.assertIn("ytm", data)

    def test_bond_comparison(self):
        response = self.client.post(
            "/bonds/compare",
            json={
                "bonds": [
                    {
                        "face_value": 1000,
                        "coupon_rate": 0.05,
                        "current_price": 950,
                        "years_to_maturity": 10,
                    },
                    {
                        "face_value": 1000,
                        "coupon_rate": 0.06,
                        "current_price": 980,
                        "years_to_maturity": 10,
                    },
                ]
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("bonds", data)
        self.assertIn("best_yield", data)

    def test_invalid_input_ytm(self):
        response = self.client.post(
            "/bonds/calculate/ytm",
            json={
                "face_value": 1000,
                "coupon_rate": 0.05,
                "current_price": 950,
            },
        )
        self.assertEqual(response.status_code, 422)


class BondEdgeCasesTest(TestCase):
    def setUp(self):
        self.service = BondCalculatorService()

    def test_zero_price(self):
        with self.assertRaises(ValueError):
            self.service.current_yield(
                face_value=Decimal("1000"),
                coupon_rate=Decimal("0.05"),
                current_price=Decimal("0"),
            )

    def test_negative_price(self):
        with self.assertRaises(ValueError):
            self.service.current_yield(
                face_value=Decimal("1000"),
                coupon_rate=Decimal("0.05"),
                current_price=Decimal("-100"),
            )

    def test_zero_maturity(self):
        with self.assertRaises(ValueError):
            self.service.yield_to_maturity(
                face_value=Decimal("1000"),
                coupon_rate=Decimal("0.05"),
                current_price=Decimal("950"),
                years_to_maturity=0,
            )

    def test_negative_maturity(self):
        with self.assertRaises(ValueError):
            self.service.yield_to_maturity(
                face_value=Decimal("1000"),
                coupon_rate=Decimal("0.05"),
                current_price=Decimal("950"),
                years_to_maturity=-5,
            )

    def test_call_price_lower_than_face(self):
        result = self.service.yield_to_call(
            face_value=Decimal("1000"),
            coupon_rate=Decimal("0.06"),
            current_price=Decimal("1050"),
            years_to_call=5,
            call_price=Decimal("980"),
        )
        self.assertIsInstance(result, Decimal)
