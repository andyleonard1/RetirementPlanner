import unittest
from types import SimpleNamespace

from planner.recommendations.recommendation_quality import RecommendationQualityEngine


class TestRecommendationQuality(unittest.TestCase):
    def decision(self, age=56, score=82.5):
        return SimpleNamespace(recommended_age=age, total_score=score)

    def optimisation(self, policy="basic_rate_band", material=True, maximum_age=56):
        return SimpleNamespace(
            higher_policy=policy,
            material=material,
            maximum_difference_age=maximum_age,
            explanation="Average difference is £3,000 per year; largest difference is £5,000 at age 56.",
            recommendation="basic_rate_band provides materially greater tax-efficient pension capacity.",
        )

    def test_combines_age_and_material_policy(self):
        result = RecommendationQualityEngine().build(self.decision(), self.optimisation())
        self.assertEqual(result.priority, 0)
        self.assertEqual(result.title, "Overall Retirement Strategy")
        self.assertIn("age 56", result.message)
        self.assertIn("basic_rate_band", result.message)
        self.assertIn("82.5/100", result.impact)

    def test_non_material_policy_is_not_overstated(self):
        result = RecommendationQualityEngine().build(self.decision(), self.optimisation(material=False))
        self.assertIn("not material", result.message)

    def test_equal_policies_are_described_as_equivalent(self):
        result = RecommendationQualityEngine().build(
            self.decision(), self.optimisation(policy=None, material=False)
        )
        self.assertIn("effectively equivalent", result.message)

    def test_missing_retirement_decision_is_safe(self):
        result = RecommendationQualityEngine().build(None, self.optimisation())
        self.assertIn("No reliable retirement-age decision", result.message)
        self.assertIn("basic_rate_band", result.impact)

    def test_invalid_retirement_age_does_not_create_a_recommendation(self):
        result = RecommendationQualityEngine().build(
            SimpleNamespace(recommended_age=None, total_score=90), self.optimisation()
        )
        self.assertIn("No reliable retirement-age decision", result.message)

    def test_missing_optimisation_decision_is_safe(self):
        result = RecommendationQualityEngine().build(self.decision(), None)
        self.assertIn("Retire at age 56", result.message)
        self.assertIn("No optimisation", result.impact)

    def test_missing_score_is_safe(self):
        result = RecommendationQualityEngine().build(
            SimpleNamespace(recommended_age=56, total_score=None), self.optimisation()
        )
        self.assertIn("score is unavailable", result.impact)

    def test_policy_advantage_at_different_age_is_explicitly_qualified(self):
        result = RecommendationQualityEngine().build(
            self.decision(age=56), self.optimisation(maximum_age=63)
        )
        self.assertIn("largest at age 63", result.message)
        self.assertIn("does not change the selected retirement age", result.message)

    def test_missing_optimisation_fields_are_safe(self):
        result = RecommendationQualityEngine().build(
            self.decision(), SimpleNamespace(higher_policy=None, material=False)
        )
        self.assertIn("effectively equivalent", result.message)

    def test_non_object_optimisation_is_safe(self):
        result = RecommendationQualityEngine().build(self.decision(), object())
        self.assertIn("No optimisation policy advantage", result.message)

    def test_no_decisions_is_conservative(self):
        result = RecommendationQualityEngine().build(None, None)
        self.assertIn("No reliable retirement-age decision", result.message)
        self.assertIn("No optimisation decision", result.impact)

    def test_recommendation_is_read_only(self):
        decision = self.decision()
        optimisation = self.optimisation()
        RecommendationQualityEngine().build(decision, optimisation)
        self.assertEqual(decision.recommended_age, 56)
        self.assertEqual(optimisation.higher_policy, "basic_rate_band")


if __name__ == "__main__":
    unittest.main()
