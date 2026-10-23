import unittest

from planner.assumptions import Assumptions
from planner.planner import RetirementPlanner
from planner.strategy_engine import StrategyEngine
from planner.timeline import TimelineEngine


class Sprint208AssumptionCalculationCoverageTests(unittest.TestCase):

    def make_year(self, *, target=40000.0, cash=0.0, isa=20000.0, max_pension=30000.0):
        assumptions = Assumptions()
        assumptions.set("max_pension_income", max_pension)
        timeline = TimelineEngine(assumptions).build()
        year = timeline[0]
        year.target_spending = target
        year.cash_available = cash
        year.maximum_tax_efficient_pension = 50000.0
        year.isa_closing = isa
        return assumptions, [year]

    def test_max_pension_income_caps_pension_and_routes_excess_to_isa(self):
        assumptions, timeline = self.make_year()

        StrategyEngine(assumptions).apply(timeline)

        year = timeline[0]
        self.assertEqual(year.pension_needed, 30000.0)
        self.assertEqual(year.isa_used, 10000.0)
        self.assertEqual(year.income_shortfall, 0.0)

    def test_max_pension_income_creates_shortfall_when_other_assets_are_exhausted(self):
        assumptions, timeline = self.make_year(isa=5000.0)

        StrategyEngine(assumptions).apply(timeline)

        year = timeline[0]
        self.assertEqual(year.pension_needed, 30000.0)
        self.assertEqual(year.isa_used, 5000.0)
        self.assertEqual(year.income_shortfall, 5000.0)

    def test_max_pension_income_changes_end_to_end_projection(self):
        capped = Assumptions()
        uncapped = Assumptions()
        capped.set("max_pension_income", 30000.0)
        uncapped.set("max_pension_income", 50000.0)

        capped_result = RetirementPlanner(capped, audit_context="test").run()
        uncapped_result = RetirementPlanner(uncapped, audit_context="test").run()

        capped_year = capped_result.timeline[0]
        uncapped_year = uncapped_result.timeline[0]

        self.assertEqual(capped_year.pension_needed, 30000.0)
        self.assertGreater(uncapped_year.pension_needed, 30000.0)
        self.assertGreater(capped_year.isa_used, 0.0)
        self.assertEqual(uncapped_year.isa_used, 0.0)
        self.assertNotEqual(
            capped_result.summary["ending_assets"],
            uncapped_result.summary["ending_assets"],
        )

    def test_validation_rejects_negative_max_pension_income(self):
        assumptions = Assumptions()
        assumptions.set("max_pension_income", -1.0)
        with self.assertRaisesRegex(ValueError, "max_pension_income cannot be negative"):
            assumptions.validate()


if __name__ == "__main__":
    unittest.main()
