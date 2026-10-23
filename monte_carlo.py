"""
Runs Monte Carlo analysis.
"""

from planner.assumptions import Assumptions
from planner.monte_carlo_engine import MonteCarloEngine


def main():

    assumptions = Assumptions()

    result = MonteCarloEngine(
        assumptions
    ).run(
        iterations=5000
    )

    print()

    print("## Monte Carlo Analysis")

    print()

    print(
        f"Iterations      : {result.iterations:,}"
    )

    print()

    print(
        f"5th Percentile  : £{result.percentile_5:,.0f}"
    )

    print(
        f"Median          : £{result.median:,.0f}"
    )

    print(
        f"95th Percentile : £{result.percentile_95:,.0f}"
    )

    print()

    print(
        f"Minimum         : £{result.minimum:,.0f}"
    )

    print(
        f"Maximum         : £{result.maximum:,.0f}"
    )

    print()

    print(
        f"Success Rate    : {result.success_rate:.1f}%"
    )

    print()


if __name__ == "__main__":
    main()