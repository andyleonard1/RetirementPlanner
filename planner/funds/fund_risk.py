from __future__ import annotations
from dataclasses import dataclass
from math import sqrt
from typing import Iterable
from .fund_history import AnnualFundReturn

@dataclass(frozen=True)
class FundRiskSummary:
    volatility: float
    negative_years: int
    negative_year_rate: float
    maximum_drawdown: float
    downside_deviation: float

class FundRiskAnalyzer:
    def __init__(self, returns: Iterable[AnnualFundReturn]):
        values = tuple(returns)
        if not values:
            raise ValueError("at least one historical return is required")
        self.returns = values

    def summary(self) -> FundRiskSummary:
        rates = [item.return_rate for item in self.returns]
        mean = sum(rates) / len(rates)
        if len(rates) == 1:
            volatility = 0.0
        else:
            variance = sum((r - mean) ** 2 for r in rates) / (len(rates) - 1)
            volatility = sqrt(variance)

        negative = [r for r in rates if r < 0]

        wealth = 1.0
        peak = 1.0
        max_drawdown = 0.0
        for rate in rates:
            wealth *= 1.0 + rate
            peak = max(peak, wealth)
            max_drawdown = max(max_drawdown, (peak - wealth) / peak)

        downside_deviation = sqrt(
            sum(min(0.0, r) ** 2 for r in rates) / len(rates)
        )

        return FundRiskSummary(
            volatility=volatility,
            negative_years=len(negative),
            negative_year_rate=len(negative) / len(rates),
            maximum_drawdown=max_drawdown,
            downside_deviation=downside_deviation,
        )
