"""Fund-informed projection inputs for RC4 Sprint 71."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class FundProjectionScenario:
    """A projection scenario derived from observed portfolio characteristics."""

    name: str
    expected_return: float
    volatility: float
    minimum_return: float
    maximum_return: float


class FundProjectionBuilder:
    """Build conservative projection scenarios without replacing the base model."""

    def build(
        self,
        portfolio_metrics: Mapping[str, float],
        *,
        name: str = "fund_informed",
    ) -> FundProjectionScenario:
        required = {
            "weighted_average_return",
            "portfolio_volatility",
        }
        missing = required.difference(portfolio_metrics)
        if missing:
            raise ValueError(
                "missing portfolio metrics: " + ", ".join(sorted(missing))
            )

        expected = float(portfolio_metrics["weighted_average_return"])
        volatility = float(portfolio_metrics["portfolio_volatility"])

        if volatility < 0:
            raise ValueError("portfolio volatility cannot be negative")

        # Scenario bounds are deliberately descriptive rather than a forecast
        # guarantee. They provide inputs for later projection/Monte Carlo work.
        return FundProjectionScenario(
            name=name,
            expected_return=expected,
            volatility=volatility,
            minimum_return=expected - volatility,
            maximum_return=expected + volatility,
        )
