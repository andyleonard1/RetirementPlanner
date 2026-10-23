import unittest

from planner.funds.portfolio_allocation import PortfolioAllocationValidator


class PortfolioAllocationValidatorTests(unittest.TestCase):
    def setUp(self):
        self.validator = PortfolioAllocationValidator()

    def test_aviva_75_sky_25_is_valid(self):
        result = self.validator.validate({
            "GB00BRDCMN86:GBP": 0.75,
            "Sky New Drawdown Lifestyle": 0.25,
        })
        self.assertTrue(result.valid)
        self.assertAlmostEqual(result.total_allocation, 1.0)

    def test_allocations_are_preserved(self):
        result = self.validator.validate({"A": 0.75, "B": 0.25})
        self.assertEqual(
            [(a.fund_identifier, a.allocation) for a in result.allocations],
            [("A", 0.75), ("B", 0.25)],
        )

    def test_ninety_nine_percent_is_invalid(self):
        result = self.validator.validate({"A": 0.75, "B": 0.24})
        self.assertFalse(result.valid)
        self.assertIn("100%", result.reason)

    def test_more_than_one_hundred_percent_is_invalid(self):
        result = self.validator.validate({"A": 0.75, "B": 0.30})
        self.assertFalse(result.valid)

    def test_negative_allocation_is_invalid(self):
        result = self.validator.validate({"A": 1.10, "B": -0.10})
        self.assertFalse(result.valid)
        self.assertIn("negative", result.reason)

    def test_empty_allocations_are_invalid(self):
        result = self.validator.validate({})
        self.assertFalse(result.valid)
        self.assertIn("required", result.reason)

    def test_near_exact_total_is_accepted(self):
        result = self.validator.validate({"A": 0.333333333, "B": 0.666666667})
        self.assertTrue(result.valid)

    def test_validator_does_not_silently_normalise(self):
        result = self.validator.validate({"A": 0.50, "B": 0.25})
        self.assertFalse(result.valid)
        self.assertAlmostEqual(result.total_allocation, 0.75)


if __name__ == "__main__":
    unittest.main()
