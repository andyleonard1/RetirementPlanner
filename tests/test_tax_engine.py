import unittest

from planner.assumptions import Assumptions
from planner.models import RetirementYear
from planner.tax_engine import TaxEngine


class TestTaxEngine(unittest.TestCase):

    def setUp(self):
        self.assumptions = Assumptions()

        # Use predictable values for testing
        self.assumptions.set("personal_allowance", 12570)
        self.assumptions.set("basic_rate_limit", 50270)
        self.assumptions.set("basic_rate", 0.20)
        self.assumptions.set("higher_rate", 0.40)
        self.assumptions.set("additional_rate", 0.45)

        self.engine = TaxEngine(self.assumptions)

    def make_year(self):
        year = RetirementYear(
            age=67,
            calendar_year=2032,
            spouse_age=65,
        )

        year.your_state_pension = 0
        year.pension_needed = 0

        return year

    def test_engine_can_be_created(self):
        self.assertIsNotNone(self.engine)

    def test_no_tax_when_no_income(self):

        year = self.make_year()

        timeline = [year]

        self.engine.apply(timeline)

        self.assertEqual(year.income_tax, 0.00)
        self.assertEqual(year.gross_pension_income, 0.00)

    def test_income_below_allowance(self):

        year = self.make_year()

        year.pension_needed = 10000

        self.engine.apply([year])

        self.assertEqual(year.income_tax, 0.00)
        self.assertEqual(year.gross_pension_income, 10000.00)

    def test_state_pension_reduces_allowance(self):

        year = self.make_year()

        year.your_state_pension = 10000
        year.pension_needed = 10000

        self.engine.apply([year])

        self.assertGreater(year.income_tax, 0.00)

    def test_gross_is_at_least_net(self):

        year = self.make_year()

        year.your_state_pension = 12000
        year.pension_needed = 25000

        self.engine.apply([year])

        self.assertGreaterEqual(
            year.gross_pension_income,
            year.net_pension_income,
        )

    def test_withdrawal_equals_gross_income(self):

        year = self.make_year()

        year.pension_needed = 18000

        self.engine.apply([year])

        self.assertEqual(
            year.pension_withdrawal,
            year.gross_pension_income,
        )


if __name__ == "__main__":
    unittest.main()