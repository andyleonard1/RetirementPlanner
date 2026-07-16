from planner.assumptions import Assumptions
from planner.pension_engine import PensionEngine


def main():

    assumptions = Assumptions()

    engine = PensionEngine(assumptions)

    projection = engine.project()

    print()

    print(
        f"{'Age':<5}"
        f"{'Opening':>15}"
        f"{'Growth':>15}"
        f"{'Withdraw':>15}"
        f"{'Closing':>15}"
    )

    print("-" * 65)

    for year in projection:

        print(
            f"{year.age:<5}"
            f"{year.opening:>15,.0f}"
            f"{year.growth:>15,.0f}"
            f"{year.withdrawal:>15,.0f}"
            f"{year.closing:>15,.0f}"
        )


if __name__ == "__main__":
    main()