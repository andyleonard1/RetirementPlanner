"""End-to-end boundary for fund-informed projection scenario selection."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .fund_informed_projection_inputs import FundInformedProjectionInput
from .portfolio_historical_statistics import PortfolioHistoricalStatistics
from .portfolio_scenario_selection import PortfolioScenarioSelector
from .projection_engine_integration import (
    ProjectionEngineIntegration,
    ProjectionReturnDecision,
)


@dataclass(frozen=True)
class FundInformedProjectionDecision:
    """Projection decision plus the selected fund-informed input."""

    projection_return: ProjectionReturnDecision
    fund_input: FundInformedProjectionInput


class FundInformedProjection:
    """Compose typed portfolio statistics, scenario selection and projection."""

    def __init__(
        self,
        scenario_selector: PortfolioScenarioSelector | None = None,
        projection_integration: ProjectionEngineIntegration | None = None,
    ):
        self.scenario_selector = scenario_selector or PortfolioScenarioSelector()
        self.projection_integration = (
            projection_integration or ProjectionEngineIntegration()
        )

    def build_from_statistics(
        self,
        starting_pension: float,
        legacy_return: float,
        statistics: PortfolioHistoricalStatistics,
        scenario_name: str,
    ) -> FundInformedProjectionDecision:
        """Build a fund-informed decision from typed portfolio statistics."""
        fund_input = self.scenario_selector.build_from_statistics(
            starting_pension=starting_pension,
            statistics=statistics,
            scenario_name=scenario_name,
        )
        decision = self.projection_integration.select_return(
            legacy_return=legacy_return,
            fund_input=fund_input,
        )
        return FundInformedProjectionDecision(decision, fund_input)

    def build_legacy(self, legacy_return: float) -> ProjectionReturnDecision:
        """Explicitly retain the pre-fund-informed projection path."""
        return self.projection_integration.select_return(legacy_return)
