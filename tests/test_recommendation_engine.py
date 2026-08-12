import unittest
from planner.recommendations.recommendation_sensitivity import RecommendationSensitivityEngine
from planner.recommendations.assumption_sensitivity import AssumptionSensitivityEngine
from planner.recommendations.sensitivity_grid import SensitivityCase, SensitivityGrid
from planner.recommendations.sensitivity_runner import SensitivityRunner
from planner.recommendations.sensitivity_driver_analysis import SensitivityDriverAnalysis

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

    def test_scored_recommendation_selects_best_sustainable_age(self):

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
            "62",
            recommendations[0].message,
        )

        self.assertIn(
            "earliest sustainable age: 60",
            recommendations[0].impact,
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

    def test_scored_retirement_age_can_select_later_successful_age(self):

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
                ending_assets=1200000,
                ending_pension=650000,
                ending_isa=350000,
                ending_savings=200000,
                total_tax=110000,
                retirement_age=62,
            ),
            ScenarioComparison(
                name="Age 64",
                success=True,
                ending_assets=1100000,
                ending_pension=600000,
                ending_isa=320000,
                ending_savings=180000,
                total_tax=115000,
                retirement_age=64,
            ),
        ]

        recommendations = RecommendationEngine().generate(
            comparisons
        )

        self.assertEqual(
            recommendations[0].title,
            "Recommended Retirement Age",
        )

        self.assertIn(
            "62",
            recommendations[0].message,
        )

    # -------------------------------------------------

    def test_scored_retirement_age_never_selects_unsuccessful_age(self):

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
                success=False,
                ending_assets=2000000,
                ending_pension=1200000,
                ending_isa=500000,
                ending_savings=300000,
                total_tax=110000,
                retirement_age=62,
            ),
        ]

        recommendations = RecommendationEngine().generate(
            comparisons
        )

        self.assertIn(
            "60",
            recommendations[0].message,
        )

    # -------------------------------------------------
    # -------------------------------------------------

    def test_scored_recommendation_explains_score_components(self):

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

        recommendations = RecommendationEngine().generate(comparisons)

        recommendation = recommendations[0]

        self.assertEqual(
            recommendation.title,
            "Recommended Retirement Age",
        )

        self.assertIn(
            "score components",
            recommendation.impact,
        )

        self.assertIn(
            "earliest age",
            recommendation.impact,
        )

        self.assertIn(
            "ending assets",
            recommendation.impact,
        )

        self.assertIn(
            "waiting efficiency",
            recommendation.impact,
        )



    def test_only_one_sustainable_age_is_recommended(self):

        comparisons = [
            ScenarioComparison(
                name="Age 60",
                success=False,
                ending_assets=1500000,
                ending_pension=800000,
                ending_isa=450000,
                ending_savings=250000,
                total_tax=100000,
                retirement_age=60,
            ),
            ScenarioComparison(
                name="Age 61",
                success=True,
                ending_assets=1000000,
                ending_pension=600000,
                ending_isa=250000,
                ending_savings=150000,
                total_tax=100000,
                retirement_age=61,
            ),
            ScenarioComparison(
                name="Age 62",
                success=False,
                ending_assets=1800000,
                ending_pension=1000000,
                ending_isa=500000,
                ending_savings=300000,
                total_tax=120000,
                retirement_age=62,
            ),
        ]

        recommendations = RecommendationEngine().generate(comparisons)

        self.assertEqual(
            recommendations[0].title,
            "Recommended Retirement Age",
        )
        self.assertIn("61", recommendations[0].message)

    def test_similar_scores_use_lower_age_as_deterministic_tiebreaker(self):

        comparisons = [
            ScenarioComparison(
                name="Age 60",
                success=True,
                ending_assets=1000000,
                ending_pension=600000,
                ending_isa=250000,
                ending_savings=150000,
                total_tax=100000,
                retirement_age=60,
            ),
            ScenarioComparison(
                name="Age 61",
                success=True,
                ending_assets=1000000,
                ending_pension=600000,
                ending_isa=250000,
                ending_savings=150000,
                total_tax=100000,
                retirement_age=61,
            ),
        ]

        recommendations = RecommendationEngine().generate(comparisons)

        self.assertEqual(
            recommendations[0].title,
            "Recommended Retirement Age",
        )
        self.assertIn("60", recommendations[0].message)


    def test_sensitivity_high_confidence_when_age_is_stable(self):
        engine = RecommendationSensitivityEngine()

        result = engine.analyse(56, [56, 56, 56])

        self.assertEqual(result.confidence, "High")
        self.assertTrue(result.stable)
        self.assertEqual(result.ages, (56,))

    def test_sensitivity_moderate_confidence_for_small_age_spread(self):
        engine = RecommendationSensitivityEngine()

        result = engine.analyse(56, [55, 56, 57])

        self.assertEqual(result.confidence, "Moderate")
        self.assertFalse(result.stable)

    def test_sensitivity_low_confidence_for_large_age_spread(self):
        engine = RecommendationSensitivityEngine()

        result = engine.analyse(56, [54, 56, 59])

        self.assertEqual(result.confidence, "Low")
        self.assertFalse(result.stable)

    def test_sensitivity_empty_results_are_low_confidence(self):
        engine = RecommendationSensitivityEngine()

        result = engine.analyse(56, [])

        self.assertEqual(result.confidence, "Low")
        self.assertFalse(result.stable)

    def test_assumption_sensitivity_high_when_all_variants_match(self):
        engine = AssumptionSensitivityEngine()

        result = engine.analyse(56, [56, 56, 56, 56])

        self.assertEqual(result.confidence, "High")
        self.assertEqual(result.min_age, 56)
        self.assertEqual(result.max_age, 56)

    def test_assumption_sensitivity_moderate_when_variants_move_two_years(self):
        engine = AssumptionSensitivityEngine()

        result = engine.analyse(56, [55, 56, 57])

        self.assertEqual(result.confidence, "Moderate")
        self.assertEqual(result.min_age, 55)
        self.assertEqual(result.max_age, 57)

    def test_assumption_sensitivity_low_when_variants_move_more_than_two_years(self):
        engine = AssumptionSensitivityEngine()

        result = engine.analyse(56, [53, 56, 59])

        self.assertEqual(result.confidence, "Low")
        self.assertEqual(result.min_age, 53)
        self.assertEqual(result.max_age, 59)

    def test_assumption_sensitivity_deduplicates_ages(self):
        engine = AssumptionSensitivityEngine()

        result = engine.analyse(56, [56, 56, 57, 57])

        self.assertEqual(result.recommended_ages, (56, 57))

    def test_sensitivity_grid_contains_27_cases(self):
        grid = SensitivityGrid()

        self.assertEqual(len(grid.cases()), 27)

    def test_sensitivity_grid_contains_baseline_case(self):
        grid = SensitivityGrid()

        self.assertIn(
            SensitivityCase(
                pension_growth=0.04,
                net_spending=35000,
                isa_growth=0.04,
            ),
            grid.cases(),
        )

    def test_sensitivity_grid_has_three_values_for_each_assumption(self):
        grid = SensitivityGrid()
        cases = grid.cases()

        self.assertEqual(
            sorted(set(case.pension_growth for case in cases)),
            [0.03, 0.04, 0.05],
        )
        self.assertEqual(
            sorted(set(case.net_spending for case in cases)),
            [34000, 35000, 36000],
        )
        self.assertEqual(
            sorted(set(case.isa_growth for case in cases)),
            [0.03, 0.04, 0.05],
        )

    def test_sensitivity_runner_executes_all_27_cases(self):
        runner = SensitivityRunner()
        result = runner.run(lambda case: 56)
        self.assertEqual(result.total_cases, 27)
        self.assertEqual(len(result.runs), 27)
        self.assertEqual(result.recommended_ages, (56,) * 27)

    def test_sensitivity_runner_summarises_age_distribution(self):
        runner = SensitivityRunner()
        result = runner.run(lambda case: 55 if case.net_spending == 34000 else 56)
        self.assertEqual(result.min_age, 55)
        self.assertEqual(result.max_age, 56)
        self.assertEqual(result.most_common_age, 56)
        self.assertEqual(result.most_common_count, 18)

    def test_sensitivity_runner_preserves_none_for_failed_case(self):
        runner = SensitivityRunner()
        result = runner.run(lambda case: None if case.net_spending == 36000 else 56)
        self.assertEqual(result.total_cases, 27)
        self.assertEqual(len(result.recommended_ages), 18)
        self.assertEqual(result.min_age, 56)
        self.assertEqual(result.max_age, 56)

    def test_sensitivity_runner_does_not_modify_baseline_assumptions(self):
        from planner.recommendations.sensitivity_runner import SensitivityRunner
        from planner.assumptions import Assumptions

        assumptions = Assumptions()
        baseline = {
            "pension_growth": assumptions.get("pension_growth"),
            "target_net_income": assumptions.get("target_net_income"),
            "isa_growth_rate": assumptions.get("isa_growth_rate"),
        }

        runner = SensitivityRunner()
        runner.run_real(assumptions, 55, 55)

        self.assertEqual(
            {
                "pension_growth": assumptions.get("pension_growth"),
                "target_net_income": assumptions.get("target_net_income"),
                "isa_growth_rate": assumptions.get("isa_growth_rate"),
            },
            baseline,
        )

    def test_real_sensitivity_runner_executes_27_cases(self):
        from planner.recommendations.sensitivity_runner import SensitivityRunner
        from planner.assumptions import Assumptions

        result = SensitivityRunner().run_real(
            Assumptions(),
            minimum_age=55,
            maximum_age=55,
        )

        self.assertEqual(result.total_cases, 27)
        self.assertEqual(len(result.runs), 27)

    def test_real_sensitivity_runner_records_successful_ages(self):
        from planner.recommendations.sensitivity_runner import SensitivityRunner
        from planner.assumptions import Assumptions

        result = SensitivityRunner().run_real(
            Assumptions(),
            minimum_age=55,
            maximum_age=57,
        )

        self.assertEqual(result.total_cases, 27)
        self.assertTrue(
            all(isinstance(run.successful_ages, tuple) for run in result.runs)
        )

    def test_sensitivity_driver_analysis_groups_all_three_dimensions(self):
        from planner.recommendations.sensitivity_runner import SensitivityRun
        from planner.recommendations.sensitivity_grid import SensitivityCase

        runs = (
            SensitivityRun(SensitivityCase(0.03, 34000, 0.03), 56),
            SensitivityRun(SensitivityCase(0.03, 35000, 0.04), 58),
            SensitivityRun(SensitivityCase(0.05, 36000, 0.05), 67),
        )

        analysis = SensitivityDriverAnalysis().analyse(runs)

        self.assertEqual(
            [item.dimension for item in analysis],
            ["pension_growth", "net_spending", "isa_growth"],
        )

    def test_sensitivity_driver_analysis_counts_recommendations(self):
        from planner.recommendations.sensitivity_runner import SensitivityRun
        from planner.recommendations.sensitivity_grid import SensitivityCase

        runs = (
            SensitivityRun(SensitivityCase(0.03, 34000, 0.03), 56),
            SensitivityRun(SensitivityCase(0.04, 35000, 0.04), 56),
            SensitivityRun(SensitivityCase(0.05, 36000, 0.05), 67),
            SensitivityRun(SensitivityCase(0.05, 35000, 0.04), None),
        )

        counts = SensitivityDriverAnalysis().recommendation_counts(runs)

        self.assertEqual(counts[56], 2)
        self.assertEqual(counts[67], 1)
        self.assertNotIn(None, counts)

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
