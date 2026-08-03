"""
Goal Engine

Evaluates whether the retirement plan meets the user's goals.
"""

import logging

logger = logging.getLogger(__name__)


class GoalEngine:

    def __init__(self, assumptions):
        self.assumptions = assumptions

    def evaluate(
        self,
        summary,
        monte_carlo,
        timeline,
    ):

        logger.info("Running Goal Engine")

        goals = []

        config = self.assumptions.get("goals")

        for goal in config:

            goal_type = goal["type"]

            if goal_type == "estate":

                actual = summary["ending_assets"]

                target = goal["target"]

                passed = actual >= target

            elif goal_type == "monte_carlo":

                actual = monte_carlo.success_rate

                target = goal["target"]

                passed = actual >= target

            elif goal_type == "pension_positive":

                actual = summary["ending_pension"]

                target = 0

                passed = actual > 0

            elif goal_type == "retirement_age":

                actual = self.assumptions.get(
                    "retirement_age"
                )

                target = actual

                passed = True

            elif goal_type == "spending":

                actual = min(
                    year.target_spending
                    for year in timeline
                )

                target = self.assumptions.get(
                    "spending_phase_3"
                )

                passed = actual >= target

            else:

                continue

            goals.append({

                "name": goal["name"],

                "passed": passed,

                "target": target,

                "actual": actual,

            })

        return goals