"""
Compare retirement strategies.
"""

import argparse

from planner.assumptions import Assumptions
from planner.scenario_engine import ScenarioEngine
from planner.cli import add_assumptions_argument

from reports.comparison_report import ComparisonReport
from reports.strategy_comparison_pdf_report import StrategyComparisonPDFReport


def main():

    parser = argparse.ArgumentParser(description="Compare retirement strategies")
    add_assumptions_argument(parser)
    parser.add_argument(
        "--pdf",
        metavar="PATH",
        help="write a professional PDF comparison report from the computed results",
    )
    args = parser.parse_args()
    engine = ScenarioEngine(assumptions=Assumptions(filename=args.assumptions))

    results = engine.compare_strategies()

    ComparisonReport().print(results)

    if args.pdf:
        pdf_path = StrategyComparisonPDFReport().create(results, args.pdf)
        print()
        print(f"PDF comparison report exported: {pdf_path}")


if __name__ == "__main__":
    main()