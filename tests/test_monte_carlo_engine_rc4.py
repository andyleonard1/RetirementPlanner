import unittest
from unittest.mock import patch

from planner.monte_carlo_engine import MonteCarloEngine


class MonteCarloEngineRC4Tests(unittest.TestCase):
    def _assumptions(self):
        data = {
            "expected_return": 0.04,
            "investment_volatility": 0.10,
            "pension_growth": 0.04,
        }
        return type("AssumptionsStub", (), {"data": data, "get": data.get})()

    def test_iterations_must_be_positive(self):
        with self.assertRaisesRegex(ValueError, "iterations must be greater than zero"):
            MonteCarloEngine(self._assumptions()).run(iterations=0, seed=1)

    def test_seed_makes_random_draws_reproducible(self):
        with patch("planner.monte_carlo_engine.RetirementPlanner") as planner_cls:
            result = type("Result", (), {"summary": {"ending_assets": 100.0}})()
            planner_cls.return_value.run.return_value = result
            engine = MonteCarloEngine(self._assumptions())
            engine.run(iterations=4, seed=123)
            first_values = [call.args[0].data["pension_growth"] for call in planner_cls.call_args_list]
            planner_cls.reset_mock()
            engine.run(iterations=4, seed=123)
            second_values = [call.args[0].data["pension_growth"] for call in planner_cls.call_args_list]
        self.assertEqual(first_values, second_values)

    def test_different_seeds_change_random_draws(self):
        with patch("planner.monte_carlo_engine.RetirementPlanner") as planner_cls:
            result = type("Result", (), {"summary": {"ending_assets": 100.0}})()
            planner_cls.return_value.run.return_value = result
            engine = MonteCarloEngine(self._assumptions())
            engine.run(iterations=4, seed=1)
            first = [c.args[0].data["pension_growth"] for c in planner_cls.call_args_list]
            planner_cls.reset_mock()
            engine.run(iterations=4, seed=2)
            second = [c.args[0].data["pension_growth"] for c in planner_cls.call_args_list]
        self.assertNotEqual(first, second)

    def test_seeded_run_does_not_use_module_global_gauss(self):
        with patch("planner.monte_carlo_engine.random.gauss", side_effect=AssertionError("global RNG used")):
            with patch("planner.monte_carlo_engine.RetirementPlanner") as planner_cls:
                result = type("Result", (), {"summary": {"ending_assets": 100.0}})()
                planner_cls.return_value.run.return_value = result
                MonteCarloEngine(self._assumptions()).run(iterations=2, seed=7)


if __name__ == "__main__":
    unittest.main()
