"""
PDF Report

Creates a professional retirement planning report from the current
PlannerResult / ScenarioManager reporting architecture.
"""

from datetime import date
from pathlib import Path

from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from planner.version import VERSION


class PDFReport:

    def create(
        self,
        result,
        decision=None,
        age_comparison=None,
        filename="RetirementReport.pdf",
        sensitivity=None,
        driver_analysis=None,
    ):
        """Create a PDF from the current planner result and scenario data."""

        styles = getSampleStyleSheet()
        document = SimpleDocTemplate(filename)
        story = []
        summary = result.summary

        story.append(Paragraph("<b>RETIREMENT PLANNER</b>", styles["Title"]))
        story.append(Paragraph("Professional Retirement Projection", styles["Heading2"]))
        story.append(Spacer(1, 18))
        story.append(Paragraph(f"Generated: {date.today()}", styles["Normal"]))
        story.append(Paragraph(f"Version: {VERSION}", styles["Normal"]))
        story.append(Spacer(1, 20))

        story.append(Paragraph("<b>Retirement Decision</b>", styles["Heading2"]))

        if decision is not None:
            story.append(Paragraph(
                f"<b>Recommended retirement age:</b> {decision.recommended_age}",
                styles["Normal"],
            ))
            story.append(Paragraph(
                f"<b>Overall recommendation score:</b> "
                f"{decision.total_score:.1f}/100"
                if decision.total_score is not None
                else "<b>Overall recommendation score:</b> Not available",
                styles["Normal"],
            ))

            if decision.later_age is not None and decision.later_ending_assets is not None:
                story.append(Paragraph(
                    f"Retiring at age {decision.later_age} would project "
                    f"£{decision.later_ending_assets:,.0f} of ending assets.",
                    styles["Normal"],
                ))

            if decision.additional_assets_from_waiting is not None:
                story.append(Paragraph(
                    f"Projected change from waiting one year: "
                    f"£{decision.additional_assets_from_waiting:,.0f}.",
                    styles["Normal"],
                ))
        else:
            story.append(Paragraph(
                "No retirement-age decision was available.",
                styles["Normal"],
            ))

        story.append(Spacer(1, 12))
        story.append(Paragraph(
            f"<b>Withdrawal strategy:</b> {summary['strategy']}",
            styles["Normal"],
        ))
        story.append(Paragraph(
            f"<b>Plan status:</b> {'Sustainable' if result.success else 'Not sustainable'}",
            styles["Normal"],
        ))

        if summary.get("failure_reason"):
            story.append(Paragraph(
                f"<b>Failure reason:</b> {summary['failure_reason']}",
                styles["Normal"],
            ))

        story.append(Spacer(1, 20))

        story.append(Paragraph("<b>Configuration Changes</b>", styles["Heading2"]))
        assumption_changes = getattr(result, "assumption_changes", ())
        if assumption_changes:
            for change in assumption_changes:
                category = getattr(
                    result, "audit_context", "user"
                ).replace("_", " ").upper()
                description = getattr(
                    change, "description", None
                )
                if description is None:
                    description = (
                        f"Assumption '{change.path}' changed for this projection."
                    )
                before = getattr(change, "before_display", change.before)
                after = getattr(change, "after_display", change.after)
                story.append(Paragraph(
                    f"<b>[{category}]</b> {description}",
                    styles["Normal"],
                ))
                story.append(Paragraph(
                    f"{change.path}: {before} -> {after}",
                    styles["Normal"],
                ))
        else:
            story.append(Paragraph(
                "No configuration changes were detected for this projection.",
                styles["Normal"],
            ))
        story.append(Paragraph("<b>Optimisation Decision Support</b>", styles["Heading2"]))
        optimisation = getattr(result, "optimisation_decision", None)
        if optimisation is not None:
            story.append(Paragraph(optimisation.recommendation, styles["Normal"]))
            story.append(Paragraph(optimisation.explanation, styles["Normal"]))
            story.append(Paragraph(
                f"<b>Practical impact:</b> {'MATERIAL' if optimisation.material else 'NOT MATERIAL'}",
                styles["Normal"],
            ))
        else:
            story.append(Paragraph(
                "No optimisation decision support is available.",
                styles["Normal"],
            ))
        story.append(Spacer(1, 20))

        if sensitivity is not None:
            story.append(Paragraph("<b>Recommendation Sensitivity</b>", styles["Heading2"]))
            story.append(Paragraph(
                f"The recommendation was tested across {sensitivity.total_cases} assumption cases.",
                styles["Normal"],
            ))

            if sensitivity.min_age is not None and sensitivity.max_age is not None:
                story.append(Paragraph(
                    f"Recommended-age range: {sensitivity.min_age} to {sensitivity.max_age}.",
                    styles["Normal"],
                ))

            if sensitivity.most_common_age is not None:
                story.append(Paragraph(
                    f"Most common recommendation: age {sensitivity.most_common_age} "
                    f"({sensitivity.most_common_count} of {sensitivity.total_cases} cases).",
                    styles["Normal"],
                ))

            counts = {}
            for run in sensitivity.runs:
                if run.recommended_age is not None:
                    counts[run.recommended_age] = counts.get(run.recommended_age, 0) + 1

            if counts:
                rows = [["Recommended Age", "Cases", "Share"]]
                for age in sorted(counts):
                    count = counts[age]
                    rows.append([str(age), str(count), f"{count / sensitivity.total_cases:.0%}"])

                sensitivity_table = Table(
                    rows,
                    colWidths=[120, 100, 100],
                )
                sensitivity_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                    ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ]))
                story.append(Spacer(1, 8))
                story.append(sensitivity_table)

            story.append(Spacer(1, 12))
            story.append(Paragraph(
                "Sensitivity analysis is informational only and does not change the live recommendation.",
                styles["Normal"],
            ))
            story.append(Spacer(1, 20))

        if driver_analysis:
            story.append(Paragraph("<b>Sensitivity Drivers</b>", styles["Heading2"]))
            story.append(Paragraph(
                "The tables below show how the recommended age varied within each tested assumption dimension.",
                styles["Normal"],
            ))

            rows = [["Assumption", "Value", "Recommended ages"]]
            labels = {
                "pension_growth": "Pension growth",
                "net_spending": "Net spending",
                "isa_growth": "ISA growth",
            }

            for analysis in driver_analysis:
                for value, ages in analysis.groups:
                    unique = sorted({age for age in ages if age is not None})
                    age_text = ", ".join(str(age) for age in unique) if unique else "No successful recommendation"
                    if analysis.dimension.endswith("growth"):
                        value_text = f"{value:.0%}"
                    else:
                        value_text = f"£{value:,.0f}"
                    rows.append([labels.get(analysis.dimension, analysis.dimension), value_text, age_text])

            driver_table = Table(rows, colWidths=[130, 90, 200])
            driver_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ]))
            story.append(Spacer(1, 8))
            story.append(driver_table)
            story.append(Spacer(1, 20))

        if age_comparison:
            story.append(Paragraph("<b>Retirement Age Comparison</b>", styles["Heading2"]))
            rows = [["Age", "Status", "Ending Assets", "Change"]]
            for comparison in age_comparison:
                rows.append([
                    str(comparison.retirement_age),
                    "SUCCESS" if comparison.success else "NOT SUSTAINABLE",
                    f"£{comparison.ending_assets:,.0f}",
                    "-" if comparison.change_from_previous_age is None
                    else f"£{comparison.change_from_previous_age:,.0f}",
                ])
            table = Table(rows, colWidths=[55, 125, 130, 100])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
            ]))
            story.append(table)
            story.append(Spacer(1, 20))

        story.append(Paragraph("<b>Pension Value</b>", styles["Heading2"]))
        story.append(Image("charts/pension.png", width=450, height=225))
        story.append(Spacer(1, 20))

        story.append(Paragraph("<b>Total Assets</b>", styles["Heading2"]))
        story.append(Image("charts/assets.png", width=450, height=225))
        story.append(Spacer(1, 20))

        story.append(Paragraph("<b>Projected Position at Age 90</b>", styles["Heading2"]))
        rows = [
            ["Financial Summary", ""],
            ["Total Assets", f"£{summary['ending_assets']:,.0f}"],
            ["Pension Remaining", f"£{summary['ending_pension']:,.0f}"],
            ["ISA Remaining", f"£{summary['ending_isa']:,.0f}"],
            ["Savings Remaining", f"£{summary['ending_savings']:,.0f}"],
            ["Lifetime Tax", f"£{summary['total_tax']:,.0f}"],
        ]
        table = Table(rows, colWidths=[250, 150])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ("ALIGN", (1, 1), (1, -1), "RIGHT"),
        ]))
        story.append(table)

        document.build(story)
        print(f"PDF created: {filename}")
