"""Sprint 283: deterministic and Monte Carlo boundary/parity regressions."""
from __future__ import annotations

import copy
import math
import unittest

from planner.assumptions import Assumptions
from planner.monte_carlo_engine import MonteCarloEngine
from planner.planner import RetirementPlanner


class Sprint283DeterministicMonteCarloParityTests(unittest.TestCase):
    @staticmethod
    def make_assumptions(**changes):
        assumptions = Assumptions()
        values = {
            "current_age": 65,
            "retirement_age": 65,
            "projection_end_age": 68,
            "current_calendar_year": 2026,
            "starting_pension": 100000.0,
            "starting_savings": 5000.0,
            "starting_isa": 10000.0,
            "property_sale": 0.0,
            "state_pension_full": 0.0,
            "max_pension_income": 0.0,
            "spending_phase_1": 0.0,
            "spending_phase_2": 0.0,
            "spending_phase_3": 0.0,
            "phase_1_end_age": 67,
            "phase_2_end_age": 68,
            "expected_investment_return": 0.06,
            "expected_return": 0.06,
            "pension_growth": 0.06,
            "investment_volatility": 0.0,
            "inflation_rate": 0.0,
            "inflation_volatility": 0.0,
            "platform_charge": 0.01,
            "fund_charge": 0.005,
        }
        values.update(changes)
        for key, value in values.items():
            assumptions.set(key, value)
        return assumptions

    def test_zero_volatility_monte_carlo_matches_deterministic_ending_assets(self):
        assumptions = self.make_assumptions()
        deterministic = RetirementPlanner(assumptions, audit_context="sprint283").run()
        simulated = MonteCarloEngine(assumptions).run(iterations=1, seed=283)
        self.assertAlmostEqual(
            deterministic.summary["ending_assets"], simulated.median, places=2
        )
        self.assertEqual(simulated.minimum, simulated.maximum)
        self.assertEqual(simulated.success_rate, 100.0)

    def test_seeded_monte_carlo_is_repeatable_for_full_projection_results(self):
        assumptions = self.make_assumptions(
            investment_volatility=0.12,
            inflation_rate=0.025,
            inflation_volatility=0.01,
        )
        first = MonteCarloEngine(assumptions).run(iterations=20, seed=283)
        second = MonteCarloEngine(assumptions).run(iterations=20, seed=283)
        self.assertEqual(first.results, second.results)
        self.assertEqual(first.success_rate, second.success_rate)

    def test_percentiles_and_success_rate_are_consistent(self):
        result = MonteCarloEngine(
            self.make_assumptions(investment_volatility=0.15, inflation_volatility=0.01)
        ).run(iterations=30, seed=284)
        self.assertEqual(result.results, sorted(result.results))
        self.assertLessEqual(result.minimum, result.percentile_5)
        self.assertLessEqual(result.percentile_5, result.median)
        self.assertLessEqual(result.median, result.percentile_95)
        self.assertLessEqual(result.percentile_95, result.maximum)
        self.assertGreaterEqual(result.success_rate, 0.0)
        self.assertLessEqual(result.success_rate, 100.0)
        for value in (result.minimum, result.percentile_5, result.median,
                      result.percentile_95, result.maximum, result.success_rate):
            self.assertTrue(math.isfinite(float(value)))

    def test_different_seeds_change_results_when_volatility_is_nonzero(self):
        assumptions = self.make_assumptions(investment_volatility=0.15)
        first = MonteCarloEngine(assumptions).run(iterations=12, seed=1)
        second = MonteCarloEngine(assumptions).run(iterations=12, seed=2)
        self.assertNotEqual(first.results, second.results)

    def test_monte_carlo_does_not_mutate_original_assumptions(self):
        assumptions = self.make_assumptions(
            investment_volatility=0.1, inflation_volatility=0.01
        )
        before = copy.deepcopy(assumptions.data)
        MonteCarloEngine(assumptions).run(iterations=5, seed=283)
        self.assertEqual(assumptions.data, before)


if __name__ == "__main__":
    unittest.main()
