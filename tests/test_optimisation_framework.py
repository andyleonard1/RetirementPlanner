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


if __name__ == "__main__":
    unittest.main()
