"""Professional PDF presentation for precomputed strategy comparison results."""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Iterable

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.graphics.shapes import Drawing, Line, Rect, String
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from planner.results import ScenarioResult
from planner.version import VERSION


class StrategyComparisonPDFReport:
    """Render a calculation-free PDF from already-computed strategy results."""

    def create(
        self,
        results: Iterable[ScenarioResult],
        filename: str | Path = "RetirementStrategyComparison.pdf",
    ) -> Path:
        if not results:
            raise ValueError("at least one comparison result is required")

        results = tuple(results)
        if any(not isinstance(result, ScenarioResult) for result in results):
            raise TypeError("results must contain ScenarioResult objects")

        target = Path(filename)
        target.parent.mkdir(parents=True, exist_ok=True)

        styles = getSampleStyleSheet()
        document = SimpleDocTemplate(
            str(target),
            pagesize=A4,
            rightMargin=16 * mm,
            leftMargin=16 * mm,
            topMargin=16 * mm,
            bottomMargin=16 * mm,
            title="Retirement Strategy Comparison",
            author="Retirement Planner",
        )

        story = [
            Paragraph("RETIREMENT PLANNER", styles["Title"]),
            Paragraph("Strategy Comparison Report", styles["Heading2"]),
            Spacer(1, 8),
            Paragraph(f"Generated: {date.today()}", styles["Normal"]),
            Paragraph(f"Version: {VERSION}", styles["Normal"]),
            Spacer(1, 16),
            Paragraph("Precomputed Strategy Results", styles["Heading2"]),
            Paragraph(
                "This report presents results already produced by the planning engine. "
                "It performs no financial recalculation and does not rank or recommend a strategy.",
                styles["Normal"],
            ),
            Spacer(1, 12),
            _summary_table(results),
            Spacer(1, 18),
            Paragraph("Ending Assets", styles["Heading2"]),
            _comparison_bar_chart(results, "ending_assets", "Ending assets by strategy", "£"),
            Spacer(1, 18),
            Paragraph("Lifetime Tax", styles["Heading2"]),
            _comparison_bar_chart(results, "total_tax", "Total tax recorded by strategy", "£"),
            PageBreak(),
            Paragraph("Projection End State", styles["Heading1"]),
            Spacer(1, 8),
            _detail_table(results),
            Spacer(1, 18),
            Paragraph("Year-by-Year Strategy Detail", styles["Heading2"]),
            Paragraph(
                "The table below presents the published timeline values for each strategy. "
                "Values are rendered directly from the supplied ScenarioResult timelines.",
                styles["Normal"],
            ),
            Spacer(1, 8),
            _timeline_table(results),
            Spacer(1, 18),
            Paragraph(
                "Report provenance: values are rendered directly from the supplied ScenarioResult objects.",
                styles["Normal"],
            ),
        ]

        document.build(
            story,
            onFirstPage=self._draw_page_chrome,
            onLaterPages=self._draw_page_chrome,
        )
        return target

    @staticmethod
    def _draw_page_chrome(canvas, document):
        canvas.saveState()
        width, height = A4
        canvas.setStrokeColor(colors.lightgrey)
        canvas.line(16 * mm, height - 11 * mm, width - 16 * mm, height - 11 * mm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.grey)
        canvas.drawString(16 * mm, 7 * mm, "Retirement Planner - Strategy Comparison Report")
        canvas.drawRightString(width - 16 * mm, 7 * mm, f"Page {canvas.getPageNumber()}")
        canvas.restoreState()


def _summary_table(results: tuple[ScenarioResult, ...]) -> Table:
    rows = [["Strategy", "Status", "Ending assets", "Pension", "ISA", "Tax"]]
    for result in results:
        summary = result.summary
        rows.append(
            [
                str(result.name),
                "SUCCESS" if summary.get("success", True) else "NOT SUSTAINABLE",
                f"£{summary['ending_assets']:,.0f}",
                f"£{summary['ending_pension']:,.0f}",
                f"£{summary['ending_isa']:,.0f}",
                f"£{summary['total_tax']:,.0f}",
            ]
        )
    table = Table(rows, repeatRows=1, colWidths=[38 * mm, 31 * mm, 31 * mm, 31 * mm, 31 * mm, 23 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
            ]
        )
    )
    return table


def _detail_table(results: tuple[ScenarioResult, ...]) -> Table:
    rows = [["Strategy", "Ending pension", "Ending savings", "Ending ISA", "Failure age"]]
    for result in results:
        summary = result.summary
        failure_age = summary.get("first_failure_age")
        rows.append(
            [
                str(result.name),
                f"£{summary['ending_pension']:,.0f}",
                f"£{summary['ending_savings']:,.0f}",
                f"£{summary['ending_isa']:,.0f}",
                "-" if failure_age is None else str(failure_age),
            ]
        )
    table = Table(rows, repeatRows=1, colWidths=[44 * mm, 39 * mm, 39 * mm, 39 * mm, 27 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ]
        )
    )
    return table


def _timeline_table(results: tuple[ScenarioResult, ...]) -> Table:
    rows = [["Strategy", "Year", "Age", "Pension", "ISA", "Savings"]]
    for result in results:
        for row in result.timeline:
            rows.append(
                [
                    str(result.name),
                    str(row.calendar_year),
                    str(row.age),
                    f"£{row.closing_pension:,.0f}",
                    f"£{row.isa_closing:,.0f}",
                    f"£{row.savings_closing:,.0f}",
                ]
            )
    table = Table(
        rows,
        repeatRows=1,
        colWidths=[38 * mm, 24 * mm, 20 * mm, 34 * mm, 34 * mm, 34 * mm],
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ]
        )
    )
    return table


def _comparison_bar_chart(results: tuple[ScenarioResult, ...], field: str, title: str, prefix: str) -> Drawing:
    width = 170 * mm
    height = 48 * mm
    drawing = Drawing(width, height)
    left, right, bottom, top = 40, width - 12, 22, height - 18
    drawing.add(String(0, height - 8, title, fontName="Helvetica-Bold", fontSize=9))

    values = [float(result.summary[field]) for result in results]
    maximum = max(values) if values else 1.0
    if maximum <= 0:
        maximum = 1.0

    drawing.add(Line(left, bottom, left, top, strokeColor=colors.grey))
    drawing.add(Line(left, bottom, right, bottom, strokeColor=colors.grey))

    slot = (right - left) / max(len(results), 1)
    bar_width = min(44, slot * 0.60)
    for index, result in enumerate(results):
        value = float(result.summary[field])
        bar_height = (top - bottom - 10) * (value / maximum)
        x = left + slot * index + (slot - bar_width) / 2
        drawing.add(Rect(x, bottom, bar_width, bar_height, fillColor=colors.darkblue, strokeColor=colors.darkblue))
        drawing.add(String(x + bar_width / 2 - 18, bottom - 11, str(result.name), fontSize=6))
        drawing.add(String(x + bar_width / 2 - 22, bottom + bar_height + 3, f"{prefix}{value:,.0f}", fontSize=6))

    drawing.add(String(0, bottom + (top - bottom) * 0.5, f"Max {prefix}{maximum:,.0f}", fontSize=6, fillColor=colors.grey))
    return drawing
