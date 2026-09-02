"""Presentation model for comparing complete retirement projections."""
from __future__ import annotations

from .projection_result_adapter import ProjectionResultReportAdapter
from .scenario_projection_comparison import ScenarioProjectionComparison


class ScenarioProjectionReport:
    """Produce deterministic, calculation-free scenario comparison output."""

    def __init__(self, adapter: ProjectionResultReportAdapter | None = None):
        self.adapter = adapter or ProjectionResultReportAdapter()

    def build(self, comparison: ScenarioProjectionComparison) -> dict:
        """Return a stable report payload suitable for console, PDF or GUI consumers."""
        payload = self.adapter.build(comparison)
        summaries = []
        for scenario in payload["scenarios"]:
            summaries.append(
                {
                    "name": scenario["name"],
                    "source": scenario["source"],
                    "starting_pension": scenario["starting_pension"],
                    "annual_return": scenario["annual_return"],
                    "ending_balance": scenario["ending_balance"],
                    "total_investment_growth": scenario["total_investment_growth"],
                    "total_withdrawals": scenario["total_withdrawals"],
                }
            )
        payload["summary"] = summaries
        return payload

    def render_text(self, comparison: ScenarioProjectionComparison) -> str:
        """Render a compact human-readable comparison without doing calculations."""
        report = self.build(comparison)
        lines = [
            "RETIREMENT SCENARIO COMPARISON",
            "================================",
            "",
            f"{'Scenario':<16}{'Return':>10}{'Ending pension':>20}",
            "-" * 46,
        ]
        for scenario in report["summary"]:
            lines.append(
                f"{scenario['name']:<16}"
                f"{scenario['annual_return']:>9.1%}"
                f"£{scenario['ending_balance']:>19,.0f}"
            )
        lines.extend(
            [
                "",
                f"Starting pension: £{report['scenarios'][0]['starting_pension']:,.0f}" if report["scenarios"] else "Starting pension: £0",
                f"Lowest ending balance: £{report['lowest_ending_balance']:,.0f}",
                f"Highest ending balance: £{report['highest_ending_balance']:,.0f}",
                f"Scenario spread: £{report['ending_balance_spread']:,.0f}",
            ]
        )
        return "\n".join(lines)

    def year_rows(self, comparison: ScenarioProjectionComparison) -> list[dict]:
        """Return flattened year/scenario rows for tabular or chart consumers."""
        report = self.build(comparison)
        rows = []
        for scenario in report["scenarios"]:
            for year in scenario["years"]:
                rows.append(
                    {
                        "scenario": scenario["name"],
                        "year": year["year"],
                        "starting_balance": year["starting_balance"],
                        "investment_growth": year["investment_growth"],
                        "withdrawals": year["withdrawals"],
                        "ending_balance": year["ending_balance"],
                    }
                )
        return rows
