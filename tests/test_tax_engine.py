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

    def test_tax_thresholds_inflate_when_link_enabled(self):

        self.assumptions.set("inflation_link_tax", True)

        first = self.make_year()
        first.inflation_factor = 1.0
        first.your_state_pension = 12500
        first.pension_needed = 50000

        second = self.make_year()
        second.inflation_factor = 2.0
        second.your_state_pension = 12500
        second.pension_needed = 50000

        self.engine.apply([first, second])

        self.assertGreater(first.income_tax, second.income_tax)

    def test_tax_thresholds_remain_nominal_when_link_disabled(self):

        self.assumptions.set("inflation_link_tax", False)

        first = self.make_year()
        first.inflation_factor = 1.0
        first.your_state_pension = 12500
        first.pension_needed = 50000

        second = self.make_year()
        second.inflation_factor = 2.0
        second.your_state_pension = 12500
        second.pension_needed = 50000

        self.engine.apply([first, second])

        self.assertEqual(first.income_tax, second.income_tax)

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