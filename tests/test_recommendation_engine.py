import unittest

from planner.recommendations.recommendation_engine import (
    RecommendationEngine,
)

from planner.scenarios.scenario_comparison import (
    ScenarioComparison,
)

from planner.scenarios.retirement_age_tradeoff import (
    RetirementAgeTradeoff,
)


class TestRecommendationEngine(unittest.TestCase):

    # -------------------------------------------------

    def test_engine_can_be_created(self):

        engine = RecommendationEngine()

        self.assertIsNotNone(
            engine
        )

    # -------------------------------------------------

    def test_empty_comparison_returns_no_recommendations(self):

        engine = RecommendationEngine()

        recommendations = engine.generate([])

        self.assertEqual(
            len(recommendations),
            0,
        )

    # -------------------------------------------------

    def test_successful_plan_generates_recommendation(self):

        comparison = ScenarioComparison(
            name="Base",
            success=True,
            ending_assets=1200000,
            ending_pension=650000,
            ending_isa=300000,
            ending_savings=250000,
            total_tax=185000,
            retirement_age=60,
        )

        engine = RecommendationEngine()

        recommendations = engine.generate(
            [comparison]
        )

        self.assertGreater(
            len(recommendations),
            0,
        )

    # -------------------------------------------------

    def test_unsuccessful_plan_generates_recommendation(self):

        comparison = ScenarioComparison(
            name="Base",
            success=False,
            ending_assets=0,
            ending_pension=0,
            ending_isa=0,
            ending_savings=0,
            total_tax=0,
            retirement_age=58,
        )

        engine = RecommendationEngine()

        recommendations = engine.generate(
            [comparison]
        )

        self.assertGreater(
            len(recommendations),
            0,
        )

    # -------------------------------------------------

    def test_no_successful_plan_returns_no_age_recommendation(self):

        comparisons = [
            ScenarioComparison(
                name="Age 58",
                success=False,
                ending_assets=0,
                ending_pension=0,
                ending_isa=0,
                ending_savings=0,
                total_tax=0,
                retirement_age=58,
            ),
        ]

        engine = RecommendationEngine()

        recommendations = engine.generate(
            comparisons
        )

        age_recommendations = [
            recommendation
            for recommendation in recommendations
            if recommendation.title
            == "Recommended Retirement Age"
        ]

        self.assertEqual(
            len(age_recommendations),
            0,
        )

    # -------------------------------------------------

    def test_earliest_successful_age_is_selected(self):

        comparisons = [

            ScenarioComparison(
                name="Age 58",
                success=False,
                ending_assets=0,
                ending_pension=0,
                ending_isa=0,
                ending_savings=0,
                total_tax=0,
                retirement_age=58,
            ),

            ScenarioComparison(
                name="Age 60",
                success=True,
                ending_assets=900000,
                ending_pension=500000,
                ending_isa=250000,
                ending_savings=150000,
                total_tax=100000,
                retirement_age=60,
            ),

            ScenarioComparison(
                name="Age 62",
                success=True,
                ending_assets=1100000,
                ending_pension=650000,
                ending_isa=300000,
                ending_savings=150000,
                total_tax=120000,
                retirement_age=62,
            ),
        ]

        engine = RecommendationEngine()

        recommendations = engine.generate(
            comparisons
        )

        self.assertEqual(
            recommendations[0].title,
            "Recommended Retirement Age",
        )

        self.assertIn(
            "60",
            recommendations[0].message,
        )

    # -------------------------------------------------

    def test_earliest_successful_age_ignores_later_failure(self):

        comparisons = [

            ScenarioComparison(
                name="Age 60",
                success=True,
                ending_assets=900000,
                ending_pension=500000,
                ending_isa=250000,
                ending_savings=150000,
                total_tax=100000,
                retirement_age=60,
            ),

            ScenarioComparison(
                name="Age 61",
                success=False,
                ending_assets=0,
                ending_pension=0,
                ending_isa=0,
                ending_savings=0,
                total_tax=0,
                retirement_age=61,
            ),
        ]

        engine = RecommendationEngine()

        recommendations = engine.generate(
            comparisons
        )

        self.assertEqual(
            recommendations[0].title,
            "Recommended Retirement Age",
        )

        self.assertIn(
            "60",
            recommendations[0].message,
        )

    # -------------------------------------------------

    def test_waiting_one_year_generates_comparison(self):

        comparisons = [

            ScenarioComparison(
                name="Age 60",
                success=True,
                ending_assets=900000,
                ending_pension=500000,
                ending_isa=250000,
                ending_savings=150000,
                total_tax=100000,
                retirement_age=60,
            ),

            ScenarioComparison(
                name="Age 61",
                success=True,
                ending_assets=950000,
                ending_pension=540000,
                ending_isa=260000,
                ending_savings=150000,
                total_tax=105000,
                retirement_age=61,
            ),
        ]

        engine = RecommendationEngine()

        recommendations = engine.generate(
            comparisons
        )

        waiting = [
            recommendation
            for recommendation in recommendations
            if recommendation.title
            == "Benefit of Waiting One Year"
        ]

        self.assertEqual(
            len(waiting),
            1,
        )

        self.assertIn(
            "£50,000",
            waiting[0].impact,
        )

    # -------------------------------------------------

    def test_waiting_one_year_requires_next_age_scenario(self):

        comparisons = [

            ScenarioComparison(
                name="Age 60",
                success=True,
                ending_assets=900000,
                ending_pension=500000,
                ending_isa=250000,
                ending_savings=150000,
                total_tax=100000,
                retirement_age=60,
            ),

            ScenarioComparison(
                name="Age 62",
                success=True,
                ending_assets=1000000,
                ending_pension=600000,
                ending_isa=250000,
                ending_savings=150000,
                total_tax=110000,
                retirement_age=62,
            ),
        ]

        engine = RecommendationEngine()

        recommendations = engine.generate(
            comparisons
        )

        waiting = [
            recommendation
            for recommendation in recommendations
            if recommendation.title
            == "Benefit of Waiting One Year"
        ]

        self.assertEqual(
            len(waiting),
            0,
        )

    # -------------------------------------------------

    def test_retirement_age_tradeoff_generates_recommendation(self):

        comparisons = [

            ScenarioComparison(
                name="Age 60",
                success=True,
                ending_assets=900000,
                ending_pension=500000,
                ending_isa=250000,
                ending_savings=150000,
                total_tax=100000,
                retirement_age=60,
            ),

            ScenarioComparison(
                name="Age 62",
                success=True,
                ending_assets=1000000,
                ending_pension=550000,
                ending_isa=280000,
                ending_savings=170000,
                total_tax=105000,
                retirement_age=62,
            ),
        ]

        tradeoffs = [
            RetirementAgeTradeoff(
                starting_age=60,
                later_age=62,
                years_waited=2,
                starting_assets=900000,
                later_assets=1000000,
                additional_assets=100000,
                additional_assets_per_year=50000,
                later_success=True,
            )
        ]

        recommendations = RecommendationEngine().generate(
            comparisons,
            tradeoffs,
        )

        tradeoff_recommendations = [
            recommendation
            for recommendation in recommendations
            if recommendation.title
            == "Retirement Age Trade-off"
        ]

        self.assertEqual(
            len(tradeoff_recommendations),
            1,
        )

        self.assertIn(
            "62",
            tradeoff_recommendations[0].message,
        )

        self.assertIn(
            "£100,000",
            tradeoff_recommendations[0].impact,
        )

    # -------------------------------------------------

    def test_retirement_age_tradeoff_ignores_later_failure(self):

        comparisons = [

            ScenarioComparison(
                name="Age 60",
                success=True,
                ending_assets=900000,
                ending_pension=500000,
                ending_isa=250000,
                ending_savings=150000,
                total_tax=100000,
                retirement_age=60,
            ),
        ]

        tradeoffs = [
            RetirementAgeTradeoff(
                starting_age=60,
                later_age=61,
                years_waited=1,
                starting_assets=900000,
                later_assets=1200000,
                additional_assets=300000,
                additional_assets_per_year=300000,
                later_success=False,
            )
        ]

        recommendations = RecommendationEngine().generate(
            comparisons,
            tradeoffs,
        )

        tradeoff_recommendations = [
            recommendation
            for recommendation in recommendations
            if recommendation.title
            == "Retirement Age Trade-off"
        ]

        self.assertEqual(
            len(tradeoff_recommendations),
            0,
        )

if __name__ == "__main__":
    unittest.main()

# -------------------------------------------------

class TestRecommendationEngineFinancialAge(unittest.TestCase):

    def test_highest_ending_assets_successful_age_generates_recommendation(self):

        comparisons = [
            ScenarioComparison(
                name="Age 60",
                success=True,
                ending_assets=900000,
                ending_pension=500000,
                ending_isa=250000,
                ending_savings=150000,
                total_tax=100000,
                retirement_age=60,
            ),
            ScenarioComparison(
                name="Age 61",
                success=True,
                ending_assets=1000000,
                ending_pension=550000,
                ending_isa=280000,
                ending_savings=170000,
                total_tax=105000,
                retirement_age=61,
            ),
            ScenarioComparison(
                name="Age 62",
                success=True,
                ending_assets=950000,
                ending_pension=520000,
                ending_isa=270000,
                ending_savings=160000,
                total_tax=110000,
                retirement_age=62,
            ),
        ]

        recommendations = RecommendationEngine().generate(comparisons)

        strongest = [
            recommendation
            for recommendation in recommendations
            if recommendation.title
            == "Highest Projected Ending Assets"
        ]

        self.assertEqual(len(strongest), 1)
        self.assertIn("61", strongest[0].message)
        self.assertIn("£1,000,000", strongest[0].impact)

    def test_highest_ending_assets_ignores_unsuccessful_scenario(self):

        comparisons = [
            ScenarioComparison(
                name="Age 60",
                success=True,
                ending_assets=900000,
                ending_pension=500000,
                ending_isa=250000,
                ending_savings=150000,
                total_tax=100000,
                retirement_age=60,
            ),
            ScenarioComparison(
                name="Age 61",
                success=False,
                ending_assets=2000000,
                ending_pension=1200000,
                ending_isa=500000,
                ending_savings=300000,
                total_tax=100000,
                retirement_age=61,
            ),
        ]

        recommendations = RecommendationEngine().generate(comparisons)

        strongest = [
            recommendation
            for recommendation in recommendations
            if recommendation.title
            == "Highest Projected Ending Assets"
        ]

        self.assertEqual(len(strongest), 0)
