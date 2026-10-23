"""Public API for composing the professional report suite into one PDF."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from reports.professional_report_pack import ProfessionalReportPackPDFReport

from .report_suite import REPORT_SUITE_KEYS, ReportSuiteExportResult


@dataclass(frozen=True)
class ReportPackExportResult:
    """Published path for the consolidated professional report pack."""

    path: Path


def export_report_pack(
    report_suite: ReportSuiteExportResult,
    output_path: str | Path,
    *,
    overwrite: bool = False,
) -> ReportPackExportResult:
    """Compose an existing five-PDF report suite into one safe published PDF."""
    if not isinstance(report_suite, ReportSuiteExportResult):
        raise TypeError("report_suite must be ReportSuiteExportResult")
    if tuple(report_suite.paths) != REPORT_SUITE_KEYS:
        raise ValueError("report_suite paths must use the canonical report-suite order")
    path = ProfessionalReportPackPDFReport().create(
        report_suite.paths,
        output_path,
        overwrite=overwrite,
    )
    return ReportPackExportResult(path=path)
