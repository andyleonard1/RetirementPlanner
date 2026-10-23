import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from planner.assumptions import Assumptions
from planner.recommendations.recommendation_engine import RecommendationEngine
from planner.services.retirement_solver import RetirementSolver


class TestFailureResilience(unittest.TestCase):

    def test_missing_assumptions_file_fails_clearly(self):
        with self.assertRaisesRegex(FileNotFoundError, "Cannot find assumptions file"):
            Assumptions("missing-assumptions.json")

    def test_invalid_assumptions_json_fails_clearly(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "assumptions.json"
            path.write_text("{not valid json", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Invalid JSON"):
                Assumptions(str(path))

    def test_missing_required_numeric_assumption_fails_with_value_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path("data/assumptions.json")
            data = json.loads(source.read_text(encoding="utf-8"))
            data.pop("current_age")
            path = Path(tmp) / "assumptions.json"
            path.write_text(json.dumps(data), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Missing required assumptions: current_age"):
                Assumptions(str(path))

    def test_non_numeric_assumption_fails_with_value_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path("data/assumptions.json")
            data = json.loads(source.read_text(encoding="utf-8"))
            data["expected_investment_return"] = "4.75%"
            path = Path(tmp) / "assumptions.json"
            path.write_text(json.dumps(data), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "expected_investment_return must be a finite number"):
                Assumptions(str(path))

    def test_non_finite_assumption_fails_with_value_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path("data/assumptions.json")
            data = json.loads(source.read_text(encoding="utf-8"))
            data["investment_volatility"] = float("nan")
            path = Path(tmp) / "assumptions.json"
            path.write_text(json.dumps(data), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "investment_volatility must be a finite number"):
                Assumptions(str(path))

    def test_solver_returns_none_when_no_scenario_succeeds(self):
        solver = RetirementSolver(Assumptions())
        failed = type("FailedResult", (), {"success": False})()

        with patch.object(solver, "_run_at_age", return_value=failed):
            self.assertIsNone(solver.find_earliest_age(55, 57))

    def test_empty_recommendation_input_is_safe(self):
        self.assertEqual(RecommendationEngine().generate([]), [])


if __name__ == "__main__":
    unittest.main()
