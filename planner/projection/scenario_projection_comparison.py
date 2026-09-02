"""Compare complete fund-informed retirement projections by scenario."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from planner.funds.portfolio_historical_statistics import PortfolioHistoricalStatistics
from planner.planner import RetirementPlanner

from .structured_projection_results import (
    ProjectionYearResult,
    StructuredProjectionResult,
    StructuredProjectionResultBuilder,
)


@dataclass(frozen=True)
class ScenarioProjectionComparison:
    """Immutable collection of complete projections for supported scenarios."""

    projections: tuple[StructuredProjectionResult, ...]

    def __post_init__(self) -> None:
        names = tuple(p.scenario_name for p in self.projections)
        if len(names) != len(set(names)):
            raise ValueError("scenario names must be unique")
        if not self.projections:
            raise ValueError("at least one scenario projection is required")

    @property
    def scenario_names(self) -> tuple[str, ...]:
        return tuple(p.scenario_name for p in self.projections)

    @property
    def ending_balances(self) -> Mapping[str, float]:
        return {p.scenario_name: p.ending_balance for p in self.projections}

    @property
    def highest_ending_balance(self) -> float:
        return max(self.ending_balances.values())

    @property
    def lowest_ending_balance(self) -> float:
        return min(self.ending_balances.values())

    @property
    def ending_balance_spread(self) -> float:
        return self.highest_ending_balance - self.lowest_ending_balance

    def get(self, scenario_name: str) -> StructuredProjectionResult:
        name = str(scenario_name).strip().lower()
        for projection in self.projections:
            if projection.scenario_name == name:
                return projection
        raise KeyError(name)


class ScenarioProjectionComparisonRunner:
    """Run supported portfolio scenarios and convert them to presentation results."""

    DEFAULT_SCENARIOS = ("conservative", "central", "optimistic")

    def __init__(
        self,
        result_builder: StructuredProjectionResultBuilder | None = None,
    ) -> None:
        self.result_builder = result_builder or StructuredProjectionResultBuilder()

    def run(
        self,
        *,
        assumptions,
        statistics: PortfolioHistoricalStatistics,
        scenarios: Iterable[str] = DEFAULT_SCENARIOS,
    ) -> ScenarioProjectionComparison:
        if not isinstance(statistics, PortfolioHistoricalStatistics):
            raise TypeError("statistics must be PortfolioHistoricalStatistics")

        names = tuple(dict.fromkeys(str(name).strip().lower() for name in scenarios))
        if not names:
            raise ValueError("at least one scenario is required")

        projections = []
        for name in names:
            planner = RetirementPlanner(assumptions)
            result = planner.run_with_portfolio_statistics(statistics, name)
            decision = planner.projection_return_decision
            if decision is None or not decision.fund_informed:
                raise ValueError("scenario projection did not produce a fund-informed decision")

            rows = tuple(
                ProjectionYearResult(
                    year=int(year.calendar_year),
                    starting_balance=float(year.opening_pension),
                    investment_growth=float(year.pension_growth),
                    withdrawals=float(year.pension_withdrawal),
                    ending_balance=float(year.closing_pension),
                )
                for year in result.timeline
            )

            projections.append(
                self.result_builder.build(
                    scenario_name=name,
                    source=decision.source,
                    starting_pension=float(assumptions.get("starting_pension")),
                    annual_return=float(decision.expected_return),
                    rows=rows,
                )
            )

        return ScenarioProjectionComparison(tuple(projections))
