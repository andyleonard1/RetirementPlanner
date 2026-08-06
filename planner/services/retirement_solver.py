"""
Retirement Solver

Determines the earliest retirement age
that satisfies the retirement goals.
"""

import copy

from planner.planner import RetirementPlanner


class RetirementSolver:

    def __init__(self, assumptions):

        self.assumptions = assumptions

    # -------------------------------------------------

    def _run_at_age(self, age):

        assumptions = copy.deepcopy(
            self.assumptions
        )

        assumptions.set(
            "retirement_age",
            age,
        )

        planner = RetirementPlanner(
            assumptions
        )

        return planner.run()

    # -------------------------------------------------

    def find_earliest_age(
        self,
        minimum_age=55,
        maximum_age=75,
    ):

        for age in range(
            minimum_age,
            maximum_age + 1,
        ):

            result = self._run_at_age(age)

            if result.success:
                return age

        return None

    # -------------------------------------------------

    def explore(
        self,
        minimum_age=55,
        maximum_age=75,
    ):

        results = []

        for age in range(
            minimum_age,
            maximum_age + 1,
        ):

            result = self._run_at_age(age)

            results.append(result)

        return results