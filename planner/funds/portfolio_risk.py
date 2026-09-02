"""Portfolio-level risk metrics for RC4 Sprint 70."""
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Mapping, Sequence


@dataclass(frozen=True)
class PortfolioRiskSummary:
    weighted_average_return: float
    portfolio_volatility: float
    negative_years: int
    negative_year_rate: float
    maximum_drawdown: float
    downside_deviation: float


class PortfolioRiskAnalyzer:
    """Calculate portfolio-level historical risk from aligned fund returns.

    ``allocations`` maps fund names to portfolio weights expressed as decimals.
    ``fund_returns`` maps fund names to a sequence of annual returns. All funds
    must contain the same number of observations and are assumed to be aligned
    by year/order.
    """

    def __init__(
        self,
        allocations: Mapping[str, float],
        fund_returns: Mapping[str, Sequence[float]],
    ):
        if not allocations:
            raise ValueError("at least one fund allocation is required")

        if set(allocations) != set(fund_returns):
            raise ValueError("allocations and fund returns must contain the same funds")

        total = sum(allocations.values())
        if abs(total - 1.0) > 1e-9:
            raise ValueError("portfolio allocations must total 1.0")

        if any(weight < 0 for weight in allocations.values()):
            raise ValueError("portfolio allocations cannot be negative")

        lengths = {len(values) for values in fund_returns.values()}
        if not lengths or 0 in lengths:
            raise ValueError("each fund must contain at least one return")
        if len(lengths) != 1:
            raise ValueError("fund return histories must have equal lengths")

        self.allocations = dict(allocations)
        self.fund_returns = {
            name: tuple(values) for name, values in fund_returns.items()
        }

    def _portfolio_returns(self) -> tuple[float, ...]:
        years = len(next(iter(self.fund_returns.values())))
        return tuple(
            sum(
                self.allocations[name] * self.fund_returns[name][index]
                for name in self.fund_returns
            )
            for index in range(years)
        )

    def summary(self) -> PortfolioRiskSummary:
        rates = self._portfolio_returns()
        mean = sum(rates) / len(rates)

        if len(rates) == 1:
            volatility = 0.0
        else:
            variance = sum((rate - mean) ** 2 for rate in rates) / (len(rates) - 1)
            volatility = sqrt(variance)

        negative = [rate for rate in rates if rate < 0]

        wealth = 1.0
        peak = 1.0
        maximum_drawdown = 0.0
        for rate in rates:
            wealth *= 1.0 + rate
            peak = max(peak, wealth)
            maximum_drawdown = max(
                maximum_drawdown,
                (peak - wealth) / peak,
            )

        downside_deviation = sqrt(
            sum(min(0.0, rate) ** 2 for rate in rates) / len(rates)
        )

        return PortfolioRiskSummary(
            weighted_average_return=mean,
            portfolio_volatility=volatility,
            negative_years=len(negative),
            negative_year_rate=len(negative) / len(rates),
            maximum_drawdown=maximum_drawdown,
            downside_deviation=downside_deviation,
        )
