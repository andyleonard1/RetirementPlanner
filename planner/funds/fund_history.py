"""Historical fund-performance infrastructure for RC4 Sprint 68."""
from __future__ import annotations

from dataclasses import dataclass
from math import prod
from typing import Iterable


@dataclass(frozen=True)
class AnnualFundReturn:
    year: int
    return_rate: float


@dataclass(frozen=True)
class FundHistorySummary:
    years: int
    arithmetic_mean: float
    annualised_return: float
    best_return: float
    worst_return: float


class FundHistory:
    """Store and summarise annual historical fund returns."""

    def __init__(self, returns: Iterable[AnnualFundReturn]):
        values = tuple(returns)
        if not values:
            raise ValueError("at least one historical return is required")

        years = [item.year for item in values]
        if len(set(years)) != len(years):
            raise ValueError("historical return years must be unique")

        self.returns = values

    def summary(self) -> FundHistorySummary:
        rates = [item.return_rate for item in self.returns]
        arithmetic_mean = sum(rates) / len(rates)
        compounded = prod(1.0 + rate for rate in rates)
        annualised = compounded ** (1.0 / len(rates)) - 1.0

        return FundHistorySummary(
            years=len(rates),
            arithmetic_mean=arithmetic_mean,
            annualised_return=annualised,
            best_return=max(rates),
            worst_return=min(rates),
        )
