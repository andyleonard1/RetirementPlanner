from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping, Sequence
from .portfolio_risk_calculation import PortfolioRiskCalculationService

@dataclass(frozen=True)
class PortfolioRiskMetrics:
    weighted_average_return: float
    portfolio_volatility: float
    included_funds: tuple[str, ...]
    excluded_funds: tuple[str, ...]
    exclusion_reasons: tuple[tuple[str, str], ...]
    calculation_available: bool
    reason: str

class PortfolioRiskMetricsCalculator:
    def __init__(self, *, risk_minimum_years=5, projection_minimum_years=10):
        self._service=PortfolioRiskCalculationService(risk_minimum_years=risk_minimum_years, projection_minimum_years=projection_minimum_years)
    def calculate(self, allocations: Mapping[str,float], fund_returns: Mapping[str,Sequence[float]]) -> PortfolioRiskMetrics:
        result=self._service.calculate(allocations, fund_returns)
        summary=result.summary
        if summary is None:
            return PortfolioRiskMetrics(0.0,0.0,result.included_funds,result.excluded_funds,result.exclusion_reasons,False,result.reason)
        return PortfolioRiskMetrics(summary.weighted_average_return,summary.portfolio_volatility,result.included_funds,result.excluded_funds,result.exclusion_reasons,result.calculated,result.reason)
