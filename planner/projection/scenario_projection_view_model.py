"""GUI-neutral view model for retirement scenario comparison screens."""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from .scenario_projection_comparison import ScenarioProjectionComparison
from .scenario_projection_report import ScenarioProjectionReport


@dataclass(frozen=True)
class ScenarioCard:
    """Immutable summary data for one scenario card."""

    name: str
    source: str
    starting_pension: float
    annual_return: float
    ending_balance: float
    total_investment_growth: float
    total_withdrawals: float


@dataclass(frozen=True)
class ScenarioYearRow:
    """Immutable year-level data for a scenario table or chart."""

    scenario: str
    year: int
    starting_balance: float
    investment_growth: float
    withdrawals: float
    ending_balance: float


@dataclass(frozen=True)
class ScenarioProjectionViewModel:
    """Stable, calculation-free data contract for future GUI consumers."""

    scenario_cards: tuple[ScenarioCard, ...]
    year_rows: tuple[ScenarioYearRow, ...]
    lowest_ending_balance: float
    highest_ending_balance: float
    ending_balance_spread: float

    @classmethod
    def from_comparison(
        cls,
        comparison: ScenarioProjectionComparison,
        report: ScenarioProjectionReport | None = None,
    ) -> "ScenarioProjectionViewModel":
        if not isinstance(comparison, ScenarioProjectionComparison):
            raise TypeError("comparison must be ScenarioProjectionComparison")

        presentation = report or ScenarioProjectionReport()
        payload = presentation.build(comparison)

        cards = tuple(
            ScenarioCard(
                name=item["name"],
                source=item["source"],
                starting_pension=item["starting_pension"],
                annual_return=item["annual_return"],
                ending_balance=item["ending_balance"],
                total_investment_growth=item["total_investment_growth"],
                total_withdrawals=item["total_withdrawals"],
            )
            for item in payload["summary"]
        )
        rows = tuple(
            ScenarioYearRow(
                scenario=item["scenario"],
                year=item["year"],
                starting_balance=item["starting_balance"],
                investment_growth=item["investment_growth"],
                withdrawals=item["withdrawals"],
                ending_balance=item["ending_balance"],
            )
            for item in presentation.year_rows(comparison)
        )

        return cls(
            scenario_cards=cards,
            year_rows=rows,
            lowest_ending_balance=payload["lowest_ending_balance"],
            highest_ending_balance=payload["highest_ending_balance"],
            ending_balance_spread=payload["ending_balance_spread"],
        )

    def _report_payload(self) -> dict:
        """Build the calculation-free report representation for this view model."""
        scenarios = []
        for card in self.scenario_cards:
            scenarios.append({
                "name": card.name,
                "source": card.source,
                "starting_pension": card.starting_pension,
                "annual_return": card.annual_return,
                "ending_balance": card.ending_balance,
                "total_investment_growth": card.total_investment_growth,
                "total_withdrawals": card.total_withdrawals,
            })
        return {
            "scenarios": scenarios,
            "summary": [dict(item) for item in scenarios],
            "lowest_ending_balance": self.lowest_ending_balance,
            "highest_ending_balance": self.highest_ending_balance,
            "ending_balance_spread": self.ending_balance_spread,
            "year_rows": [
                {
                    "scenario": row.scenario,
                    "year": row.year,
                    "starting_balance": row.starting_balance,
                    "investment_growth": row.investment_growth,
                    "withdrawals": row.withdrawals,
                    "ending_balance": row.ending_balance,
                }
                for row in self.year_rows
            ],
        }

    @staticmethod
    def _freeze_report_value(value: Any) -> Any:
        """Recursively freeze report data without changing its public shape."""
        if isinstance(value, Mapping):
            return MappingProxyType({
                key: ScenarioProjectionViewModel._freeze_report_value(item)
                for key, item in value.items()
            })
        if isinstance(value, (list, tuple)):
            return tuple(ScenarioProjectionViewModel._freeze_report_value(item) for item in value)
        return value

    def report_snapshot(self) -> Mapping[str, Any]:
        """Return one immutable presentation snapshot for all report consumers."""
        payload = self._report_payload()
        frozen = {
            "payload": self._freeze_report_value(payload),
            "text": self.report_text(),
        }
        return MappingProxyType(frozen)

    def report_payload(self) -> dict:
        """Return a calculation-free report snapshot of the displayed result."""
        return self._report_payload()

    def report_text(self) -> str:
        """Render the displayed result as deterministic calculation-free text."""
        lines = [
            "RETIREMENT SCENARIO COMPARISON",
            "================================",
            "",
            f"{'Scenario':<16}{'Return':>10}{'Ending pension':>20}",
            "-" * 46,
        ]
        for scenario in self.scenario_cards:
            lines.append(
                f"{scenario.name:<16}{scenario.annual_return:>9.1%}"
                f"£{scenario.ending_balance:>19,.0f}"
            )
        lines.extend([
            "",
            f"Starting pension: £{self.scenario_cards[0].starting_pension:,.0f}" if self.scenario_cards else "Starting pension: £0",
            f"Lowest ending balance: £{self.lowest_ending_balance:,.0f}",
            f"Highest ending balance: £{self.highest_ending_balance:,.0f}",
            f"Scenario spread: £{self.ending_balance_spread:,.0f}",
        ])
        return "\n".join(lines)

    @property
    def scenario_names(self) -> tuple[str, ...]:
        return tuple(card.name for card in self.scenario_cards)

    def ending_balance_series(self) -> tuple[tuple[str, float], ...]:
        """Return scenario/end-balance pairs in presentation order."""
        return tuple((card.name, card.ending_balance) for card in self.scenario_cards)
