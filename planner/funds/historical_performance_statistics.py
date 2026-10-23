"""Historical performance statistics derived from stored fund returns."""
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Iterable

from .historical_fund_returns import HistoricalFundReturn


@dataclass(frozen=True)
class HistoricalPerformanceStatistics:
    fund_identifier: str
    observation_count: int
    actual_observation_count: int
    estimated_observation_count: int
    cumulative_return: float | None
    annualised_return: float | None
    minimum_return: float | None
    maximum_return: float | None
    volatility: float | None
    sufficient_for_volatility: bool
    source_observations: tuple[HistoricalFundReturn, ...]


class HistoricalPerformanceStatisticsCalculator:
    """Calculate statistics without fabricating missing observations.

    Volatility uses sample standard deviation and requires at least two
    observations. Annualised return requires at least one annual observation.
    """

    def calculate(
        self,
        fund_identifier: str,
        observations: Iterable[HistoricalFundReturn],
        *,
        actual_only: bool = False,
    ) -> HistoricalPerformanceStatistics:
        items = tuple(
            item for item in observations
            if item.fund_identifier == fund_identifier
            and (not actual_only or item.data_type == "actual")
        )

        if not items:
            return HistoricalPerformanceStatistics(
                fund_identifier=fund_identifier,
                observation_count=0,
                actual_observation_count=0,
                estimated_observation_count=0,
                cumulative_return=None,
                annualised_return=None,
                minimum_return=None,
                maximum_return=None,
                volatility=None,
                sufficient_for_volatility=False,
                source_observations=(),
            )

        ordered = tuple(sorted(items, key=lambda item: item.year))
        values = tuple(item.return_rate for item in ordered)
        actual_count = sum(item.data_type == "actual" for item in ordered)
        estimated_count = len(ordered) - actual_count

        cumulative_factor = 1.0
        for value in values:
            cumulative_factor *= 1.0 + value
        cumulative = cumulative_factor - 1.0

        years = len(values)
        annualised = cumulative_factor ** (1.0 / years) - 1.0

        minimum = min(values)
        maximum = max(values)

        volatility = None
        if len(values) >= 2:
            mean = sum(values) / len(values)
            variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
            volatility = sqrt(variance)

        return HistoricalPerformanceStatistics(
            fund_identifier=fund_identifier,
            observation_count=len(ordered),
            actual_observation_count=actual_count,
            estimated_observation_count=estimated_count,
            cumulative_return=cumulative,
            annualised_return=annualised,
            minimum_return=minimum,
            maximum_return=maximum,
            volatility=volatility,
            sufficient_for_volatility=volatility is not None,
            source_observations=ordered,
        )
