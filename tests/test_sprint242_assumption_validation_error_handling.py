import math
import unittest

from planner.assumption_resolver import AssumptionResolver


class Sprint242AssumptionValidationErrorHandlingTests(unittest.TestCase):
    def test_required_numeric_accessor_rejects_missing_value_clearly(self):
        with self.assertRaisesRegex(ValueError, "missing numeric assumption: inflation_rate"):
            AssumptionResolver({}).inflation_rate()

    def test_required_numeric_accessor_rejects_non_finite_value(self):
        for value in (math.nan, math.inf, -math.inf):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "inflation_rate must be a finite number"):
                    AssumptionResolver({"inflation_rate": value}).inflation_rate()

    def test_required_numeric_accessor_rejects_boolean(self):
        with self.assertRaisesRegex(ValueError, "savings_interest_rate must be a finite number"):
            AssumptionResolver({"savings_interest_rate": True}).savings_interest_rate()

    def test_invalid_canonical_value_does_not_fall_back_to_legacy(self):
        with self.assertRaisesRegex(ValueError, "inflation_rate must be a finite number"):
            AssumptionResolver({"inflation_rate": math.nan, "inflation": 0.02}).inflation_rate()

    def test_monte_carlo_precedence_validates_selected_value(self):
        with self.assertRaisesRegex(ValueError, "expected_return must be a finite number"):
            AssumptionResolver({"expected_return": math.nan, "expected_investment_return": 0.04}).monte_carlo_expected_return()

    def test_optional_numeric_defaults_remain_available(self):
        resolver = AssumptionResolver({})
        self.assertEqual(0.0, resolver.investment_volatility())
        self.assertEqual(0.0, resolver.inflation_volatility())
        self.assertEqual(0.0, resolver.isa_growth_rate())
        self.assertEqual(0.0, resolver.platform_charge())
        self.assertEqual(0.0, resolver.fund_charge())


if __name__ == "__main__":
    unittest.main()
