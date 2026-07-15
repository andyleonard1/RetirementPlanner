from planner.assumptions import Assumptions


def main():

    print("====================================")
    print("      Retirement Planner V5")
    print("====================================")

    assumptions = Assumptions()

    print()
    print(f"Current Age      : {assumptions.get('current_age')}")
    print(f"Retirement Age   : {assumptions.get('retirement_age')}")
    print(f"Starting Pension : £{assumptions.get('starting_pension'):,.0f}")
    print(f"Target Income    : £{assumptions.get('target_net_income'):,.0f}")


if __name__ == "__main__":
    main()