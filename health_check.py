"""
Retirement Health Check

Runs the planner, recommendation engine, Monte Carlo analysis,
health assessment and adviser narrative.
"""

from planner.assumptions import Assumptions
from planner.planner import RetirementPlanner

from planner.decision_engine import DecisionEngine
from planner.recommendation_engine import RecommendationEngine
from planner.monte_carlo_engine import MonteCarloEngine
from planner.health_engine import HealthEngine
from planner.adviser_engine import AdviserEngine

from reports.health_report import HealthReport
from reports.adviser_report import AdviserReport
from planner.goal_engine import GoalEngine
from reports.goal_report import GoalReport


def main():

    #
    # Load assumptions
    #
    assumptions = Assumptions()

    #
    # Run retirement planner
    #
    planner = RetirementPlanner(
        assumptions
    )

    result = planner.run()

    #
    # Build recommendation
    #
    decision = DecisionEngine().run()

    recommendation = RecommendationEngine().apply(
        decision
    )

    #
    # Monte Carlo analysis
    #
    monte_carlo = MonteCarloEngine(
        assumptions
    ).run(
        iterations=5000
    )
    goals = GoalEngine(
        assumptions
    ).evaluate(
        result.summary,
        monte_carlo,
        result.timeline,
    )

    GoalReport().print(
        goals
    )
    #
    # Retirement health
    #
    health = HealthEngine().build(
        result.summary,
        recommendation,
        monte_carlo,
    )

    #
    # Executive dashboard
    #
    HealthReport().print(
        health,
        recommendation,
        monte_carlo,
        result.summary,
    )

    #
    # Adviser narrative
    #
    advice = AdviserEngine().build(
        result.summary,
        recommendation,
        monte_carlo,
        health,
    )

    AdviserReport().print(
        advice
    )


if __name__ == "__main__":
    main()