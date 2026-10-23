import unittest
from unittest.mock import patch

from planner.assumptions import Assumptions
from planner.inflation_engine import InflationEngine
from planner.models import RetirementYear
from planner.monte_carlo_engine import MonteCarloEngine
from planner.state_pension import StatePensionEngine


class TestSprint216InflationVolatility(unittest.TestCase):
    def make_assumptions(self):
        assumptions = Assumptions()
        assumptions.set("current_age", 62)
        assumptions.set("projection_end_age", 64)
        assumptions.set("inflation_rate", 0.025)
        assumptions.set("inflation_volatility", 0.01)
        return assumptions

    def test_deterministic_inflation_remains_unchanged_without_simulated_path(self):
        assumptions = self.make_assumptions()
        timeline = [
            RetirementYear(age=62, calendar_year=2026, spouse_age=59),
            RetirementYear(age=63, calendar_year=2027, spouse_age=60),
            RetirementYear(age=64, calendar_year=2028, spouse_age=61),
        ]
        InflationEngine(assumptions).apply(timeline)
        self.assertEqual([y.inflation_rate for y in timeline], [0.025] * 3)
        self.assertEqual([y.inflation_factor for y in timeline], [1.0, 1.025, 1.050625])

    def test_simulated_path_drives_year_specific_inflation_factor(self):
        assumptions = self.make_assumptions()
        assumptions.data["_monte_carlo_inflation_path"] = [0.01, 0.04, 0.02]
        timeline = [
            RetirementYear(age=62, calendar_year=2026, spouse_age=59),
            RetirementYear(age=63, calendar_year=2027, spouse_age=60),
            RetirementYear(age=64, calendar_year=2028, spouse_age=61),
        ]
        InflationEngine(assumptions).apply(timeline)
        self.assertEqual([y.inflation_rate for y in timeline], [0.01, 0.04, 0.02])
        self.assertEqual([y.inflation_factor for y in timeline], [1.0, 1.01, 1.0504])

    def test_triple_lock_uses_simulated_cpi_path(self):
        assumptions = self.make_assumptions()
        assumptions.set("state_pension_full", 10000.0)
        assumptions.set("state_pension_earnings_growth", 0.02)
        assumptions.set("state_pension_triple_lock_enabled", True)
        assumptions.data["_monte_carlo_inflation_path"] = [0.01, 0.04, 0.02]
        timeline = [
            RetirementYear(age=67, calendar_year=2031, spouse_age=64),
            RetirementYear(age=68, calendar_year=2032, spouse_age=65),
        ]
        InflationEngine(assumptions).apply(timeline)
        StatePensionEngine(assumptions).apply(timeline)
        self.assertEqual(timeline[1].your_state_pension, 10400.0)

    def test_monte_carlo_draws_inflation_path_with_seed(self):
        assumptions = self.make_assumptions()
        assumptions.set("expected_return", 0.04)
        assumptions.set("investment_volatility", 0.10)
        assumptions.set("platform_charge", 0.0)
        assumptions.set("fund_charge", 0.0)
        with patch("planner.monte_carlo_engine.RetirementPlanner") as planner_cls:
            result = type("Result", (), {"summary": {"ending_assets": 100.0}})()
            planner_cls.return_value.run.return_value = result
            MonteCarloEngine(assumptions).run(iterations=1, seed=123)
            path1 = planner_cls.call_args.args[0].data["_monte_carlo_inflation_path"]
            planner_cls.reset_mock()
            MonteCarloEngine(assumptions).run(iterations=1, seed=123)
            path2 = planner_cls.call_args.args[0].data["_monte_carlo_inflation_path"]
        self.assertEqual(path1, path2)
        self.assertEqual(len(path1), 3)

    def test_inflation_volatility_changes_real_monte_carlo_projection(self):
        low = self.make_assumptions()
        high = self.make_assumptions()
        low.set("inflation_volatility", 0.0)
        high.set("inflation_volatility", 0.02)
        low_result = MonteCarloEngine(low).run(iterations=2, seed=123)
        high_result = MonteCarloEngine(high).run(iterations=2, seed=123)
        self.assertNotEqual(low_result.results, high_result.results)

    def test_zero_inflation_volatility_produces_configured_cpi(self):
        assumptions = self.make_assumptions()
        assumptions.set("inflation_volatility", 0.0)
        with patch("planner.monte_carlo_engine.RetirementPlanner") as planner_cls:
            result = type("Result", (), {"summary": {"ending_assets": 100.0}})()
            planner_cls.return_value.run.return_value = result
            MonteCarloEngine(assumptions).run(iterations=1, seed=123)
            path = planner_cls.call_args.args[0].data["_monte_carlo_inflation_path"]
        self.assertEqual(path, [0.025, 0.025, 0.025])


if __name__ == "__main__":
    unittest.main()
