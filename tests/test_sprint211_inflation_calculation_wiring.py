import unittest

from planner.assumptions import Assumptions
from planner.inflation_engine import InflationEngine
from planner.models import RetirementYear
from planner.planner import RetirementPlanner


class TestSprint211InflationCalculationWiring(unittest.TestCase):
    def test_inflation_engine_builds_compounded_factors(self):
        assumptions = Assumptions()
        assumptions.set("inflation_rate", 0.025)

        timeline = [
            RetirementYear(age=63, calendar_year=2027, spouse_age=60),
            RetirementYear(age=64, calendar_year=2028, spouse_age=61),
            RetirementYear(age=65, calendar_year=2029, spouse_age=62),
        ]

        InflationEngine(assumptions).apply(timeline)

        self.assertEqual(timeline[0].inflation_factor, 1.0)
        self.assertEqual(timeline[1].inflation_factor, 1.025)
        self.assertEqual(timeline[2].inflation_factor, 1.050625)

    def test_planner_runs_inflation_engine_before_cashflow(self):
        assumptions = Assumptions()
        assumptions.set("inflation_rate", 0.05)
        assumptions.set("inflation_link_spending", True)
        assumptions.set("spending_phase_1", 35000.0)

        result = RetirementPlanner(assumptions).run()
        first, second = result.timeline[0], result.timeline[1]

        self.assertEqual(first.inflation_factor, 1.0)
        self.assertEqual(second.inflation_factor, 1.05)
        self.assertEqual(first.target_spending, 35000.0)
        self.assertEqual(second.target_spending, 36750.0)

    def test_disabling_spending_link_keeps_target_spending_static(self):
        assumptions = Assumptions()
        assumptions.set("inflation_rate", 0.05)
        assumptions.set("inflation_link_spending", False)
        assumptions.set("spending_phase_1", 35000.0)

        result = RetirementPlanner(assumptions).run()
        first, second = result.timeline[0], result.timeline[1]

        self.assertEqual(first.inflation_factor, 1.0)
        self.assertEqual(second.inflation_factor, 1.05)
        self.assertEqual(first.target_spending, 35000.0)
        self.assertEqual(second.target_spending, 35000.0)

    def test_inflation_rate_changes_end_to_end_projection(self):
        low = Assumptions()
        low.set("inflation_rate", 0.0)

        high = Assumptions()
        high.set("inflation_rate", 0.05)

        low_result = RetirementPlanner(low).run()
        high_result = RetirementPlanner(high).run()

        self.assertNotEqual(
            low_result.summary["ending_assets"],
            high_result.summary["ending_assets"],
        )

    def test_inflation_rate_is_used_by_the_live_planner_not_just_the_engine(self):
        assumptions = Assumptions()
        assumptions.set("inflation_rate", 0.03)

        result = RetirementPlanner(assumptions).run()
        factors = [year.inflation_factor for year in result.timeline[:3]]

        self.assertEqual(factors, [1.0, 1.03, 1.0609])


if __name__ == "__main__":
    unittest.main()
