import unittest
from decimal import Decimal

from planner.funds.fund_value_calculation import FundValueCalculator


class FundValueCalculatorTests(unittest.TestCase):
    def setUp(self):
        self.calculator = FundValueCalculator()

    def test_current_aviva_sky_split(self):
        result = self.calculator.calculate(
            665000,
            {
                "GB00BRDCMN86:GBP": 0.75,
                "Sky New Drawdown Lifestyle": 0.25,
            },
        )
        self.assertEqual(
            [item.value for item in result.fund_values],
            [Decimal("498750.00"), Decimal("166250.00")],
        )
        self.assertEqual(result.total_value, Decimal("665000.00"))

    def test_single_fund_gets_entire_pension(self):
        result = self.calculator.calculate(665000, {"A": 1.0})
        self.assertEqual(result.fund_values[0].value, Decimal("665000.00"))
        self.assertEqual(result.total_value, Decimal("665000.00"))

    def test_zero_allocation_is_preserved(self):
        result = self.calculator.calculate(100000, {"A": 1.0, "B": 0.0})
        self.assertEqual(result.fund_values[1].value, Decimal("0.00"))
        self.assertEqual(result.total_value, Decimal("100000.00"))

    def test_pence_rounding_preserves_total(self):
        result = self.calculator.calculate(
            100,
            {"A": 0.333333333, "B": 0.333333333, "C": 0.333333334},
        )
        self.assertEqual(result.total_value, Decimal("100.00"))
        self.assertEqual(
            sum((item.value for item in result.fund_values), Decimal("0.00")),
            Decimal("100.00"),
        )

    def test_invalid_allocation_is_rejected(self):
        with self.assertRaises(ValueError):
            self.calculator.calculate(100000, {"A": 0.75, "B": 0.20})

    def test_negative_pension_is_rejected(self):
        with self.assertRaises(ValueError):
            self.calculator.calculate(-1, {"A": 1.0})

    def test_zero_pension_is_supported(self):
        result = self.calculator.calculate(0, {"A": 0.75, "B": 0.25})
        self.assertEqual(result.total_value, Decimal("0.00"))
        self.assertEqual(
            [item.value for item in result.fund_values],
            [Decimal("0.00"), Decimal("0.00")],
        )

    def test_decimal_starting_pension_is_supported(self):
        result = self.calculator.calculate(
            Decimal("665000.55"),
            {"A": 0.75, "B": 0.25},
        )
        self.assertEqual(result.total_value, Decimal("665000.55"))

    def test_total_value_always_matches_starting_pension(self):
        result = self.calculator.calculate(
            123456.78,
            {"A": 0.10, "B": 0.20, "C": 0.30, "D": 0.40},
        )
        self.assertEqual(result.total_value, Decimal("123456.78"))

    def test_allocation_is_returned_with_value(self):
        result = self.calculator.calculate(1000, {"A": 0.75, "B": 0.25})
        self.assertEqual(result.fund_values[0].allocation, 0.75)
        self.assertEqual(result.fund_values[1].allocation, 0.25)


if __name__ == "__main__":
    unittest.main()
