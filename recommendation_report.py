"""
Recommendation report.
"""

from reports.report_utils import (
    heading,
    section,
    currency,
)


class RecommendationReport:

    def print(self, report):

        heading("RETIREMENT PLANNER")

        section("Recommended Strategy")
        print(report["strategy"])

        section("Overall Retirement Strategy")
        overall = report.get("overall_recommendation")
        if overall:
            print(overall["message"])
            print(overall["impact"])
        else:
            print("No combined retirement strategy recommendation is available.")

        section("Why this strategy?")
        for reason in report["reasons"]:
            print(f"[OK] {reason}")

        section("Recommendation Confidence")
        print(report["confidence"])

        section("Optimisation Decision Support")
        optimisation = report.get("optimisation_decision")
        if optimisation:
            print(optimisation["recommendation"])
            print(optimisation["explanation"])
            if optimisation.get("material"):
                print("Practical impact: MATERIAL")
            else:
                print("Practical impact: NOT MATERIAL")
        else:
            print("No optimisation decision support is available.")

        section("Configuration Changes")
        changes = report.get("assumption_changes", [])
        if changes:
            for change in changes:
                before = change.get("before_display", change.get("before"))
                after = change.get("after_display", change.get("after"))
                print(
                    f"[CHANGED] [{change.get('category', 'USER ASSUMPTION')}] "
                    f"{change.get('description', change['path'])}"
                )
                print(f"          {change['path']}: {before} -> {after}")
        else:
            print("No configuration changes detected for this projection.")

        section("Projected position at age 90")
        print(f"Total Assets      {currency(report['ending_assets'])}")
        print(f"Pension           {currency(report['ending_pension'])}")
        print(f"ISA               {currency(report['ending_isa'])}")
        print(f"Savings           {currency(report['ending_savings'])}")
        print(f"Lifetime Tax      {currency(report['total_tax'])}")

        section("Retirement Risk")
        print(f"Overall Risk : {report['risk_rating']}")
        print(f"Risk Score   : {report['risk_score']}/10")

        print()
        for message in report["risk_messages"]:
            print(f"[OK] {message}")


print()
