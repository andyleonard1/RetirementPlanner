"""Professional PDF presentation for precomputed retirement health data."""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, Mapping

from reportlab.graphics.shapes import Drawing, Line, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from planner.version import VERSION


class HealthCheckPDFReport:
    """Render a calculation-free health dashboard from supplied report data."""

    def create(
        self,
        health: Mapping[str, Any],
        recommendation: Mapping[str, Any],
        monte_carlo: Any,
        summary: Mapping[str, Any],
        filename: str | Path = "RetirementHealthCheck.pdf",
    ) -> Path:
        _validate_inputs(health, recommendation, monte_carlo, summary)

        target = Path(filename)
        target.parent.mkdir(parents=True, exist_ok=True)

        document = SimpleDocTemplate(
            str(target),
            pagesize=A4,
            rightMargin=16 * mm,
            leftMargin=16 * mm,
            topMargin=16 * mm,
            bottomMargin=16 * mm,
            title="Retirement Health Check",
            author="Retirement Planner",
        )

        story = [
            Paragraph("RETIREMENT PLANNER", _style("Title")),
            Paragraph("Health Check Report", _style("Heading2")),
            Spacer(1, 8),
            Paragraph(f"Generated: {date.today()}", _style("Normal")),
            Paragraph(f"Version: {VERSION}", _style("Normal")),
            Spacer(1, 14),
            Paragraph("Executive Dashboard", _style("Heading1")),
            _dashboard_table(health, recommendation, monte_carlo),
            Spacer(1, 14),
            _score_chart(health),
            Spacer(1, 14),
            Paragraph("Projected Position", _style("Heading2")),
            _position_table(summary),
            Spacer(1, 14),
            Paragraph("Monte Carlo Outcome Range", _style("Heading2")),
            _monte_carlo_table(monte_carlo),
            Spacer(1, 14),
            _monte_carlo_chart(monte_carlo),
            Spacer(1, 14),
            Paragraph("Key Strengths / Findings", _style("Heading2")),
            _reasons_table(health.get("reasons", ())),
            Spacer(1, 16),
            Paragraph(
                "Report provenance: this presentation is generated from the supplied health, recommendation, "
                "Monte Carlo and projection-summary data. It performs no financial recalculation and does not "
                "mutate the supplied objects.",
                _style("Normal"),
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
        canvas.drawString(16 * mm, 7 * mm, "Retirement Planner - Health Check Report")
        canvas.drawRightString(width - 16 * mm, 7 * mm, f"Page {canvas.getPageNumber()}")
        canvas.restoreState()


def _validate_inputs(health, recommendation, monte_carlo, summary) -> None:
    if not isinstance(health, Mapping):
        raise TypeError("health must be a mapping")
    if not isinstance(recommendation, Mapping):
        raise TypeError("recommendation must be a mapping")
    if not isinstance(summary, Mapping):
        raise TypeError("summary must be a mapping")
    required_health = ("score", "rating", "reasons")
    missing_health = [key for key in required_health if key not in health]
    if missing_health:
        raise ValueError(f"health is missing required fields: {', '.join(missing_health)}")
    required_recommendation = ("strategy", "confidence")
    missing_recommendation = [
        key for key in required_recommendation if key not in recommendation
    ]
    if missing_recommendation:
        raise ValueError(
            "recommendation is missing required fields: "
            + ", ".join(missing_recommendation)
        )
    required_summary = (
        "ending_assets",
        "ending_pension",
        "ending_isa",
        "ending_savings",
        "total_tax",
    )
    missing_summary = [key for key in required_summary if key not in summary]
    if missing_summary:
        raise ValueError(f"summary is missing required fields: {', '.join(missing_summary)}")
    required_mc = (
        "iterations",
        "minimum",
        "percentile_5",
        "median",
        "percentile_95",
        "maximum",
        "success_rate",
    )
    missing_mc = [key for key in required_mc if not hasattr(monte_carlo, key)]
    if missing_mc:
        raise ValueError(
            "monte_carlo is missing required fields: " + ", ".join(missing_mc)
        )


def _style(name: str):
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    styles = getSampleStyleSheet()
    if name == "Normal":
        return ParagraphStyle("HealthNormal", parent=styles["Normal"], fontSize=8.5, leading=11)
    return styles[name]


def _dashboard_table(health, recommendation, monte_carlo) -> Table:
    rows = [
        ["Health score", f"{float(health['score']):.1f} / 10"],
        ["Health rating", str(health["rating"])],
        ["Success probability", f"{float(monte_carlo.success_rate):.1f}%"],
        ["Recommended strategy", str(recommendation["strategy"])],
        ["Recommendation confidence", str(recommendation["confidence"])],
    ]
    return _table(rows, [74 * mm, 91 * mm])


def _position_table(summary: Mapping[str, Any]) -> Table:
    rows = [
        ["Projected estate", _currency(summary["ending_assets"])],
        ["Projected pension", _currency(summary["ending_pension"])],
        ["Projected ISA", _currency(summary["ending_isa"])],
        ["Projected savings", _currency(summary["ending_savings"])],
        ["Lifetime tax", _currency(summary["total_tax"])],
    ]
    return _table(rows, [74 * mm, 91 * mm])


def _monte_carlo_table(monte_carlo) -> Table:
    rows = [
        ["Iterations", f"{int(monte_carlo.iterations):,}"],
        ["Minimum ending assets", _currency(monte_carlo.minimum)],
        ["5th percentile", _currency(monte_carlo.percentile_5)],
        ["Median", _currency(monte_carlo.median)],
        ["95th percentile", _currency(monte_carlo.percentile_95)],
        ["Maximum ending assets", _currency(monte_carlo.maximum)],
        ["Success rate", f"{float(monte_carlo.success_rate):.1f}%"],
    ]
    return _table(rows, [74 * mm, 91 * mm])


def _reasons_table(reasons) -> Table:
    if not reasons:
        reasons = ("No health findings were supplied.",)
    rows = [[f"{index}.", _paragraph(reason)] for index, reason in enumerate(reasons, start=1)]
    return _table(rows, [10 * mm, 155 * mm])


def _score_chart(health) -> Drawing:
    width, height = 170 * mm, 22 * mm
    drawing = Drawing(width, height)
    score = max(0.0, min(10.0, float(health["score"])))
    x0, y0, bar_width, bar_height = 8, 7, width - 16, 10
    drawing.add(Rect(x0, y0, bar_width, bar_height, fillColor=colors.whitesmoke, strokeColor=colors.grey))
    drawing.add(
        Rect(
            x0,
            y0,
            bar_width * (score / 10.0),
            bar_height,
            fillColor=colors.darkblue,
            strokeColor=colors.darkblue,
        )
    )
    drawing.add(String(x0, height - 5, "Overall retirement health score", fontName="Helvetica-Bold", fontSize=8))
    drawing.add(String(x0 + bar_width - 22, height - 5, f"{score:.1f}/10", fontSize=8))
    return drawing


def _monte_carlo_chart(monte_carlo) -> Drawing:
    width, height = 170 * mm, 32 * mm
    drawing = Drawing(width, height)
    x0, x1, y0, y1 = 12, width - 12, 8, height - 12
    minimum = float(monte_carlo.minimum)
    maximum = float(monte_carlo.maximum)
    if maximum <= minimum:
        maximum = minimum + 1.0

    def x(value):
        return x0 + (float(value) - minimum) / (maximum - minimum) * (x1 - x0)

    drawing.add(String(0, height - 5, "Ending-assets distribution landmarks", fontName="Helvetica-Bold", fontSize=8))
    drawing.add(Line(x0, y0, x1, y0, strokeColor=colors.grey))

    for value, label in (
        (monte_carlo.minimum, "Min"),
        (monte_carlo.percentile_5, "5th"),
        (monte_carlo.median, "Median"),
        (monte_carlo.percentile_95, "95th"),
        (monte_carlo.maximum, "Max"),
    ):
        px = x(value)
        drawing.add(Line(px, y0, px, y1, strokeColor=colors.darkblue, strokeWidth=1))
        drawing.add(String(max(0, px - 8), y0 - 8, label, fontSize=6))
        drawing.add(String(max(0, px - 15), y1 + 1, _short_currency(value), fontSize=6))
    return drawing


def _table(rows, widths) -> Table:
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


def _paragraph(value) -> Paragraph:
    return Paragraph(_escape(str(value)), _style("Normal"))


def _currency(value) -> str:
    return f"£{float(value):,.0f}"


def _short_currency(value) -> str:
    value = float(value)
    if abs(value) >= 1_000_000:
        return f"£{value / 1_000_000:.1f}m"
    if abs(value) >= 1_000:
        return f"£{value / 1_000:.0f}k"
    return f"£{value:.0f}"


def _escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )
