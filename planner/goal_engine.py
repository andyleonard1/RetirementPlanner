"""
Goal Engine

Evaluates whether the retirement plan meets the user's goals.
"""

import logging
import math
from numbers import Real

logger = logging.getLogger(__name__)


class GoalEngine:

    def __init__(self, assumptions):
        self.assumptions = assumptions

    _OPERATORS = {">=", ">", "<=", "<", "==", "!="}

    @classmethod
    def _validate_target(cls, goal, index, *, required=False):
        if "target" not in goal:
            if required:
                raise ValueError(
                    f"goals[{index}].target is required for goal type '{goal.get('type')}'."
                )
            return None

        target = goal["target"]
        if (
            isinstance(target, bool)
            or not isinstance(target, Real)
            or not math.isfinite(target)
        ):
            raise ValueError(f"goals[{index}].target must be a finite number.")
        return target

    @classmethod
    def _resolve_operator(cls, goal, index, default_operator):
        operator = goal.get("operator") or default_operator
        if operator not in cls._OPERATORS:
            raise ValueError(
                f"goals[{index}].operator must be one of: "
                + ", ".join(sorted(cls._OPERATORS))
                + "."
            )
        return operator

    @classmethod
    def _validate_actual(cls, actual, index):
        if (
            isinstance(actual, bool)
            or not isinstance(actual, Real)
            or not math.isfinite(actual)
        ):
            raise ValueError(f"goals[{index}] actual value must be a finite number.")
        return actual

    @staticmethod
    def _compare(actual, target, operator):
        comparisons = {
            ">=": lambda: actual >= target,
            ">": lambda: actual > target,
            "<=": lambda: actual <= target,
            "<": lambda: actual < target,
            "==": lambda: actual == target,
            "!=": lambda: actual != target,
        }
        return comparisons[operator]()

    def evaluate(
        self,
        summary,
        monte_carlo,
        timeline,
    ):

        logger.info("Running Goal Engine")

        goals = []
        config = self.assumptions.get("goals") or []

        for index, goal in enumerate(config):
            if not isinstance(goal, dict):
                raise ValueError(f"goals[{index}] must be an object.")

            name = goal.get("name")
            if not isinstance(name, str) or not name.strip():
                raise ValueError(f"goals[{index}].name must be a non-empty string.")

            goal_type = goal.get("type")
            if not isinstance(goal_type, str) or not goal_type.strip():
                raise ValueError(f"goals[{index}].type must be a non-empty string.")

            if "enabled" in goal and not isinstance(goal["enabled"], bool):
                raise ValueError(f"goals[{index}].enabled must be a boolean.")

            if goal.get("enabled", True) is False:
                continue


            if goal_type == "estate":
                actual = summary["ending_assets"]
                target = self._validate_target(goal, index, required=True)
                default_operator = ">="
            elif goal_type == "monte_carlo":
                actual = monte_carlo.success_rate
                target = self._validate_target(goal, index, required=True)
                default_operator = ">="
            elif goal_type == "pension_positive":
                actual = summary["ending_pension"]
                target = self._validate_target(goal, index)
                target = 0 if target is None else target
                default_operator = ">"
            elif goal_type == "retirement_age":
                actual = self.assumptions.get("retirement_age")
                target = self._validate_target(goal, index)
                target = actual if target is None else target
                default_operator = "=="
            elif goal_type == "spending":
                if not timeline:
                    raise ValueError(
                        f"goals[{index}] spending goal requires a non-empty timeline."
                    )
                actual = min(year.target_spending for year in timeline)
                target = self._validate_target(goal, index)
                target = self.assumptions.get("spending_phase_3") if target is None else target
                default_operator = ">="
            else:
                continue

            actual = self._validate_actual(actual, index)
            target = self._validate_target(goal, index) if target is None else target
            operator = self._resolve_operator(goal, index, default_operator)
            passed = self._compare(actual, target, operator)

            goals.append({
                "name": name,
                "passed": passed,
                "target": target,
                "actual": actual,
                "operator": operator,
                "enabled": True,
            })

        return goals
