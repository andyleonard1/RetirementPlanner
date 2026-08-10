"""
Retirement Planner

Application entry point.
"""

import copy
import logging
import time

from planner.assumptions import Assumptions
from planner.planner import RetirementPlanner
from planner.report import ConsoleReport
from planner.scenarios.scenario import Scenario
from planner.scenarios.scenario_manager import ScenarioManager
from planner.services.retirement_solver import RetirementSolver
from planner.version import banner


logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)

logger = logging.getLogger(__name__)


def build_scenarios(
    assumptions,
    minimum_age=55,
    maximum_age=75,
):
    """
    Build one scenario for each retirement age.
    """

    scenarios = []

    for age in range(
        minimum_age,
        maximum_age + 1,
    ):

        scenario_assumptions = copy.deepcopy(
            assumptions
        )

        scenario_assumptions.set(
            "retirement_age",
            age,
        )

        scenarios.append(
            Scenario(
                name=f"Retire {age}",
                assumptions=scenario_assumptions,
            )
        )

    return scenarios


def main():

    print()
    print(banner())
    print()

    start = time.perf_counter()

    try:

        assumptions = Assumptions()

        # -------------------------------------------------
        # Find the earliest successful retirement age.
        # -------------------------------------------------

        solver = RetirementSolver(
            assumptions
        )

        recommended_age = solver.find_earliest_age(
            minimum_age=55,
            maximum_age=75,
        )

        if recommended_age is None:

            print()
            print(
                "No sustainable retirement age was "
                "found between ages 55 and 75."
            )

            return

        # -------------------------------------------------
        # Build scenario comparisons.
        # -------------------------------------------------

        manager = ScenarioManager()

        for scenario in build_scenarios(
            assumptions,
            minimum_age=55,
            maximum_age=75,
        ):

            manager.add(
                scenario
            )

        decision = manager.decision_summary()
        age_comparison = manager.retirement_age_comparison()

        # -------------------------------------------------
        # Run the planner at the recommended age.
        # -------------------------------------------------

        recommended_assumptions = copy.deepcopy(
            assumptions
        )

        recommended_assumptions.set(
            "retirement_age",
            recommended_age,
        )

        planner = RetirementPlanner(
            recommended_assumptions
        )

        result = planner.run()

        # -------------------------------------------------
        # Report.
        # -------------------------------------------------

        report = ConsoleReport()

        report.print(
            result.timeline,
            result.summary,
            decision,
            age_comparison,
        )

        elapsed = (
            time.perf_counter() - start
        )

        print()
        print(
            f"Recommended retirement age : "
            f"{recommended_age}"
        )

        print(
            f"Execution time             : "
            f"{elapsed:.2f} seconds"
        )

        print()

    except Exception as ex:

        logger.exception(ex)

        print()
        print("Planner failed.")
        print(ex)

        raise


if __name__ == "__main__":
    main()
