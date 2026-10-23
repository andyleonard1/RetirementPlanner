"""Explicit, explainable fund suitability decisions for RC4 Sprint 77."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .fund_history_suitability import FundHistorySuitabilityAnalyzer
from .fund_import import ImportedFundReturn


@dataclass(frozen=True)
class FundSuitabilityDecision:
    fund_identifier: str
    risk_modelling: bool
    projection_modelling: bool
    status: str
    reason: str


class FundSuitabilityDecisionEngine:
    """Convert history-suitability results into a stable decision contract."""

    def __init__(
        self,
        *,
        risk_minimum_years: int = 5,
        projection_minimum_years: int = 10,
    ):
        self._analyzer = FundHistorySuitabilityAnalyzer(
            risk_minimum_years=risk_minimum_years,
            projection_minimum_years=projection_minimum_years,
        )

    def decide(
        self,
        records: Iterable[ImportedFundReturn],
    ) -> tuple[FundSuitabilityDecision, ...]:
        suitability = self._analyzer.analyze(records)
        decisions = []

        for item in suitability:
            if item.suitable_for_projection:
                status = "suitable_for_risk_and_projection"
                reason = (
                    "Fund history is sufficient and continuous for both "
                    "risk and fund-informed projection modelling."
                )
            elif item.suitable_for_risk_metrics:
                status = "suitable_for_risk_only"
                reason = (
                    "Fund history is sufficient for risk metrics but does "
                    "not meet the projection-history requirement."
                )
            else:
                status = "not_suitable"
                reason = item.reason

            decisions.append(
                FundSuitabilityDecision(
                    fund_identifier=item.fund_identifier,
                    risk_modelling=item.suitable_for_risk_metrics,
                    projection_modelling=item.suitable_for_projection,
                    status=status,
                    reason=reason,
                )
            )

        return tuple(decisions)
