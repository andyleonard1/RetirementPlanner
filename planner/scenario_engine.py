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

        timeline = planner.run()

        return {
            "name": scenario_name,
            "timeline": timeline,
            "final_year": timeline[-1],
        }