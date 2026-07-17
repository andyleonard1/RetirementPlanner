from planner.assumptions import Assumptions
from planner.planner import RetirementPlanner
from planner.report import ConsoleReport

def main():

    assumptions = Assumptions()

    planner = RetirementPlanner(assumptions)

    timeline = planner.run()

    def main():

        assumptions = Assumptions()

        planner = RetirementPlanner(assumptions)

        timeline = planner.run()

        ConsoleReport().print(timeline)

    for year in timeline:

        print(
            f"{year.age:<5}"
            f"{year.calendar_year:>8}"
            f"{year.closing_pension:>15,.0f}"
            f"{year.your_state_pension:>15,.0f}"
            f"{year.spouse_state_pension:>15,.0f}"
        )


if __name__ == "__main__":
    main()