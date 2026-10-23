import logging
import unittest
from types import SimpleNamespace

from planner.recommendation_engine import RecommendationEngine
from planner.validation import ValidationEngine
from planner.scenarios.scenario_comparison import ScenarioComparison


class TestLoggingConsistency(unittest.TestCase):

    def test_recommendation_engine_uses_debug_logging_instead_of_stdout(self):
        comparison = ScenarioComparison(
            name="Base",
            success=True,
            ending_assets=1000000,
            ending_pension=600000,
            ending_isa=250000,
            ending_savings=150000,
            total_tax=100000,
            retirement_age=60,
        )

        with self.assertLogs("planner.recommendation_engine", level="DEBUG") as logs:
            RecommendationEngine().generate([comparison])

        self.assertTrue(
            any("Generating recommendations" in message for message in logs.output)
        )

    def test_validation_engine_uses_warning_logging(self):
        year = SimpleNamespace(
            closing_pension=-1,
            savings_closing=-2,
            isa_closing=-3,
            age=75,
        )

        with self.assertLogs("planner.validation", level="WARNING") as logs:
            ValidationEngine().validate([year])

        self.assertEqual(len(logs.output), 3)
        self.assertTrue(any("Pension below zero at age 75" in m for m in logs.output))
        self.assertTrue(any("Savings below zero at age 75" in m for m in logs.output))
        self.assertTrue(any("ISA below zero at age 75" in m for m in logs.output))


if __name__ == "__main__":
    unittest.main()
