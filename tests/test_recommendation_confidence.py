import unittest

from planner.recommendations.recommendation_confidence import (
    RecommendationConfidenceEngine,
)


class Decision:
    def __init__(self, score):
        self.total_score = score


class Score:
    def __init__(self, score, success=True):
        self.total_score = score
        self.success = success


class TestRecommendationConfidence(unittest.TestCase):

    def test_missing_decision_is_low(self):
        result = RecommendationConfidenceEngine().analyse()
        self.assertEqual(result.level, "LOW")

    def test_strong_clear_decision_is_high(self):
        result = RecommendationConfidenceEngine().analyse(
            decision=Decision(95),
            scores=[Score(95), Score(80)],
            optimisation_material=False,
            risk_score=2,
        )
        self.assertEqual(result.level, "HIGH")

    def test_close_scores_reduce_confidence(self):
        result = RecommendationConfidenceEngine().analyse(
            decision=Decision(75),
            scores=[Score(75), Score(74)],
            optimisation_material=False,
            risk_score=4,
        )
        self.assertIn(result.level, {"MEDIUM", "LOW"})

    def test_material_optimisation_tradeoff_reduces_confidence(self):
        result = RecommendationConfidenceEngine().analyse(
            decision=Decision(90),
            scores=[Score(90), Score(80)],
            optimisation_material=True,
            risk_score=3,
        )
        self.assertLess(result.score, 100)

    def test_high_risk_reduces_confidence(self):
        result = RecommendationConfidenceEngine().analyse(
            decision=Decision(90),
            scores=[Score(90)],
            optimisation_material=False,
            risk_score=8,
        )
        self.assertLess(result.score, 100)

    def test_reasons_are_exposed(self):
        result = RecommendationConfidenceEngine().analyse(
            decision=Decision(80),
            scores=[Score(80), Score(70)],
        )
        self.assertTrue(result.reasons)


if __name__ == "__main__":
    unittest.main()
