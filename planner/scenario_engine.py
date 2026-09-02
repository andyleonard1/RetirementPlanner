"""
Scenario Engine

Runs one or more retirement scenarios.
"""

from planner.assumptions import Assumptions
from planner.planner import RetirementPlanner
from planner.results import ScenarioResult


class ScenarioEngine:

    def run(self, scenario_name, changes=None):

        assumptions = Assumptions()

        if changes:
            assumptions.data.update(changes)

        planner = RetirementPlanner(assumptions, audit_context="analysis")
        result = planner.run()

        return ScenarioResult(
            name=scenario_name,
            timeline=result.timeline,
            summary=result.summary,
            final_year=result.timeline[-1],
        )

    def compare_strategies(self):

        scenarios = []

        for strategy in [
            "PENSION_FIRST",
            "ISA_FIRST",
        ]:

            result = self.run(
                scenario_name=strategy,
                changes={
                    "withdrawal_strategy": strategy,
                },
            )

            scenarios.append(result)

        return scenarios
