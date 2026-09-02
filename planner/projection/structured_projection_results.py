"""Structured, GUI-ready projection result models."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class ProjectionYearResult:
    year: int
    starting_balance: float
    investment_growth: float
    withdrawals: float
    ending_balance: float


@dataclass(frozen=True)
class StructuredProjectionResult:
    scenario_name: str
    source: str
    starting_pension: float
    annual_return: float
    years: tuple[ProjectionYearResult, ...]

    @property
    def ending_balance(self) -> float:
        return self.years[-1].ending_balance if self.years else self.starting_pension

    @property
    def total_investment_growth(self) -> float:
        return sum(row.investment_growth for row in self.years)

    @property
    def total_withdrawals(self) -> float:
        return sum(row.withdrawals for row in self.years)


class StructuredProjectionResultBuilder:
    """Build a stable presentation model from projection-year records."""

    def build(
        self,
        *,
        scenario_name: str,
        source: str,
        starting_pension: float,
        annual_return: float,
        rows: Iterable[ProjectionYearResult],
    ) -> StructuredProjectionResult:
        if starting_pension < 0:
            raise ValueError("starting_pension cannot be negative")

        materialised = tuple(rows)
        previous = starting_pension

        for row in materialised:
            if row.starting_balance != previous:
                raise ValueError("projection years are not balance-contiguous")
            if row.investment_growth < 0 and annual_return >= 0:
                # Negative growth is valid only when explicitly represented by
                # a negative annual return; prevents inconsistent result models.
                raise ValueError("investment growth conflicts with annual return")
            previous = row.ending_balance

        return StructuredProjectionResult(
            scenario_name=str(scenario_name),
            source=str(source),
            starting_pension=float(starting_pension),
            annual_return=float(annual_return),
            years=materialised,
        )
