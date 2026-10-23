import unittest

from planner.funds.fund_import import ImportedFundReturn
from planner.funds.fund_source_validation import (
    FundSourceValidation,
    FundSourceValidator,
)


class FundSourceValidatorTests(unittest.TestCase):
    def setUp(self):
        self.validator = FundSourceValidator()

    def test_valid_source_data(self):
        result = self.validator.validate([
            ImportedFundReturn("A", 2022, 0.10),
            ImportedFundReturn("A", 2023, -0.05),
            ImportedFundReturn("B", 2023, 0.08),
        ])

        self.assertTrue(result.valid)
        self.assertEqual(result.record_count, 3)
        self.assertEqual(result.fund_count, 2)
        self.assertEqual(result.first_year, 2022)
        self.assertEqual(result.last_year, 2023)

    def test_duplicate_fund_year_is_invalid(self):
        result = self.validator.validate([
            ImportedFundReturn("A", 2023, 0.10),
            ImportedFundReturn("A", 2023, 0.12),
        ])

        self.assertFalse(result.valid)
        self.assertEqual(result.duplicate_years, (("A", 2023),))

    def test_different_funds_can_share_year(self):
        result = self.validator.validate([
            ImportedFundReturn("A", 2023, 0.10),
            ImportedFundReturn("B", 2023, 0.12),
        ])

        self.assertTrue(result.valid)

    def test_empty_source_is_valid_but_empty(self):
        result = self.validator.validate([])

        self.assertTrue(result.valid)
        self.assertEqual(result.record_count, 0)
        self.assertEqual(result.fund_count, 0)
        self.assertIsNone(result.first_year)
        self.assertIsNone(result.last_year)

    def test_duplicate_list_is_sorted(self):
        result = self.validator.validate([
            ImportedFundReturn("B", 2024, 0.10),
            ImportedFundReturn("A", 2023, 0.05),
            ImportedFundReturn("B", 2024, 0.11),
            ImportedFundReturn("A", 2023, 0.06),
        ])

        self.assertEqual(
            result.duplicate_years,
            (("A", 2023), ("B", 2024)),
        )


if __name__ == "__main__":
    unittest.main()
