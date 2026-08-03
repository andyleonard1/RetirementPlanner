"""
Retirement Planner

Application entry point.
"""

import logging
import time

from planner.assumptions import Assumptions
from planner.planner import RetirementPlanner
from planner.version import banner

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)

logger = logging.getLogger(__name__)


def main():

    print()
    print(banner())
    print()

    start = time.perf_counter()

    try:

        assumptions = Assumptions()

        planner = RetirementPlanner(
            assumptions
        )

        result = planner.run()

        elapsed = (
            time.perf_counter() - start
        )

        print()

        print("Retirement plan completed successfully")

        print(f"Execution time : {elapsed:.2f} seconds")

        print()

        print("Projected position at age 90")

        print("----------------------------")

        print(
            f"Pension : £{result.summary['ending_pension']:,.0f}"
        )

        print(
            f"ISA      : £{result.summary['ending_isa']:,.0f}"
        )

        print(
            f"Savings  : £{result.summary['ending_savings']:,.0f}"
        )

        print(
            f"Assets   : £{result.summary['ending_assets']:,.0f}"
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