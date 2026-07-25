"""
Basic tests for Strategy Engine.
"""

import unittest

from planner.assumptions import Assumptions
from planner.timeline import TimelineEngine
from planner.strategy_engine import StrategyEngine


class StrategyEngineTests(unittest.TestCase):

    def create_year(self):

        assumptions = Assumptions()

        timeline = TimelineEngine(assumptions).build()

        year = timeline[0]

        year.cash_available = 5000
        year.target_spending = 35000
        year.maximum_tax_efficient_pension = 10000
        year.isa_closing = 50000
        year.savings_closing = 10000

        return assumptions, year

    def test_strategy_runs(self):

        assumptions = Assumptions()

        timeline = TimelineEngine(assumptions).build()

        StrategyEngine(assumptions).apply(timeline)

        self.assertTrue(len(timeline) > 0)

    def test_pension_first_uses_tax_efficient_pension(self):

        assumptions, year = self.create_year()

        assumptions.data["withdrawal_strategy"] = "PENSION_FIRST"

        StrategyEngine(assumptions).apply([year])

        self.assertEqual(year.interest_used, 5000)
        self.assertEqual(year.pension_needed, 30000)
        self.assertEqual(year.isa_used, 0)
    def test_isa_first_uses_tax_efficient_pension_then_isa(self):

        assumptions, year = self.create_year()

        assumptions.data["withdrawal_strategy"] = "ISA_FIRST"

        StrategyEngine(assumptions).apply([year])

        self.assertEqual(year.interest_used, 5000)
        self.assertEqual(year.pension_needed, 10000)
        self.assertEqual(year.isa_used, 20000)

    def test_unknown_strategy_defaults_to_pension_first(self):

        assumptions, year = self.create_year()

        assumptions.data["withdrawal_strategy"] = "SOMETHING_RANDOM"

        StrategyEngine(assumptions).apply([year])

        self.assertEqual(year.interest_used, 5000)
        self.assertEqual(year.pension_needed, 30000)
        self.assertEqual(year.isa_used, 0)


if __name__ == "__main__":
    unittest.main()