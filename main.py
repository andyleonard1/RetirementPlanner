from planner.assumptions import Assumptions
from planner.pension_engine import PensionEngine


def main():

    assumptions = Assumptions()

    engine = PensionEngine(assumptions)

    projection = engine.project()

    print()

    print(
        f'{"Age":<6}'
        f'{"Opening":>15}'
        f'{"Growth":>15}'
        f'{"Withdraw":>15}'
        f'{"Closing":>15}'
    )

    print("-" * 70)

    for year in projection:

        print(
            f'{year.age:<6}'
            f'£{year.opening:>14,.0f}'
            f'£{year.growth:>14,.0f}'
            f'£{year.withdrawal:>14,.0f}'
            f'£{year.closing:>14,.0f}'
        )


if __name__ == "__main__":
    main()