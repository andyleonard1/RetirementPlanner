"""Select a validated portfolio scenario for retirement projection."""
from __future__ import annotations

from typing import Iterable, Mapping

from .fund_informed_projection_inputs import (
    FundInformedProjectionInput,
    FundInformedProjectionInputBuilder,
)
from .portfolio_historical_statistics import PortfolioHistoricalStatistics
from .portfolio_risk_return_scenarios import (
    PortfolioRiskReturnScenario,
    PortfolioRiskReturnScenarioBuilder,
)


class PortfolioScenarioSelector:
    """Select projection scenarios without mutating user assumptions."""

    VALID_NAMES = {"conservative", "central", "optimistic"}

    def __init__(
        self,
        scenario_builder: PortfolioRiskReturnScenarioBuilder | None = None,
        input_builder: FundInformedProjectionInputBuilder | None = None,
    ):
        self.scenario_builder = scenario_builder or PortfolioRiskReturnScenarioBuilder()
        self.input_builder = input_builder or FundInformedProjectionInputBuilder()

    def _select(
        self,
        starting_pension: float,
        portfolio_metrics: Mapping[str, float | None],
        scenario_name: str,
        fund_allocation: Iterable[tuple[str, float]],
    ) -> FundInformedProjectionInput:
        name = str(scenario_name).strip().lower()
        if name not in self.VALID_NAMES:
            raise ValueError(
                "scenario_name must be one of: "
                + ", ".join(sorted(self.VALID_NAMES))
            )

        scenarios = self.scenario_builder.build(portfolio_metrics)
        selected = next((s for s in scenarios if s.name == name), None)
        if selected is None:
            raise ValueError(
                f"scenario '{name}' is not available from the supplied portfolio data"
            )

        return self.input_builder.build(starting_pension, selected, fund_allocation)

    def build(
        self,
        starting_pension: float,
        portfolio_metrics: Mapping[str, float | None],
        scenario_name: str,
        fund_allocation: Iterable[tuple[str, float]],
    ) -> FundInformedProjectionInput:
        return self._select(
            starting_pension, portfolio_metrics, scenario_name, fund_allocation
        )

    def build_from_statistics(
        self,
        starting_pension: float,
        statistics: PortfolioHistoricalStatistics,
        scenario_name: str,
    ) -> FundInformedProjectionInput:
        """Select directly from typed portfolio statistics.

        This is the preferred application boundary.  The selector owns the
        mapping from the statistics object to the scenario builder, while the
        projection layer never needs to know dictionary field names.
        """
        if not isinstance(statistics, PortfolioHistoricalStatistics):
            raise TypeError("statistics must be PortfolioHistoricalStatistics")
        metrics = {
            "annualised_return": statistics.annualised_return,
            "volatility": statistics.volatility,
        }
        return self._select(
            starting_pension,
            metrics,
            scenario_name,
            statistics.allocations,
        )

    def available_scenarios(
        self,
        portfolio_metrics: Mapping[str, float | None],
    ) -> tuple[PortfolioRiskReturnScenario, ...]:
        return self.scenario_builder.build(portfolio_metrics)

    def available_scenarios_from_statistics(
        self,
        statistics: PortfolioHistoricalStatistics,
    ) -> tuple[PortfolioRiskReturnScenario, ...]:
        if not isinstance(statistics, PortfolioHistoricalStatistics):
            raise TypeError("statistics must be PortfolioHistoricalStatistics")
        return self.scenario_builder.build(
            {
                "annualised_return": statistics.annualised_return,
                "volatility": statistics.volatility,
            }
        )
