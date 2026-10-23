"""Presentation model for comparing complete retirement projections."""
from __future__ import annotations

from typing import Any, Mapping

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

    @staticmethod
    def _validate_snapshot(snapshot: Mapping[str, Any]) -> Mapping[str, Any]:
        """Validate the minimum immutable report-snapshot contract without recalculating."""
        if not isinstance(snapshot, Mapping):
            raise TypeError("snapshot must be a mapping")
        if not isinstance(snapshot.get("payload"), Mapping):
            raise TypeError("snapshot payload must be a mapping")
        if not isinstance(snapshot.get("text"), str):
            raise TypeError("snapshot text must be a string")
        payload = snapshot["payload"]
        required = {
            "scenarios",
            "summary",
            "lowest_ending_balance",
            "highest_ending_balance",
            "ending_balance_spread",
            "year_rows",
        }
        missing = required.difference(payload)
        if missing:
            raise ValueError(f"snapshot payload is missing fields: {sorted(missing)}")
        return snapshot

    def build_from_snapshot(self, snapshot: Mapping[str, Any]) -> dict:
        """Return a defensive payload copy from a published GUI result snapshot.

        This is deliberately calculation-free: it consumes the already-published
        presentation snapshot rather than reconstructing a comparison object.
        """
        self._validate_snapshot(snapshot)
        return self._mutable_value(snapshot["payload"])

    @classmethod
    def render_text_from_snapshot(cls, snapshot: Mapping[str, Any]) -> str:
        """Return the published deterministic report text without rebuilding it."""
        cls._validate_snapshot(snapshot)
        return str(snapshot["text"])

    def year_rows_from_snapshot(self, snapshot: Mapping[str, Any]) -> list[dict]:
        """Return defensive year-row copies from a published result snapshot."""
        payload = self.build_from_snapshot(snapshot)
        return payload["year_rows"]

    @staticmethod
    def _mutable_value(value: Any) -> Any:
        if isinstance(value, Mapping):
            return {key: ScenarioProjectionReport._mutable_value(item) for key, item in value.items()}
        if isinstance(value, tuple):
            return [ScenarioProjectionReport._mutable_value(item) for item in value]
        return value

    def render_text(self, comparison: ScenarioProjectionComparison) -> str:
        """Render a compact human-readable comparison without doing calculations."""
        report = self.build(comparison)
        return self._render_payload_text(report)

    @staticmethod
    def _render_payload_text(report: Mapping[str, Any]) -> str:
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
