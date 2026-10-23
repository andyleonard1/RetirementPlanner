"""Compare pension withdrawal strategies for RC4 Sprint 65."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class StrategyOutcome:
    name: str
    gross_pension: float
    tax_paid: float
    tax_free_cash: float
    net_income: float


@dataclass(frozen=True)
class StrategyComparison:
    strategies: tuple[StrategyOutcome, ...]
    lowest_tax_strategy: str
    highest_net_income_strategy: str
    tax_saving_vs_highest_tax: float


class WithdrawalStrategyComparator:
    """Compare already-calculated withdrawal strategies.

    The comparator does not calculate UK tax itself. It consumes strategy
    outcomes produced by the existing tax/withdrawal engines.
    """

    def compare(
        self,
        outcomes: Iterable[StrategyOutcome],
    ) -> StrategyComparison:
        values = tuple(outcomes)
        if not values:
            raise ValueError("at least one strategy outcome is required")

        for outcome in values:
            if outcome.gross_pension < 0:
                raise ValueError("gross_pension cannot be negative")
            if outcome.tax_paid < 0:
                raise ValueError("tax_paid cannot be negative")
            if outcome.tax_free_cash < 0:
                raise ValueError("tax_free_cash cannot be negative")

        lowest_tax = min(values, key=lambda x: x.tax_paid)
        highest_tax = max(values, key=lambda x: x.tax_paid)
        highest_net = max(values, key=lambda x: x.net_income)

        return StrategyComparison(
            strategies=values,
            lowest_tax_strategy=lowest_tax.name,
            highest_net_income_strategy=highest_net.name,
            tax_saving_vs_highest_tax=(
                highest_tax.tax_paid - lowest_tax.tax_paid
            ),
        )
