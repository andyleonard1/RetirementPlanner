from planner.assumptions import Assumptions
from planner.planner import RetirementPlanner
from planner.report import ConsoleReport


def main():

    assumptions = Assumptions()

    print("Starting savings:", assumptions.get("starting_savings"))
    print("Starting ISA:", assumptions.get("starting_isa"))

    planner = RetirementPlanner(assumptions)

    timeline = planner.run()

    ConsoleReport().print(timeline)


if __name__ == "__main__":
    main()