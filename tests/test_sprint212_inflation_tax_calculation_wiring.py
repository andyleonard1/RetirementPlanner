import unittest

from planner.assumptions import Assumptions
from planner.planner import RetirementPlanner
from planner.tax_engine import TaxEngine
from planner.models import RetirementYear


class TestSprint212InflationTaxCalculationWiring(unittest.TestCase):
    def setUp(self):
        self.assumptions = Assumptions()
        self.assumptions.set("personal_allowance", 12570.0)
        self.assumptions.set("basic_rate_limit", 50270.0)
        self.assumptions.set("basic_rate", 0.20)
        self.assumptions.set("higher_rate", 0.40)
        self.assumptions.set("additional_rate", 0.45)

    def _year(self, factor):
        year = RetirementYear(age=67, calendar_year=2032, spouse_age=65)
        year.inflation_factor = factor
        year.your_state_pension = 12500.0
        year.pension_needed = 50000.0
        return year

    def test_enabled_tax_link_uses_year_inflation_factor(self):
        self.assumptions.set("inflation_link_tax", True)
        first = self._year(1.0)
        later = self._year(2.0)

        TaxEngine(self.assumptions).apply([first, later])

        self.assertGreater(first.income_tax, later.income_tax)

    def test_disabled_tax_link_keeps_configured_thresholds(self):
        self.assumptions.set("inflation_link_tax", False)
        first = self._year(1.0)
        later = self._year(2.0)

        TaxEngine(self.assumptions).apply([first, later])

        self.assertEqual(first.income_tax, later.income_tax)
        self.assertEqual(first.gross_pension_income, later.gross_pension_income)

    def test_first_projection_year_keeps_configured_tax_thresholds(self):
        self.assumptions.set("inflation_link_tax", True)
        year = self._year(1.0)

        TaxEngine(self.assumptions).apply([year])

        self.assertAlmostEqual(year.income_tax, 10617.08, places=2)

    def test_live_projection_changes_when_tax_link_is_disabled(self):
        linked = Assumptions()
        linked.set("inflation_link_tax", True)
        unlinked = Assumptions()
        unlinked.set("inflation_link_tax", False)

        linked_result = RetirementPlanner(linked).run()
        unlinked_result = RetirementPlanner(unlinked).run()

        self.assertEqual(len(linked_result.timeline), len(unlinked_result.timeline))
        self.assertTrue(
            any(
                a.income_tax != b.income_tax
                for a, b in zip(linked_result.timeline, unlinked_result.timeline)
            )
        )
        self.assertNotEqual(
            linked_result.timeline[-1].closing_pension,
            unlinked_result.timeline[-1].closing_pension,
        )

    def test_live_projection_uses_compounded_inflation_factors(self):
        assumptions = Assumptions()
        assumptions.set("inflation_link_tax", True)
        result = RetirementPlanner(assumptions).run()

        self.assertAlmostEqual(result.timeline[0].inflation_factor, 1.0, places=6)
        self.assertAlmostEqual(result.timeline[1].inflation_factor, 1.025, places=6)
        self.assertGreater(result.timeline[-1].inflation_factor, result.timeline[1].inflation_factor)


if __name__ == "__main__":
    unittest.main()
