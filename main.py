from planner.assumptions import Assumptions
from planner.planner import RetirementPlanner
from planner.report import ConsoleReport
from planner.reports.excel_report import ExcelReport
from planner.logger import setup_logging

def main():
    setup_logging()
    assumptions = Assumptions()

    print("Starting savings:", assumptions.get("starting_savings"))
    print("Starting ISA:", assumptions.get("starting_isa"))

    planner = RetirementPlanner(assumptions)

    # Run the retirement model
    timeline, summary = planner.run()

    # Console report
    ConsoleReport().print(timeline, summary)

    # Excel report
    ExcelReport().generate(timeline, assumptions)


if __name__ == "__main__":
    main()