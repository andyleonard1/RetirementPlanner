import unittest

from planner.results import (
    DecisionResult,
    HistogramResult,
    RiskResult,
    ScenarioResult,
)
from planner.scenario_engine import ScenarioEngine
from planner.risk_engine import RiskEngine
from planner.histogram_engine import HistogramEngine
from planner.decision_engine import DecisionEngine


class TestResultObjects(unittest.TestCase):

    def test_scenario_engine_returns_scenario_result(self):
        result = ScenarioEngine().run("Base")

        self.assertIsInstance(result, ScenarioResult)
        self.assertIs(result.timeline, result["timeline"])
        self.assertEqual(result.name, "Base")

    def test_risk_engine_returns_risk_result(self):
        scenario = ScenarioEngine().run("Base")
        result = RiskEngine().analyse(scenario.timeline)

        self.assertIsInstance(result, RiskResult)
        self.assertEqual(result.score, result["score"])
        self.assertEqual(result.rating, result["rating"])

    def test_decision_engine_returns_decision_result(self):
        result = DecisionEngine().run()

        self.assertIsInstance(result, DecisionResult)
        self.assertEqual(result.recommended, result["recommended"])
        self.assertIsInstance(result.risk, RiskResult)
        self.assertTrue(result.all)

    def test_histogram_engine_returns_histogram_result(self):
        result = HistogramEngine().build([100, 100, 100])

        self.assertIsInstance(result, HistogramResult)
        self.assertEqual(result.labels, result["labels"])
        self.assertEqual(result.counts, [3])


if __name__ == "__main__":
    unittest.main()
