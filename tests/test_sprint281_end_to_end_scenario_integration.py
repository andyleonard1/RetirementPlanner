"""Sprint 281: end-to-end scenario composition across the retirement planner."""
from __future__ import annotations

import math
import unittest

from planner.assumptions import Assumptions
from planner.planner import RetirementPlanner


class Sprint281EndToEndScenarioIntegrationTests(unittest.TestCase):
    @staticmethod
    def run_scenario(**changes):
        assumptions = Assumptions()
        for key, value in changes.items():
            assumptions.set(key, value)
        return RetirementPlanner(assumptions).run()

    def test_default_scenario_produces_complete_contiguous_timeline(self):
        result = self.run_scenario()
        self.assertTrue(result.timeline)
        years = [year.calendar_year for year in result.timeline]
        self.assertEqual(years, list(range(years[0], years[0] + len(years))))
        self.assertTrue(all(year.age >= 0 for year in result.timeline))

    def test_repeated_default_scenarios_are_deterministic(self):
        first = self.run_scenario()
        second = self.run_scenario()
        self.assertEqual(len(first.timeline), len(second.timeline))
        for a, b in zip(first.timeline, second.timeline):
            for field in ("target_spending", "required_pension_income", "closing_pension", "isa_closing", "savings_closing"):
                self.assertAlmostEqual(getattr(a, field), getattr(b, field), places=2, msg=f"{field} at {a.calendar_year}")

    def test_higher_inflation_flows_through_future_spending_and_funding(self):
        baseline = self.run_scenario()
        higher = self.run_scenario(inflation_rate=0.05)
        year = baseline.timeline[5].calendar_year
        base_row = next(row for row in baseline.timeline if row.calendar_year == year)
        high_row = next(row for row in higher.timeline if row.calendar_year == year)
        self.assertGreater(high_row.target_spending, base_row.target_spending)
        self.assertNotEqual(high_row.required_pension_income, base_row.required_pension_income)

    def test_state_pension_policy_toggle_changes_full_projection(self):
        locked = self.run_scenario(state_pension_triple_lock_enabled=True)
        legacy = self.run_scenario(state_pension_triple_lock_enabled=False)
        locked_rows = {row.calendar_year: row for row in locked.timeline}
        legacy_rows = {row.calendar_year: row for row in legacy.timeline}
        common_years = sorted(set(locked_rows) & set(legacy_rows))
        self.assertTrue(any(
            abs(locked_rows[year].your_state_pension - legacy_rows[year].your_state_pension) > 0.01
            for year in common_years
        ))

    def test_isa_inflation_link_is_opt_in_across_full_projection(self):
        nominal = self.run_scenario(inflation_link_isa=False)
        linked = self.run_scenario(inflation_link_isa=True)
        self.assertEqual(len(nominal.timeline), len(linked.timeline))
        self.assertTrue(any(
            abs(a.isa_closing - b.isa_closing) > 0.01
            for a, b in zip(nominal.timeline, linked.timeline)
        ))

    def test_projection_financial_outputs_are_finite(self):
        result = self.run_scenario()
        fields = ("target_spending", "required_pension_income", "closing_pension", "isa_closing", "savings_closing", "total_assets")
        for row in result.timeline:
            for field in fields:
                value = getattr(row, field)
                self.assertTrue(math.isfinite(float(value)), f"{field} is not finite in {row.calendar_year}")

    def test_scenario_runs_do_not_mutate_the_shipped_assumptions_file(self):
        from pathlib import Path
        assumptions_path = Path(__file__).resolve().parents[1] / "data" / "assumptions.json"
        before = assumptions_path.read_bytes()
        self.run_scenario(inflation_rate=0.05, state_pension_triple_lock_enabled=False)
        self.assertEqual(assumptions_path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
