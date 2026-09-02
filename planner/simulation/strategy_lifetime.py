"""Lifetime aggregation for withdrawal strategy comparisons."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .withdrawal_strategy_comparison import StrategyOutcome


@dataclass(frozen=True)
class LifetimeStrategyResult:
    name: str
    total_tax: float
    total_net_income: float
    total_tax_free_cash: float
    years: int


class LifetimeStrategyAggregator:
    """Aggregate yearly strategy outcomes into lifetime metrics."""

    def aggregate(
        self,
        name: str,
        yearly_outcomes: Iterable[StrategyOutcome],
    ) -> LifetimeStrategyResult:
        values = tuple(yearly_outcomes)
        if not values:
            raise ValueError("at least one yearly outcome is required")

        return LifetimeStrategyResult(
            name=name,
            total_tax=sum(v.tax_paid for v in values),
            total_net_income=sum(v.net_income for v in values),
            total_tax_free_cash=sum(v.tax_free_cash for v in values),
            years=len(values),
        )
