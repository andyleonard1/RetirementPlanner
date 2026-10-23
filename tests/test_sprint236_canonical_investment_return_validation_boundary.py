import unittest
from pathlib import Path

from planner.assumption_resolver import AssumptionResolver
from planner.validation_engine import ValidationEngine


class Sprint236CanonicalInvestmentReturnValidationBoundaryTests(unittest.TestCase):
    def _valid_assumptions(self):
        return {
            "current_age": 62,
            "retirement_age": 63,
            "projection_end_age": 90,
            "starting_pension": 660000.0,
            "starting_savings": 72500.0,
            "starting_isa": 126000.0,
            "annual_isa_allowance": 40000.0,
            "property_sale": 350000.0,
            "max_pension_income": 30000.0,
            "personal_allowance": 12570.0,
            "basic_rate": 0.2,
            "higher_rate": 0.4,
            "additional_rate": 0.45,
            "tax_free_pension_percentage": 0.25,
            "property_sale_age": 67,
            "expected_return": 0.04,
            "investment_volatility": 0.1,
            "platform_charge": 0.0025,
            "fund_charge": 0.0025,
            "spending_phase_1": 35000.0,
            "spending_phase_2": 32000.0,
            "spending_phase_3": 28000.0,
            "expected_investment_return": 0.0475,
        }

    def test_validation_uses_canonical_investment_return(self):
        assumptions = self._valid_assumptions()
        assumptions["expected_investment_return"] = 0.10
        assumptions["pension_growth"] = -0.10

        ValidationEngine(assumptions).validate()

    def test_validation_preserves_legacy_fallback_when_canonical_missing(self):
        assumptions = self._valid_assumptions()
        assumptions.pop("expected_investment_return")
        assumptions["pension_growth"] = 0.10

        ValidationEngine(assumptions).validate()

    def test_validation_rejects_out_of_range_legacy_fallback(self):
        assumptions = self._valid_assumptions()
        assumptions.pop("expected_investment_return")
        assumptions["pension_growth"] = 0.30

        with self.assertRaisesRegex(ValueError, "Expected investment return looks unrealistic"):
            ValidationEngine(assumptions).validate()

    def test_validation_has_no_direct_canonical_investment_return_read(self):
        source = Path("planner/validation_engine.py").read_text(encoding="utf-8")
        self.assertNotIn('self._number("expected_investment_return")', source)
        self.assertIn("AssumptionResolver(self.assumptions).expected_investment_return()", source)


if __name__ == "__main__":
    unittest.main()
