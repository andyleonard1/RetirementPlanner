from planner.assumptions import Assumptions
from planner.state_pension import StatePensionEngine


def main():

    print()
    print("=" * 70)
    print("                 Retirement Planner V5")
    print("=" * 70)

    assumptions = Assumptions()

    engine = StatePensionEngine(assumptions)

    projection = engine.project()

    print()
    print(f'{"Age":<6}{"Your Pension":>18}{"Spouse Pension":>20}')
    print("-" * 70)

    for year in projection:

        print(
            f'{year["age"]:<6}'
            f'£{year["your_pension"]:>16,.2f}'
            f'£{year["spouse_pension"]:>18,.2f}'
        )


if __name__ == "__main__":
    main()