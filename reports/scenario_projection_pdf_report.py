"""PDF rendering for the unified scenario projection workflow result."""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, Mapping

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.graphics.shapes import Drawing, Line, String
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from planner.projection import ScenarioProjectionWorkflowResult
from planner.version import VERSION


class ScenarioProjectionPDFReport:
    """Render a calculation-free professional PDF from one workflow result."""

    def create(
        self,
        workflow_result: ScenarioProjectionWorkflowResult,
        filename: str | Path = "RetirementProjectionReport.pdf",
    ) -> Path:
        """Create a PDF using only the already-published workflow report payload."""
        if not isinstance(workflow_result, ScenarioProjectionWorkflowResult):
            raise TypeError("workflow_result must be ScenarioProjectionWorkflowResult")

        payload = workflow_result.report_payload
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
            title="Retirement Projection Report",
            author="Retirement Planner",
        )
        story = []
        story.extend(self._summary_story(styles, workflow_result, payload))
        story.append(PageBreak())
        story.extend(self._trajectory_story(styles, payload))
        story.append(PageBreak())
        story.extend(self._scenario_story(styles, payload))
        story.append(PageBreak())
        story.extend(self._year_rows_story(styles, payload))
        document.build(
            story,
            onFirstPage=self._draw_page_chrome,
            onLaterPages=self._draw_page_chrome,
        )
        return target

    @staticmethod
    def _summary_story(styles, result, payload: Mapping[str, Any]):
        inputs = result.inputs
        summary = payload.get("summary", [])
        story = [
            Paragraph("RETIREMENT PLANNER", styles["Title"]),
            Paragraph("Scenario Projection Report", styles["Heading2"]),
            Spacer(1, 8),
            Paragraph(f"Generated: {date.today()}", styles["Normal"]),
            Paragraph(f"Version: {VERSION}", styles["Normal"]),
            Spacer(1, 16),
            Paragraph("Projection Inputs", styles["Heading2"]),
        ]
        inputs_rows = [
            ["Starting pension", f"£{inputs.starting_pension:,.0f}"],
            ["Retirement age", str(inputs.retirement_age)],
            ["Projection end age", str(inputs.projection_end_age)],
            ["Scenarios", ", ".join(inputs.scenarios)],
        ]
        story.append(_styled_table(inputs_rows, widths=[70 * mm, 95 * mm]))
        story.extend(
            [
                Spacer(1, 16),
                Paragraph("Scenario Overview", styles["Heading2"]),
            ]
        )
        scenario_rows = [["Scenario", "Return", "Ending balance", "Withdrawals"]]
        for item in summary:
            scenario_rows.append(
                [
                    str(item["name"]),
                    f"{item['annual_return']:.1%}",
                    f"£{item['ending_balance']:,.0f}",
                    f"£{item['total_withdrawals']:,.0f}",
                ]
            )
        story.append(_styled_table(scenario_rows, widths=[48 * mm, 30 * mm, 44 * mm, 44 * mm], header=True))
        story.extend(
            [
                Spacer(1, 16),
                Paragraph("Range of Projected Outcomes", styles["Heading2"]),
            ]
        )
        range_rows = [
            ["Lowest ending balance", f"£{payload['lowest_ending_balance']:,.0f}"],
            ["Highest ending balance", f"£{payload['highest_ending_balance']:,.0f}"],
            ["Scenario spread", f"£{payload['ending_balance_spread']:,.0f}"],
        ]
        story.append(_styled_table(range_rows, widths=[70 * mm, 95 * mm]))
        story.extend(
            [
                Spacer(1, 16),
                Paragraph("Published Report Text", styles["Heading2"]),
                Paragraph(_escape_paragraph_text(result.report_text), styles["Normal"]),
            ]
        )
        return story

    @staticmethod
    def _trajectory_story(styles, payload: Mapping[str, Any]):
        """Render a vector trajectory chart directly from published year rows."""
        story = [Paragraph("Projected Balance Trajectory", styles["Heading1"]), Spacer(1, 8)]
        story.append(Paragraph(
            "The chart below visualises the published year-by-year balances for each scenario. "
            "It is rendered directly from the report payload and performs no additional financial calculations.",
            styles["Normal"],
        ))
        story.append(Spacer(1, 12))
        story.append(_balance_trajectory_chart(payload.get("year_rows", [])))
        story.append(Spacer(1, 12))
        story.append(Paragraph(
            "Report provenance: this presentation is generated from one immutable "
            "ScenarioProjectionWorkflowResult.",
            styles["Normal"],
        ))
        return story

    @staticmethod
    def _draw_page_chrome(canvas, document):
        canvas.saveState()
        width, height = A4
        canvas.setStrokeColor(colors.lightgrey)
        canvas.line(16 * mm, height - 11 * mm, width - 16 * mm, height - 11 * mm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.grey)
        canvas.drawString(16 * mm, 7 * mm, "Retirement Planner — Scenario Projection Report")
        canvas.drawRightString(width - 16 * mm, 7 * mm, f"Page {canvas.getPageNumber()}")
        canvas.restoreState()

    @staticmethod
    def _scenario_story(styles, payload: Mapping[str, Any]):
        story = [Paragraph("Scenario Detail", styles["Heading1"]), Spacer(1, 8)]
        for scenario in payload.get("scenarios", []):
            story.append(Paragraph(str(scenario["name"]).title(), styles["Heading2"]))
            detail_rows = [
                ["Source", str(scenario["source"])],
                ["Starting pension", f"£{scenario['starting_pension']:,.0f}"],
                ["Annual return", f"{scenario['annual_return']:.1%}"],
                ["Ending balance", f"£{scenario['ending_balance']:,.0f}"],
                ["Investment growth", f"£{scenario['total_investment_growth']:,.0f}"],
                ["Total withdrawals", f"£{scenario['total_withdrawals']:,.0f}"],
            ]
            story.append(_styled_table(detail_rows, widths=[70 * mm, 95 * mm]))
            story.append(Spacer(1, 12))
        return story

    @staticmethod
    def _year_rows_story(styles, payload: Mapping[str, Any]):
        story = [Paragraph("Year-by-Year Projection", styles["Heading1"]), Spacer(1, 8)]
        rows = [["Scenario", "Year", "Starting", "Growth", "Withdrawals", "Ending"]]
        for item in payload.get("year_rows", []):
            rows.append(
                [
                    str(item["scenario"]),
                    str(item["year"]),
                    f"£{item['starting_balance']:,.0f}",
                    f"£{item['investment_growth']:,.0f}",
                    f"£{item['withdrawals']:,.0f}",
                    f"£{item['ending_balance']:,.0f}",
                ]
            )
        story.append(
            _styled_table(
                rows,
                widths=[30 * mm, 18 * mm, 34 * mm, 30 * mm, 32 * mm, 34 * mm],
                header=True,
                font_size=7,
            )
        )
        return story


def _balance_trajectory_chart(year_rows):
    width = 170 * mm
    height = 92 * mm
    drawing = Drawing(width, height)
    left, right, bottom, top = 40, width - 12, 22, height - 18
    drawing.add(String(0, height - 8, "Published ending balance by year", fontName="Helvetica-Bold", fontSize=9))

    grouped = {}
    for row in year_rows:
        grouped.setdefault(str(row["scenario"]), []).append(row)
    if not grouped:
        drawing.add(String(left, height / 2, "No year-by-year projection rows available.", fontSize=8))
        return drawing

    values = [float(row["ending_balance"]) for rows in grouped.values() for row in rows]
    min_value, max_value = min(values), max(values)
    if max_value == min_value:
        max_value = min_value + 1.0
    years = sorted({int(row["year"]) for row in year_rows})
    min_year, max_year = min(years), max(years)
    year_span = max(max_year - min_year, 1)

    drawing.add(Line(left, bottom, right, bottom, strokeColor=colors.grey))
    drawing.add(Line(left, bottom, left, top, strokeColor=colors.grey))

    for index, value in enumerate((min_value, max_value)):
        y = bottom + (top - bottom) * index
        drawing.add(String(0, y - 3, f"£{value:,.0f}", fontSize=6, fillColor=colors.grey))

    for year in (min_year, max_year):
        x = left + (right - left) * ((year - min_year) / year_span)
        drawing.add(String(x - 12, bottom - 12, str(year), fontSize=6, fillColor=colors.grey))

    palette = [colors.darkblue, colors.darkgreen, colors.darkred, colors.purple, colors.orange]
    for series_index, (name, rows) in enumerate(sorted(grouped.items())):
        rows = sorted(rows, key=lambda item: int(item["year"]))
        points = []
        for row in rows:
            x = left + (right - left) * ((int(row["year"]) - min_year) / year_span)
            y = bottom + (top - bottom) * ((float(row["ending_balance"]) - min_value) / (max_value - min_value))
            points.extend((x, y))
        colour = palette[series_index % len(palette)]
        if len(points) >= 4:
            from reportlab.graphics.shapes import PolyLine
            drawing.add(PolyLine(points, strokeColor=colour, strokeWidth=1.6))
        legend_x = left + series_index * 82
        drawing.add(Line(legend_x, height - 14, legend_x + 12, height - 14, strokeColor=colour, strokeWidth=2))
        drawing.add(String(legend_x + 15, height - 17, name.title(), fontSize=7))

    return drawing


def _styled_table(rows, *, widths, header=False, font_size=8):
    table = Table(rows, colWidths=widths, repeatRows=1 if header else 0)
    commands = [
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]
    if header:
        commands.extend(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    table.setStyle(TableStyle(commands))
    return table


def _escape_paragraph_text(text: str) -> str:
    """Render existing report text safely inside a ReportLab paragraph."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )
