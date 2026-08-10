import unittest

from planner.assumptions import Assumptions
from planner.scenarios.scenario import Scenario
from planner.scenarios.scenario_manager import ScenarioManager
from planner.scenarios.scenario_comparison import ScenarioComparison


class TestScenarioManager(unittest.TestCase):

    def test_add_scenario(self):

        manager = ScenarioManager()

        scenario = Scenario(
            name="Base Plan",
            assumptions=Assumptions(),
        )

        manager.add(scenario)

        self.assertEqual(
            manager.count(),
            1,
        )

    # -------------------------------------------------

    def test_returns_all_scenarios(self):

        manager = ScenarioManager()

        manager.add(
            Scenario(
                "Base",
                Assumptions(),
            )
        )

        manager.add(
            Scenario(
                "Retire 60",
                Assumptions(),
            )
        )

        self.assertEqual(
            len(manager.all()),
            2,
        )

    # -------------------------------------------------

    def test_run_all(self):

        manager = ScenarioManager()

        manager.add(
            Scenario(
                "Base",
                Assumptions(),
            )
        )

        results = manager.run_all()

        self.assertEqual(
            len(results),
            1,
        )

    # -------------------------------------------------

    def test_run_returns_planner_result(self):

        manager = ScenarioManager()

        assumptions = Assumptions()

        manager.add(
            Scenario(
                "Base",
                assumptions,
            )
        )

        results = manager.run_all()

        self.assertIsNotNone(
            results[0].summary
        )

    # -------------------------------------------------

    def test_compare_returns_result(self):

        manager = ScenarioManager()

        assumptions = Assumptions()

        manager.add(
            Scenario(
                "Base",
                assumptions,
            )
        )

        comparison = manager.compare()

        self.assertEqual(
            len(comparison),
            1,
        )

        self.assertGreater(
            comparison[0].ending_assets,
            0,
        )

        self.assertEqual(
            comparison[0].retirement_age,
            assumptions.get(
                "retirement_age"
            ),
        )

    # -------------------------------------------------

    def test_recommendations_returns_results(self):

        manager = ScenarioManager()

        manager.add(
            Scenario(
                "Base",
                Assumptions(),
            )
        )

        recommendations = (
            manager.recommendations()
        )

        self.assertGreater(
            len(recommendations),
            0,
        )

    # -------------------------------------------------

    def test_decision_summary_returns_result(self):

        manager = ScenarioManager()

        assumptions = Assumptions()

        manager.add(
            Scenario(
                "Base",
                assumptions,
            )
        )

        summary = (
            manager.decision_summary()
        )

        self.assertIsNotNone(
            summary
        )

        self.assertEqual(
            summary.recommended_age,
            assumptions.get(
                "retirement_age"
            ),
        )

    # -------------------------------------------------

    def test_decision_summary_returns_none_without_success(self):

        manager = ScenarioManager()

        manager.compare = lambda: [
            ScenarioComparison(
                name="Age 60",
                success=False,
                ending_assets=0,
                ending_pension=0,
                ending_isa=0,
                ending_savings=0,
                total_tax=0,
                retirement_age=60,
            )
        ]

        summary = (
            manager.decision_summary()
        )

        self.assertIsNone(
            summary
        )

    # -------------------------------------------------

    def test_retirement_age_comparison_returns_sorted_results(self):

        manager = ScenarioManager()

        assumptions_62 = Assumptions()

        assumptions_62.set(
            "retirement_age",
            62,
        )

        manager.add(
            Scenario(
                "Age 62",
                assumptions_62,
            )
        )

        assumptions_60 = Assumptions()

        assumptions_60.set(
            "retirement_age",
            60,
        )

        manager.add(
            Scenario(
                "Age 60",
                assumptions_60,
            )
        )

        comparison = (
            manager.retirement_age_comparison()
        )

        self.assertEqual(
            len(comparison),
            2,
        )

        self.assertEqual(
            comparison[0].retirement_age,
            60,
        )

        self.assertEqual(
            comparison[1].retirement_age,
            62,
        )

    # -------------------------------------------------

    def test_retirement_age_tradeoffs_compare_against_earliest_successful_age(self):

        manager = ScenarioManager()

        manager.compare = lambda: [

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

        tradeoffs = manager.retirement_age_tradeoffs()

        self.assertEqual(
            len(tradeoffs),
            1,
        )

        self.assertEqual(
            tradeoffs[0].starting_age,
            60,
        )

        self.assertEqual(
            tradeoffs[0].later_age,
            62,
        )

        self.assertEqual(
            tradeoffs[0].years_waited,
            2,
        )

        self.assertEqual(
            tradeoffs[0].additional_assets,
            100000,
        )

        self.assertEqual(
            tradeoffs[0].additional_assets_per_year,
            50000,
        )

    # -------------------------------------------------

    def test_retirement_age_tradeoffs_include_later_failure(self):

        manager = ScenarioManager()

        manager.compare = lambda: [

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
                ending_assets=950000,
                ending_pension=540000,
                ending_isa=260000,
                ending_savings=150000,
                total_tax=105000,
                retirement_age=61,
            ),
        ]

        tradeoffs = manager.retirement_age_tradeoffs()

        self.assertEqual(
            len(tradeoffs),
            1,
        )

        self.assertFalse(
            tradeoffs[0].later_success
        )

        self.assertEqual(
            tradeoffs[0].additional_assets,
            50000,
        )

    # -------------------------------------------------

    def test_retirement_age_tradeoffs_returns_none_without_successful_plan(self):

        manager = ScenarioManager()

        manager.compare = lambda: [
            ScenarioComparison(
                name="Age 60",
                success=False,
                ending_assets=0,
                ending_pension=0,
                ending_isa=0,
                ending_savings=0,
                total_tax=0,
                retirement_age=60,
            )
        ]

        tradeoffs = manager.retirement_age_tradeoffs()

        self.assertEqual(
            tradeoffs,
            [],
        )

    # -------------------------------------------------

    def test_retirement_age_comparison_calculates_asset_change(self):

        manager = ScenarioManager()

        manager.compare = lambda: [

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

        comparison = (
            manager.retirement_age_comparison()
        )

        self.assertIsNone(
            comparison[0].change_from_previous_age
        )

        self.assertEqual(
            comparison[1].change_from_previous_age,
            50000,
        )


if __name__ == "__main__":
    unittest.main()
# -------------------------------------------------

class TestRetirementAgeScoring(unittest.TestCase):

    def test_retirement_age_scores_are_returned_in_age_order(self):

        manager = ScenarioManager()

        manager.compare = lambda: [
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

        scores = manager.retirement_age_scores()

        self.assertEqual(
            [score.retirement_age for score in scores],
            [60, 62],
        )

    def test_earliest_successful_age_scores_high_for_early_retirement(self):

        manager = ScenarioManager()

        manager.compare = lambda: [
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

        scores = manager.retirement_age_scores()

        self.assertEqual(
            scores[0].earliest_age_score,
            100.0,
        )

        self.assertEqual(
            scores[1].earliest_age_score,
            0.0,
        )

    def test_highest_assets_score_is_100(self):

        manager = ScenarioManager()

        manager.compare = lambda: [
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

        scores = manager.retirement_age_scores()

        self.assertEqual(
            scores[1].ending_assets_score,
            100.0,
        )

    def test_unsuccessful_age_scores_zero(self):

        manager = ScenarioManager()

        manager.compare = lambda: [
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

        scores = manager.retirement_age_scores()

        self.assertFalse(scores[1].success)
        self.assertEqual(scores[1].total_score, 0.0)
