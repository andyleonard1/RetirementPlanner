"""Eligibility-aware portfolio risk calculation for RC4 Sprint 80."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

from .fund_import import ImportedFundReturn
from .portfolio_risk import PortfolioRiskAnalyzer, PortfolioRiskSummary
from .portfolio_risk_eligibility import PortfolioRiskEligibilityIntegrator


@dataclass(frozen=True)
class PortfolioRiskCalculation:
    """Auditable result of an eligibility-aware risk calculation."""

    calculated: bool
    summary: PortfolioRiskSummary | None
    included_funds: tuple[str, ...]
    excluded_funds: tuple[str, ...]
    exclusion_reasons: tuple[tuple[str, str], ...]
    reason: str


class PortfolioRiskCalculationService:
    """Apply eligibility before allowing the existing risk engine to calculate.

    An incomplete/ineligible portfolio is deliberately not re-weighted or
    silently repaired. The caller receives an explicit blocked result instead.
    """

    def __init__(
        self,
        *,
        risk_minimum_years: int = 5,
        projection_minimum_years: int = 10,
    ):
        self._eligibility = PortfolioRiskEligibilityIntegrator(
            risk_minimum_years=risk_minimum_years,
            projection_minimum_years=projection_minimum_years,
        )

    def calculate(
        self,
        allocations: Mapping[str, float],
        fund_returns: Mapping[str, Sequence[float]],
    ) -> PortfolioRiskCalculation:
        records = tuple(
            ImportedFundReturn(fund, year, value)
            for fund, values in fund_returns.items()
            for year, value in enumerate(values)
        )
        eligibility = self._eligibility.evaluate(records)

        if eligibility.excluded_funds:
            return PortfolioRiskCalculation(
                calculated=False,
                summary=None,
                included_funds=eligibility.included_funds,
                excluded_funds=eligibility.excluded_funds,
                exclusion_reasons=eligibility.exclusion_reasons,
                reason=(
                    "Portfolio risk calculation blocked because one or more "
                    "funds are not eligible for risk analysis."
                ),
            )

        summary = PortfolioRiskAnalyzer(allocations, fund_returns).summary()
        return PortfolioRiskCalculation(
            calculated=True,
            summary=summary,
            included_funds=eligibility.included_funds,
            excluded_funds=eligibility.excluded_funds,
            exclusion_reasons=eligibility.exclusion_reasons,
            reason="Portfolio risk calculation completed using eligible funds.",
        )
