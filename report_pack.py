"""Compose an existing five-file professional report suite into one PDF."""
from __future__ import annotations

import argparse
from pathlib import Path

from planner.reporting.report_pack import export_report_pack
from planner.reporting.report_suite import ReportSuiteExportResult


def main(argv=None):
    parser = argparse.ArgumentParser(description="Compose the professional retirement report pack")
    parser.add_argument("--directory", required=True, metavar="PATH", help="folder containing the five report-suite PDFs")
    parser.add_argument("--pdf", required=True, metavar="PATH", help="output combined PDF path")
    parser.add_argument("--overwrite", action="store_true", help="replace an existing combined PDF safely")
    args = parser.parse_args(argv)

    directory = Path(args.directory)
    suite = ReportSuiteExportResult(
        scenario_projection=directory / "retirement_scenario_projection.pdf",
        strategy_comparison=directory / "retirement_strategy_comparison.pdf",
        recommendation=directory / "retirement_recommendation.pdf",
        health_check=directory / "retirement_health_check.pdf",
        retirement_goals=directory / "retirement_goals.pdf",
    )
    result = export_report_pack(suite, args.pdf, overwrite=args.overwrite)
    print(f"Professional report pack exported: {result.path}")


if __name__ == "__main__":
    main()
