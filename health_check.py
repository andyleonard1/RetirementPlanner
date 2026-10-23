"""
Retirement Health Check

Runs the current retirement-age scenario architecture, Monte Carlo analysis,
health assessment, goals and adviser narrative.
"""

import argparse
import copy

from planner.assumptions import Assumptions
from planner.adviser_engine import AdviserEngine
from planner.goal_engine import GoalEngine
from planner.health_engine import HealthEngine
from planner.monte_carlo_engine import MonteCarloEngine
from planner.planner import RetirementPlanner
from planner.recommendations.report_adapter import (
    RecommendationReportAdapter,
)
from planner.risk_engine import RiskEngine
from planner.scenarios.scenario import Scenario
from planner.scenarios.scenario_manager import ScenarioManager

from reports.adviser_report import AdviserReport
from reports.goal_report import GoalReport
from reports.goal_pdf_report import GoalPDFReport
from reports.health_report import HealthReport
from reports.health_check_pdf_report import HealthCheckPDFReport


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


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build the retirement health check report")
    parser.add_argument("--pdf", metavar="PATH", help="also export the health check report as PDF")
    parser.add_argument("--goals-pdf", metavar="PATH", help="also export the evaluated retirement goals as PDF")
    args = parser.parse_args(argv)

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

    monte_carlo = MonteCarloEngine(
        recommended_assumptions
    ).run(iterations=5000)

    risk = RiskEngine().analyse(result.timeline)

    recommendation = RecommendationReportAdapter().build(
        recommended_assumptions,
        result,
        decision,
        recommendations,
        risk,
    )

    goals = GoalEngine(
        recommended_assumptions
    ).evaluate(
        result.summary,
        monte_carlo,
        result.timeline,
    )

    GoalReport().print(goals)

    health = HealthEngine().build(
        result.summary,
        recommendation,
        monte_carlo,
    )

    HealthReport().print(
        health,
        recommendation,
        monte_carlo,
        result.summary,
    )

    advice = AdviserEngine().build(
        result.summary,
        recommendation,
        monte_carlo,
        health,
    )

    AdviserReport().print(advice)

    if args.pdf:
        path = HealthCheckPDFReport().create(health, recommendation, monte_carlo, result.summary, args.pdf)
        print(f"PDF health report exported: {path}")

    if args.goals_pdf:
        path = GoalPDFReport().create(goals, args.goals_pdf)
        print(f"PDF goals report exported: {path}")


if __name__ == "__main__":
    main()
