"""
Recommend the best retirement strategy.

Uses the current retirement-age scenario architecture rather than the
legacy DecisionEngine / RecommendationEngine.apply() workflow.
"""

import copy

from planner.assumptions import Assumptions
from planner.planner import RetirementPlanner
from planner.recommendations.report_adapter import (
    RecommendationReportAdapter,
)
from planner.risk_engine import RiskEngine
from planner.scenarios.scenario import Scenario
from planner.scenarios.scenario_manager import ScenarioManager

from reports.recommendation_report import RecommendationReport


def build_scenarios(assumptions, minimum_age=55, maximum_age=75):
    scenarios = []

    for age in range(minimum_age, maximum_age + 1):
        scenario_assumptions = copy.deepcopy(assumptions)
        scenario_assumptions.set("retirement_age", age)
        scenarios.append(
            Scenario(
                name=f"Retire {age}",
                assumptions=scenario_assumptions,
            )
        )

    return scenarios


def main():
    assumptions = Assumptions()

    manager = ScenarioManager()

    for scenario in build_scenarios(assumptions):
        manager.add(scenario)

    decision = manager.decision_summary()
    recommendations = manager.recommendations()

    recommended_age = (
        decision.recommended_age
        if decision is not None
        else assumptions.get("retirement_age")
    )

    recommended_assumptions = copy.deepcopy(assumptions)
    recommended_assumptions.set("retirement_age", recommended_age)

    result = RetirementPlanner(
        recommended_assumptions
    ).run()

    risk = RiskEngine().analyse(result.timeline)

    report = RecommendationReportAdapter().build(
        recommended_assumptions,
        result,
        decision,
        recommendations,
        risk,
    )

    RecommendationReport().print(report)


if __name__ == "__main__":
    main()
