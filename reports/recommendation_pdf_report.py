"""Professional PDF presentation for a precomputed recommendation report."""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Mapping, Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from planner.version import VERSION


class RecommendationPDFReport:
    """Render a calculation-free PDF from an already-built recommendation report."""

    def create(
        self,
        report: Mapping[str, Any],
        filename: str | Path = "RetirementRecommendation.pdf",
    ) -> Path:
        if not isinstance(report, Mapping):
            raise TypeError("report must be a mapping")
        _validate_report(report)

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
            title="Retirement Recommendation Report",
            author="Retirement Planner",
        )

        story = [
            Paragraph("RETIREMENT PLANNER", styles["Title"]),
            Paragraph("Recommendation Report", styles["Heading2"]),
            Spacer(1, 8),
            Paragraph(f"Generated: {date.today()}", styles["Normal"]),
            Paragraph(f"Version: {VERSION}", styles["Normal"]),
            Spacer(1, 16),
            Paragraph("Recommendation Summary", styles["Heading2"]),
            _summary_table(report),
            Spacer(1, 16),
            Paragraph("Why this recommendation?", styles["Heading2"]),
            _reasons_table(report.get("reasons", [])),
            Spacer(1, 16),
            Paragraph("Projected Position", styles["Heading2"]),
            _position_table(report),
            Spacer(1, 16),
            KeepTogether(
                [
                    Paragraph("Retirement Risk", styles["Heading2"]),
                    _risk_table(report),
                ]
            ),
        ]

        overall = report.get("overall_recommendation")
        optimisation = report.get("optimisation_decision")
        changes = report.get("assumption_changes", [])

        if overall or optimisation:
            story.extend([Paragraph("Decision Support", styles["Heading1"]), Spacer(1, 8)])

            if overall:
                story.extend(
                    [
                        Paragraph("Overall Retirement Strategy", styles["Heading2"]),
                        Paragraph(_escape(overall.get("message", "")), styles["Normal"]),
                        Spacer(1, 6),
                        Paragraph(_escape(overall.get("impact", "")), styles["Normal"]),
                        Spacer(1, 16),
                    ]
                )

            if optimisation:
                story.extend(
                    [
                        Paragraph("Optimisation Decision Support", styles["Heading2"]),
                        _optimisation_table(optimisation),
                        Spacer(1, 16),
                    ]
                )

        if changes:
            story.extend(
                [
                    PageBreak(),
                    Paragraph("Configuration Changes", styles["Heading1"]),
                    Spacer(1, 8),
                    _changes_table(changes),
                    Spacer(1, 16),
                ]
            )

        story.extend(
            [
                Paragraph("Recommendation Confidence", styles["Heading2"]),
                Paragraph(_escape(str(report["confidence"])), styles["Normal"]),
                Spacer(1, 16),
                Paragraph(
                    "Report provenance: this presentation is generated from the supplied recommendation report data. "
                    "It performs no financial recalculation and does not mutate the source report.",
                    styles["Normal"],
                ),
            ]
        )

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
        canvas.drawString(16 * mm, 7 * mm, "Retirement Planner — Recommendation Report")
        canvas.drawRightString(width - 16 * mm, 7 * mm, f"Page {canvas.getPageNumber()}")
        canvas.restoreState()


def _validate_report(report: Mapping[str, Any]) -> None:
    required = (
        "strategy",
        "confidence",
        "reasons",
        "ending_assets",
        "ending_pension",
        "ending_isa",
        "ending_savings",
        "total_tax",
        "risk_rating",
        "risk_score",
        "risk_messages",
        "recommended_age",
        "recommendation_score",
    )
    missing = [key for key in required if key not in report]
    if missing:
        raise ValueError(f"report is missing required fields: {', '.join(missing)}")


def _summary_table(report: Mapping[str, Any]) -> Table:
    rows = [
        ["Recommended strategy", str(report["strategy"])],
        ["Recommended retirement age", str(report["recommended_age"])],
        ["Recommendation score", f"{float(report['recommendation_score']):.1f}"],
        ["Confidence", str(report["confidence"])],
    ]
    return _table(rows, widths=[74 * mm, 91 * mm])


def _reasons_table(reasons) -> Table:
    rows = [[f"{index}.", _cell(reason)] for index, reason in enumerate(reasons, start=1)]
    if not rows:
        rows = [["", _cell("No recommendation reasons were supplied.")]]
    return _table(rows, widths=[10 * mm, 155 * mm])


def _position_table(report: Mapping[str, Any]) -> Table:
    rows = [
        ["Total assets", _currency(report["ending_assets"])],
        ["Pension", _currency(report["ending_pension"])],
        ["ISA", _currency(report["ending_isa"])],
        ["Savings", _currency(report["ending_savings"])],
        ["Lifetime tax", _currency(report["total_tax"])],
    ]
    return _table(rows, widths=[74 * mm, 91 * mm])


def _risk_table(report: Mapping[str, Any]) -> Table:
    rows = [
        ["Overall risk", str(report["risk_rating"])],
        ["Risk score", f"{report['risk_score']}/10"],
    ]
    for message in report.get("risk_messages", []):
        rows.append(["Risk message", _escape(str(message))])
    return _table(rows, widths=[42 * mm, 123 * mm])


def _optimisation_table(optimisation: Mapping[str, Any]) -> Table:
    rows = [
        ["Higher policy", _cell(optimisation["higher_policy"])],
        ["Lower policy", _cell(optimisation["lower_policy"])],
        ["Average difference", _cell(_currency(optimisation["average_difference"]))],
        ["Maximum difference", _cell(_currency(optimisation["maximum_difference"]))],
        ["Maximum difference age", _cell(optimisation["maximum_difference_age"])],
        ["Material", _cell(optimisation["material"])],
        ["Recommendation", _cell(optimisation["recommendation"])],
        ["Explanation", _cell(optimisation["explanation"])],
    ]
    return _table(rows, widths=[55 * mm, 110 * mm])


def _changes_table(changes) -> Table:
    rows = [["Category", "Path", "Before", "After"]]
    for change in changes:
        rows.append(
            [
                _cell(change.get("category", "USER ASSUMPTION")),
                _cell(change.get("description", change.get("path", ""))),
                _cell(change.get("before_display", change.get("before", "not set"))),
                _cell(change.get("after_display", change.get("after", "not set"))),
            ]
        )
    table = Table(rows, repeatRows=1, colWidths=[35 * mm, 65 * mm, 32 * mm, 33 * mm])
    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


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


def _currency(value) -> str:
    return f"£{float(value):,.0f}"


def _cell(value) -> Paragraph:
    style = ParagraphStyle(
        "RecommendationCell",
        parent=getSampleStyleSheet()["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        spaceAfter=0,
    )
    return Paragraph(_escape(str(value)), style)


def _escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")
