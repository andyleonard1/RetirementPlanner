"""GUI-neutral view model for retirement scenario comparison screens."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

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

    @property
    def scenario_names(self) -> tuple[str, ...]:
        return tuple(card.name for card in self.scenario_cards)

    def ending_balance_series(self) -> tuple[tuple[str, float], ...]:
        """Return scenario/end-balance pairs in presentation order."""
        return tuple((card.name, card.ending_balance) for card in self.scenario_cards)
