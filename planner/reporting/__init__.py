"""Application-level reporting orchestration surfaces.

Exports are resolved lazily to avoid importing report-pack composition while
loading shared reporting utilities (such as export cancellation control).
"""
from __future__ import annotations

from typing import Any

__all__ = [
    "ReportPackExportResult",
    "ReportSuiteExportResult",
    "export_report_pack",
    "export_report_suite",
]


def __getattr__(name: str) -> Any:
    if name in {"ReportPackExportResult", "export_report_pack"}:
        from . import report_pack

        return getattr(report_pack, name)
    if name in {"ReportSuiteExportResult", "export_report_suite"}:
        from . import report_suite

        return getattr(report_suite, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
