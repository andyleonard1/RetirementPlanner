"""Generate and optionally export the scenario projection report."""
from __future__ import annotations

import argparse
import logging

from planner.assumptions import Assumptions
from planner.cli import add_assumptions_argument
from planner.projection import ScenarioProjectionApplication
from reports.scenario_projection_pdf_report import ScenarioProjectionPDFReport


DEFAULT_ALLOCATIONS = {"Aviva": 0.75, "Sky": 0.25}
DEFAULT_FUND_RETURNS = {
    "Aviva": [0.10, 0.02, 0.08],
    "Sky": [0.20, 0.04, 0.16],
}

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Retirement Planner scenario report")
    add_assumptions_argument(parser)
    parser.add_argument(
        "--export-dir",
        metavar="DIR",
        help="write the JSON/text report bundle to this directory",
    )
    parser.add_argument(
        "--export-stem",
        default="retirement_projection",
        metavar="NAME",
        help="filename stem for exported JSON/text companions",
    )
    parser.add_argument(
        "--pdf",
        metavar="PATH",
        help="write a professional PDF report from the published workflow result",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace an existing report bundle transactionally",
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.overwrite and not args.export_dir:
        parser.error("--overwrite requires --export-dir")

    try:
        application = ScenarioProjectionApplication(Assumptions(filename=args.assumptions))
        result = application.run_report_workflow(
            allocations=DEFAULT_ALLOCATIONS,
            fund_returns=DEFAULT_FUND_RETURNS,
        )
        print(result.report_text)

        if args.pdf:
            pdf_path = ScenarioProjectionPDFReport().create(result, args.pdf)
            print()
            print(f"PDF report exported: {pdf_path}")

        if args.export_dir:
            paths = result.export_bundle(
                args.export_dir,
                args.export_stem,
                overwrite=args.overwrite,
            )
            print()
            print(f"JSON report exported: {paths['json']}")
            print(f"Text report exported: {paths['text']}")
        return 0
    except Exception as exc:
        logger.error("Scenario report failed: %s", exc)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
