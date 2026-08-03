"""
Scenario Engine

Runs one or more retirement scenarios.
"""

from copy import deepcopy

from planner.assumptions import Assumptions
from planner.planner import RetirementPlanner


class ScenarioEngine:

    def run(self, scenario_name, changes=None):

        assumptions = Assumptions()

        if changes:
            assumptions.data.update(changes)

        planner = RetirementPlanner(assumptions)

        result = planner.run()

        timeline = result.timeline
        summary = result.summary

        return {
            "name": scenario_name,
            "timeline": timeline,
            "summary": summary,
            "final_year": timeline[-1],
        }

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