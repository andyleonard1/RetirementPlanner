import unittest

from planner.funds.portfolio_risk_calculation import PortfolioRiskCalculationService


class PortfolioRiskCalculationServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = PortfolioRiskCalculationService()

    def test_eligible_portfolio_is_calculated(self):
        result = self.service.calculate(
            {"a": 0.5, "b": 0.5},
            {"a": (0.10, 0.20, 0.30, 0.10, 0.20),
             "b": (0.00, 0.10, 0.20, 0.00, 0.10)},
        )
        self.assertTrue(result.calculated)
        self.assertIsNotNone(result.summary)
        self.assertEqual(result.excluded_funds, ())

    def test_ineligible_fund_blocks_calculation(self):
        result = self.service.calculate(
            {"a": 0.5, "b": 0.5},
            {"a": (0.10, 0.20, 0.30, 0.10, 0.20),
             "b": (0.10, 0.20, 0.30)},
        )
        self.assertFalse(result.calculated)
        self.assertIsNone(result.summary)
        self.assertEqual(result.excluded_funds, ("b",))

    def test_ineligible_fund_is_not_silently_reweighted(self):
        result = self.service.calculate(
            {"a": 0.75, "b": 0.25},
            {"a": (0.10, 0.20, 0.30, 0.10, 0.20),
             "b": (0.10, 0.20)},
        )
        self.assertFalse(result.calculated)
        self.assertIsNone(result.summary)
        self.assertIn("not eligible", result.reason)

    def test_exclusion_reason_is_preserved(self):
        result = self.service.calculate(
            {"a": 0.5, "b": 0.5},
            {"a": (0.10, 0.20, 0.30, 0.10, 0.20),
             "b": (0.10, 0.20, 0.30)},
        )
        self.assertEqual(len(result.exclusion_reasons), 1)
        self.assertEqual(result.exclusion_reasons[0][0], "b")

    def test_allocation_and_return_inputs_still_use_existing_risk_engine_rules(self):
        with self.assertRaises(ValueError):
            self.service.calculate(
                {"a": 0.6, "b": 0.3},
                {"a": (0.10, 0.20, 0.30, 0.10, 0.20),
                 "b": (0.00, 0.10, 0.20, 0.00, 0.10)},
            )

    def test_empty_portfolio_is_rejected_by_existing_engine(self):
        with self.assertRaises(ValueError):
            self.service.calculate({}, {})


if __name__ == "__main__":
    unittest.main()
