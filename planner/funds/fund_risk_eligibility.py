"""Fund risk-analysis eligibility for RC4 Sprint 78."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .fund_import import ImportedFundReturn
from .fund_suitability_decision import (
    FundSuitabilityDecision,
    FundSuitabilityDecisionEngine,
)


@dataclass(frozen=True)
class FundRiskEligibility:
    fund_identifier: str
    eligible: bool
    reason: str


class FundRiskEligibilityAnalyzer:
    """Translate fund suitability decisions into explicit risk eligibility."""

    def __init__(
        self,
        *,
        risk_minimum_years: int = 5,
        projection_minimum_years: int = 10,
    ):
        self._decision_engine = FundSuitabilityDecisionEngine(
            risk_minimum_years=risk_minimum_years,
            projection_minimum_years=projection_minimum_years,
        )

    def analyze(
        self,
        records: Iterable[ImportedFundReturn],
    ) -> tuple[FundRiskEligibility, ...]:
        decisions = self._decision_engine.decide(records)
        return tuple(
            FundRiskEligibility(
                fund_identifier=decision.fund_identifier,
                eligible=decision.risk_modelling,
                reason=(
                    "Eligible for risk analysis."
                    if decision.risk_modelling
                    else f"Excluded from risk analysis: {decision.reason}"
                ),
            )
            for decision in decisions
        )

    def eligible_funds(
        self,
        records: Iterable[ImportedFundReturn],
    ) -> tuple[str, ...]:
        return tuple(
            item.fund_identifier
            for item in self.analyze(records)
            if item.eligible
        )
