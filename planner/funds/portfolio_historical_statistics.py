"""Portfolio-level historical statistics from aligned fund observations."""
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Mapping, Sequence


@dataclass(frozen=True)
class PortfolioHistoricalStatistics:
    allocations: tuple[tuple[str, float], ...]
    observation_count: int
    weighted_average_return: float | None
    cumulative_return: float | None
    annualised_return: float | None
    minimum_return: float | None
    maximum_return: float | None
    volatility: float | None
    negative_years: int
    negative_year_rate: float | None
    sufficient_for_volatility: bool
    actual_observation_count: int
    estimated_observation_count: int


class PortfolioHistoricalStatisticsCalculator:
    """Calculate portfolio statistics from aligned annual fund returns.

    Allocations are supplied as decimal weights and must total 1.0. Each fund
    must have the same number of annual observations. Actual/estimated counts
    describe the supplied observations; no missing observations are invented.
    """

    def __init__(self, *, tolerance: float = 1e-9):
        self._tolerance = tolerance

    def calculate(
        self,
        allocations: Mapping[str, float],
        fund_returns: Mapping[str, Sequence[float]],
        *,
        actual_observations: Mapping[str, int] | None = None,
    ) -> PortfolioHistoricalStatistics:
        if not allocations:
            raise ValueError("at least one fund allocation is required")
        if set(allocations) != set(fund_returns):
            raise ValueError("allocations and fund returns must contain the same funds")
        if any(weight < 0 for weight in allocations.values()):
            raise ValueError("portfolio allocations cannot be negative")
        if abs(sum(allocations.values()) - 1.0) > self._tolerance:
            raise ValueError("portfolio allocations must total 1.0")

        histories = {fund: tuple(values) for fund, values in fund_returns.items()}
        lengths = {len(values) for values in histories.values()}
        if not lengths or 0 in lengths:
            raise ValueError("each fund must contain at least one return")
        if len(lengths) != 1:
            raise ValueError("fund return histories must have equal lengths")

        count = next(iter(lengths))
        rates = tuple(
            sum(allocations[fund] * histories[fund][index] for fund in histories)
            for index in range(count)
        )

        mean = sum(rates) / count
        factor = 1.0
        for rate in rates:
            factor *= 1.0 + rate
        cumulative = factor - 1.0
        annualised = factor ** (1.0 / count) - 1.0
        minimum = min(rates)
        maximum = max(rates)

        if count >= 2:
            variance = sum((rate - mean) ** 2 for rate in rates) / (count - 1)
            volatility = sqrt(variance)
        else:
            volatility = None

        negative = sum(rate < 0 for rate in rates)
        actual_counts = actual_observations or {}
        actual_count = sum(int(actual_counts.get(fund, count)) for fund in histories)
        actual_count = min(actual_count, count * len(histories))
        total_observations = count * len(histories)

        return PortfolioHistoricalStatistics(
            allocations=tuple(allocations.items()),
            observation_count=count,
            weighted_average_return=mean,
            cumulative_return=cumulative,
            annualised_return=annualised,
            minimum_return=minimum,
            maximum_return=maximum,
            volatility=volatility,
            negative_years=negative,
            negative_year_rate=negative / count,
            sufficient_for_volatility=volatility is not None,
            actual_observation_count=actual_count,
            estimated_observation_count=total_observations - actual_count,
        )
