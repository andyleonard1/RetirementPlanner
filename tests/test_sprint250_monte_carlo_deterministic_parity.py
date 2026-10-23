import unittest
from unittest.mock import patch

from planner.assumptions import Assumptions
from planner.assumption_resolver import AssumptionResolver
from planner.investment_return import InvestmentReturnResolver
from planner.monte_carlo_engine import MonteCarloEngine
from planner.planner import RetirementPlanner


class Sprint250MonteCarloDeterministicParityTests(unittest.TestCase):
    """Protect the explicit deterministic/Monte Carlo return boundary."""

    def _assumptions(self):
        a = Assumptions()
        values = {
            "current_age": 65,
            "retirement_age": 65,
            "projection_end_age": 67,
            "current_calendar_year": 2026,
            "starting_pension": 100000.0,
            "starting_savings": 0.0,
            "starting_isa": 0.0,
            "property_sale": 0.0,
            "state_pension_full": 0.0,
            "max_pension_income": 0.0,
            "spending_phase_1": 0.0,
            "spending_phase_2": 0.0,
            "spending_phase_3": 0.0,
            "phase_1_end_age": 67,
            "phase_2_end_age": 68,
            "expected_investment_return": 0.06,
            "expected_return": 0.03,
            "pension_growth": 0.08,
            "investment_volatility": 0.0,
            "platform_charge": 0.01,
            "fund_charge": 0.005,
        }
        for key, value in values.items():
            a.set(key, value)
        return a

    def test_deterministic_return_uses_expected_investment_return(self):
        a = self._assumptions()
        config = InvestmentReturnResolver.resolve(a)
        self.assertEqual(config.gross_projection_return, 0.06)
        self.assertAlmostEqual(config.net_projection_return, 0.045)

    def test_monte_carlo_return_uses_expected_return_first(self):
        a = self._assumptions()
        self.assertEqual(AssumptionResolver(a).monte_carlo_expected_return(), 0.03)
        config = InvestmentReturnResolver.resolve(a)
        self.assertAlmostEqual(config.net_monte_carlo_expected_return, 0.015)

    def test_charges_are_applied_once_to_both_return_boundaries(self):
        a = self._assumptions()
        config = InvestmentReturnResolver.resolve(a)
        self.assertAlmostEqual(config.net_projection_return, 0.06 - 0.015)
        self.assertAlmostEqual(config.net_monte_carlo_expected_return, 0.03 - 0.015)

    def test_deterministic_projection_is_independent_of_monte_carlo_mean(self):
        first = self._assumptions()
        second = self._assumptions()
        second.set("expected_return", 0.20)
        r1 = RetirementPlanner(first, audit_context="sprint250").run()
        r2 = RetirementPlanner(second, audit_context="sprint250").run()
        self.assertEqual(r1.summary, r2.summary)
        self.assertEqual(
            [y.pension_growth for y in r1.timeline],
            [y.pension_growth for y in r2.timeline],
        )

    def test_monte_carlo_is_independent_of_deterministic_projection_mean(self):
        a = self._assumptions()
        with patch("planner.monte_carlo_engine.RetirementPlanner") as planner_cls:
            planner_cls.return_value.run.return_value = type(
                "Result", (), {"summary": {"ending_assets": 100.0}}
            )()
            MonteCarloEngine(a).run(iterations=3, seed=42)
            first = [
                c.args[0].data["expected_investment_return"]
                for c in planner_cls.call_args_list
            ]
            planner_cls.reset_mock()
            a.set("expected_investment_return", 0.20)
            MonteCarloEngine(a).run(iterations=3, seed=42)
            second = [
                c.args[0].data["expected_investment_return"]
                for c in planner_cls.call_args_list
            ]
        self.assertEqual(first, second)

    def test_seeded_zero_volatility_monte_carlo_injects_net_mean_as_gross_plus_charges(self):
        a = self._assumptions()
        with patch("planner.monte_carlo_engine.RetirementPlanner") as planner_cls:
            planner_cls.return_value.run.return_value = type(
                "Result", (), {"summary": {"ending_assets": 100.0}}
            )()
            MonteCarloEngine(a).run(iterations=1, seed=7)
            generated = planner_cls.call_args[0][0]
        # MC mean = 3%; net after charges = 1.5%; equivalent gross = 3%.
        self.assertAlmostEqual(generated.data["pension_growth"], 0.015)
        self.assertAlmostEqual(generated.data["expected_investment_return"], 0.03)

    def test_monte_carlo_precedence_falls_back_to_deterministic_return(self):
        a = self._assumptions()
        a.set("expected_return", None)
        self.assertEqual(AssumptionResolver(a).monte_carlo_expected_return(), 0.06)

    def test_monte_carlo_precedence_falls_back_to_legacy_pension_growth(self):
        a = self._assumptions()
        a.set("expected_return", None)
        a.set("expected_investment_return", None)
        self.assertEqual(AssumptionResolver(a).monte_carlo_expected_return(), 0.08)

    def test_conflicting_return_assumptions_remain_distinct(self):
        a = self._assumptions()
        resolver = AssumptionResolver(a)
        self.assertEqual(resolver.expected_investment_return(), 0.06)
        self.assertEqual(resolver.monte_carlo_expected_return(), 0.03)

    def test_seeded_monte_carlo_is_repeatable_at_the_return_boundary(self):
        a = self._assumptions()
        captured = []
        with patch("planner.monte_carlo_engine.RetirementPlanner") as planner_cls:
            planner_cls.return_value.run.return_value = type(
                "Result", (), {"summary": {"ending_assets": 100.0}}
            )()
            MonteCarloEngine(a).run(iterations=5, seed=99)
            captured.append([
                c.args[0].data["pension_growth"] for c in planner_cls.call_args_list
            ])
            planner_cls.reset_mock()
            MonteCarloEngine(a).run(iterations=5, seed=99)
            captured.append([
                c.args[0].data["pension_growth"] for c in planner_cls.call_args_list
            ])
        self.assertEqual(captured[0], captured[1])


if __name__ == "__main__":
    unittest.main()
