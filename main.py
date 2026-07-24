"""
Retirement Planner

Application entry point.
"""

import logging

from planner.version import VERSION
from planner.assumptions import Assumptions
from planner.planner import RetirementPlanner
from planner.report import ConsoleReport
from planner.reports.excel_report import ExcelReport


logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)

logger = logging.getLogger(__name__)


def main():

    logger.info("")
    logger.info("=" * 60)
    logger.info(f"Retirement Planner  v{VERSION}")
    logger.info("=" * 60)

    assumptions = Assumptions()

    planner = RetirementPlanner(assumptions)

    timeline, summary = planner.run()

    ConsoleReport().print(timeline, summary)

    ExcelReport().generate(timeline, assumptions)

    logger.info("")
    logger.info("Run complete.")


if __name__ == "__main__":
    main()