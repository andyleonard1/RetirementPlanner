import unittest

from planner.assumptions import Assumptions
from planner.optimisation_engine import OptimisationEngine
from planner.optimiser_engine import OptimiserEngine
from planner.tax_optimizer_engine import TaxOptimizerEngine
from planner.timeline import TimelineEngine


class OptimisationFrameworkTests(unittest.TestCase):

    def make_year(self):
        assumptions = Assumptions()
        timeline = TimelineEngine(assumptions).build()
        year = timeline[0]
        year.your_state_pension = 10000
        year.spouse_state_pension = 0
        return assumptions, [year]

    def test_canonical_engine_uses_personal_allowance(self):
        assumptions, timeline = self.make_year()

        OptimisationEngine(assumptions).apply(timeline)

        self.assertEqual(
            timeline[0].maximum_tax_efficient_pension,
            round(
                assumptions.get("personal_allowance") - 10000,
                2,
            ),
        )

    def test_tax_optimizer_reuses_shared_framework(self):
        assumptions, timeline = self.make_year()

        TaxOptimizerEngine(assumptions).apply(timeline)

        self.assertEqual(
            timeline[0].maximum_tax_efficient_pension,
            round(
                assumptions.get("basic_rate_limit") - 10000,
                2,
            ),
        )

    def test_british_spelling_is_compatibility_alias(self):
        self.assertIs(
            OptimiserEngine,
            OptimisationEngine,
        )

    def test_supported_policies_are_explicit(self):
        self.assertEqual(
            OptimisationEngine.supported_policies(),
            ("personal_allowance", "basic_rate_band"),
        )

    def test_policy_descriptions_cover_supported_policies(self):
        descriptions = OptimisationEngine.policy_descriptions()
        self.assertEqual(set(descriptions), set(OptimisationEngine.supported_policies()))
        self.assertTrue(all(descriptions.values()))

    def test_unknown_policy_fails_clearly(self):
        assumptions, _ = self.make_year()
        with self.assertRaisesRegex(ValueError, "Unknown optimisation policy"):
            OptimisationEngine(assumptions, policy="unknown")

    def test_calculate_is_read_only(self):
        assumptions, timeline = self.make_year()
        original = timeline[0].maximum_tax_efficient_pension

        values = OptimisationEngine(assumptions).calculate(timeline)

        self.assertEqual(
            values,
            [(timeline[0].age, round(assumptions.get("personal_allowance") - 10000, 2))],
        )
        self.assertEqual(timeline[0].maximum_tax_efficient_pension, original)

    def test_compare_policies_is_read_only_and_returns_both_policies(self):
        assumptions, timeline = self.make_year()

        original = timeline[0].maximum_tax_efficient_pension

        comparison = OptimisationEngine(assumptions).compare_policies(timeline)

        self.assertEqual(
            set(comparison),
            {"personal_allowance", "basic_rate_band"},
        )
        self.assertEqual(
            comparison["personal_allowance"][0][1],
            round(assumptions.get("personal_allowance") - 10000, 2),
        )
        self.assertEqual(
            comparison["basic_rate_band"][0][1],
            round(assumptions.get("basic_rate_limit") - 10000, 2),
        )
        self.assertEqual(timeline[0].maximum_tax_efficient_pension, original)

    def test_compare_policies_rejects_unknown_policy(self):
        assumptions, timeline = self.make_year()
        with self.assertRaisesRegex(ValueError, "Unknown optimisation policy"):
            OptimisationEngine(assumptions).compare_policies(
                timeline,
                policies=["personal_allowance", "unknown"],
            )


if __name__ == "__main__":
    unittest.main()


class OptimisationDecisionSupportTests(unittest.TestCase):

    def make_comparison(self):
        return {
            "personal_allowance": [(56, 20000), (57, 21000), (58, 22000)],
            "basic_rate_band": [(56, 40000), (57, 41000), (58, 42000)],
        }

    def test_assessment_identifies_higher_and_lower_policy(self):
        from planner.optimisation_decision_support import OptimisationDecisionSupport
        result = OptimisationDecisionSupport().assess(self.make_comparison())
        self.assertEqual(result.higher_policy, "basic_rate_band")
        self.assertEqual(result.lower_policy, "personal_allowance")

    def test_assessment_calculates_average_difference(self):
        from planner.optimisation_decision_support import OptimisationDecisionSupport
        result = OptimisationDecisionSupport().assess(self.make_comparison())
        self.assertEqual(result.average_difference, 20000)

    def test_assessment_finds_largest_difference_and_age(self):
        from planner.optimisation_decision_support import OptimisationDecisionSupport
        result = OptimisationDecisionSupport().assess(self.make_comparison())
        self.assertEqual(result.maximum_difference, 20000)
        self.assertEqual(result.maximum_difference_age, 56)

    def test_assessment_marks_material_difference(self):
        from planner.optimisation_decision_support import OptimisationDecisionSupport
        result = OptimisationDecisionSupport(materiality_threshold=1000).assess(self.make_comparison())
        self.assertTrue(result.material)

    def test_assessment_can_mark_difference_non_material(self):
        from planner.optimisation_decision_support import OptimisationDecisionSupport
        result = OptimisationDecisionSupport(materiality_threshold=25000).assess(self.make_comparison())
        self.assertFalse(result.material)

    def test_assessment_rejects_no_common_ages(self):
        from planner.optimisation_decision_support import OptimisationDecisionSupport
        with self.assertRaisesRegex(ValueError, "no common ages"):
            OptimisationDecisionSupport().assess({"a": [(56, 1)], "b": [(57, 2)]})

    def test_assessment_does_not_mutate_input(self):
        from planner.optimisation_decision_support import OptimisationDecisionSupport
        comparison = self.make_comparison()
        original = {key: list(value) for key, value in comparison.items()}
        OptimisationDecisionSupport().assess(comparison)
        self.assertEqual(comparison, original)
