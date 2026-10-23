"""Compose the five professional retirement PDFs into one navigable report pack."""
from __future__ import annotations

from datetime import date
from io import BytesIO
from pathlib import Path
from typing import Mapping

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle, Paragraph

from planner.version import VERSION


REPORT_TITLES = {
    "scenario_projection": "Scenario Projection",
    "strategy_comparison": "Strategy Comparison",
    "recommendation": "Recommendation",
    "health_check": "Health Check",
    "retirement_goals": "Retirement Goals",
}
REPORT_ORDER = tuple(REPORT_TITLES)


class ProfessionalReportPackPDFReport:
    """Create one navigable PDF from an already-generated report suite."""

    def create(
        self,
        report_paths: Mapping[str, str | Path],
        filename: str | Path = "RetirementPlanner_Report_Pack.pdf",
        *,
        overwrite: bool = False,
    ) -> Path:
        _validate_report_paths(report_paths)
        target = Path(filename)
        target.parent.mkdir(parents=True, exist_ok=True)

        if target.exists() and not overwrite:
            raise FileExistsError(f"report pack destination already exists: {target}")

        resolved_sources = {key: Path(report_paths[key]).resolve() for key in REPORT_ORDER}
        if target.resolve() in resolved_sources.values():
            raise ValueError("report pack output must not replace a source report")

        readers = {key: PdfReader(str(path)) for key, path in resolved_sources.items()}
        cover = _build_cover_pdf(readers)

        writer = PdfWriter()
        cover_reader = PdfReader(cover)
        writer.append(cover_reader)
        section_pages: dict[str, int] = {}
        for key in REPORT_ORDER:
            section_pages[key] = len(writer.pages)
            writer.append(readers[key])

        writer.add_metadata(
            {
                "/Title": "Retirement Planner — Professional Report Pack",
                "/Author": "Retirement Planner",
                "/Subject": "Consolidated professional retirement reports",
                "/Creator": f"Retirement Planner {VERSION}",
            }
        )
        for key in REPORT_ORDER:
            writer.add_outline_item(REPORT_TITLES[key], section_pages[key])

        temporary = target.with_name(f".{target.name}.tmp")
        if temporary.exists():
            temporary.unlink()
        try:
            with temporary.open("wb") as handle:
                writer.write(handle)
            temporary.replace(target)
        except Exception:
            temporary.unlink(missing_ok=True)
            raise
        return target


def _validate_report_paths(report_paths: Mapping[str, str | Path]) -> None:
    if not isinstance(report_paths, Mapping):
        raise TypeError("report_paths must be a mapping")
    if tuple(report_paths) != REPORT_ORDER:
        raise ValueError(
            "report_paths must contain exactly the five professional reports "
            f"in canonical order: {REPORT_ORDER}"
        )
    for key in REPORT_ORDER:
        path = Path(report_paths[key])
        if not path.exists():
            raise FileNotFoundError(f"report source does not exist: {path}")
        if path.suffix.lower() != ".pdf":
            raise ValueError(f"report source must be a PDF: {path}")


def _build_cover_pdf(readers: Mapping[str, PdfReader]) -> BytesIO:
    buffer = BytesIO()
    styles = getSampleStyleSheet()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=22 * mm,
        bottomMargin=18 * mm,
        title="Retirement Planner — Professional Report Pack",
        author="Retirement Planner",
    )
    rows = [["Section", "Pages"]]
    for key in REPORT_ORDER:
        rows.append([REPORT_TITLES[key], str(len(readers[key].pages))])

    story = [
        Paragraph("RETIREMENT PLANNER", styles["Title"]),
        Paragraph("Professional Retirement Report Pack", styles["Heading1"]),
        Spacer(1, 8),
        Paragraph(f"Generated: {date.today()}", styles["Normal"]),
        Paragraph(f"Version: {VERSION}", styles["Normal"]),
        Spacer(1, 18),
        Paragraph("Included Reports", styles["Heading2"]),
        Table(
            rows,
            colWidths=[118 * mm, 32 * mm],
            repeatRows=1,
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                ]
            ),
        ),
        Spacer(1, 18),
        Paragraph(
            "Use the document outline/bookmarks to jump directly to each report section. "
            "Each included report is reproduced from its already-generated PDF; this pack "
            "performs no retirement-financial recalculation and does not modify the source reports.",
            styles["Normal"],
        ),
    ]
    document.build(story)
    buffer.seek(0)
    return buffer
