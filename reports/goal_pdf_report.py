"""Professional PDF presentation for precomputed retirement-goal results."""
from __future__ import annotations

import html
from datetime import date
from pathlib import Path
from typing import Any, Mapping, Sequence

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from planner.version import VERSION


class GoalPDFReport:
    """Render a calculation-free PDF from already-evaluated goal results."""

    def create(
        self,
        goals: Sequence[Mapping[str, Any]],
        filename: str | Path = "RetirementGoals.pdf",
    ) -> Path:
        _validate_goals(goals)

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
            title="Retirement Goals Report",
            author="Retirement Planner",
        )

        achieved = sum(1 for goal in goals if bool(goal["passed"]))
        total = len(goals)

        story = [
            Paragraph("RETIREMENT PLANNER", styles["Title"]),
            Paragraph("Retirement Goals Report", styles["Heading2"]),
            Spacer(1, 8),
            Paragraph(f"Generated: {date.today()}", styles["Normal"]),
            Paragraph(f"Version: {VERSION}", styles["Normal"]),
            Spacer(1, 14),
            Paragraph("Goals Summary", styles["Heading2"]),
            _summary_table(achieved, total),
            Spacer(1, 14),
            Paragraph("Goal Status", styles["Heading2"]),
            _goals_table(goals),
            Spacer(1, 14),
            Paragraph("Status Overview", styles["Heading2"]),
            _status_drawing(achieved, total),
            Spacer(1, 12),
            Paragraph(
                "Report provenance: this presentation is generated from the supplied goal-evaluation data. "
                "It performs no financial recalculation and does not mutate the source goal results.",
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
        canvas.drawString(16 * mm, 7 * mm, "Retirement Planner — Goals Report")
        canvas.drawRightString(width - 16 * mm, 7 * mm, f"Page {canvas.getPageNumber()}")
        canvas.restoreState()


def _validate_goals(goals: Sequence[Mapping[str, Any]]) -> None:
    if not isinstance(goals, Sequence) or isinstance(goals, (str, bytes)):
        raise TypeError("goals must be a sequence of mappings")

    for index, goal in enumerate(goals):
        if not isinstance(goal, Mapping):
            raise TypeError(f"goals[{index}] must be a mapping")
        missing = [key for key in ("name", "passed", "target", "actual") if key not in goal]
        if missing:
            raise ValueError(
                f"goals[{index}] is missing required fields: {', '.join(missing)}"
            )


def _summary_table(achieved: int, total: int) -> Table:
    ratio = f"{achieved}/{total}" if total else "0/0"
    status = "All evaluated goals achieved" if achieved == total else "Some evaluated goals not yet achieved"
    rows = [
        ["Goals achieved", ratio],
        ["Status", status],
    ]
    return _table(rows, widths=[62 * mm, 103 * mm])


def _goals_table(goals: Sequence[Mapping[str, Any]]) -> Table:
    rows = [["Status", "Goal", "Constraint", "Target", "Actual"]]
    for goal in goals:
        marker = "ACHIEVED" if goal["passed"] else "NOT ACHIEVED"
        rows.append(
            [
                _cell(marker),
                _cell(goal["name"]),
                _cell(goal.get("operator", "")),
                _cell(goal["target"]),
                _cell(goal["actual"]),
            ]
        )
    if len(rows) == 1:
        rows.append([_cell(""), _cell("No goals were evaluated."), _cell(""), _cell(""), _cell("")])

    table = Table(rows, repeatRows=1, colWidths=[28 * mm, 55 * mm, 25 * mm, 29 * mm, 28 * mm])
    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def _status_drawing(achieved: int, total: int) -> Drawing:
    width = 165 * mm
    height = 21 * mm
    drawing = Drawing(width, height)

    x = 0
    if total:
        achieved_width = width * (achieved / total)
        drawing.add(Rect(x, 8 * mm, achieved_width, 8 * mm, fillColor=colors.darkgreen, strokeColor=None))
        if achieved_width < width:
            drawing.add(Rect(achieved_width, 8 * mm, width - achieved_width, 8 * mm, fillColor=colors.whitesmoke, strokeColor=colors.lightgrey))
    else:
        drawing.add(Rect(0, 8 * mm, width, 8 * mm, fillColor=colors.whitesmoke, strokeColor=colors.lightgrey))

    drawing.add(String(0, 0, f"{achieved} of {total} goals achieved"))
    return drawing


def _table(rows, *, widths) -> Table:
    table = Table(rows, colWidths=widths)
    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def _cell(value: Any) -> Paragraph:
    style = ParagraphStyle(
        "GoalCell",
        parent=getSampleStyleSheet()["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        spaceAfter=0,
    )
    return Paragraph(_escape(str(value)), style)


def _escape(value: str) -> str:
    return html.escape(value).replace("\n", "<br/>")
