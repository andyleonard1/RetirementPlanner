"""Forward portfolio scenarios derived from validated historical statistics."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class PortfolioRiskReturnScenario:
    name: str
    expected_return: float
    volatility: float | None
    source: str
    descriptive: bool = True


class PortfolioRiskReturnScenarioBuilder:
    """Build descriptive forward scenarios without modifying user assumptions.

    The central scenario uses the historical annualised return when available.
    Conservative and optimistic scenarios move one observed volatility unit
    below/above the centre. These are scenario inputs, not guaranteed forecasts.
    """

    def build(
        self,
        portfolio_metrics: Mapping[str, float | None],
    ) -> tuple[PortfolioRiskReturnScenario, ...]:
        required = {"annualised_return", "volatility"}
        missing = required.difference(portfolio_metrics)
        if missing:
            raise ValueError(
                "missing portfolio metrics: " + ", ".join(sorted(missing))
            )

        expected = portfolio_metrics["annualised_return"]
        volatility = portfolio_metrics["volatility"]

        if expected is None:
            raise ValueError("annualised return is required for scenarios")
        expected = float(expected)

        if volatility is not None:
            volatility = float(volatility)
            if volatility < 0:
                raise ValueError("portfolio volatility cannot be negative")

        if volatility is None:
            # Without observed volatility we cannot honestly manufacture a
            # risk-adjusted range. Return the central descriptive scenario only.
            return (
                PortfolioRiskReturnScenario(
                    name="central",
                    expected_return=expected,
                    volatility=None,
                    source="historical annualised return",
                ),
            )

        return (
            PortfolioRiskReturnScenario(
                name="conservative",
                expected_return=expected - volatility,
                volatility=volatility,
                source="historical annualised return minus one historical volatility",
            ),
            PortfolioRiskReturnScenario(
                name="central",
                expected_return=expected,
                volatility=volatility,
                source="historical annualised return",
            ),
            PortfolioRiskReturnScenario(
                name="optimistic",
                expected_return=expected + volatility,
                volatility=volatility,
                source="historical annualised return plus one historical volatility",
            ),
        )
