"""Fund-history suitability checks for RC4 Sprint 76."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .fund_data_quality import FundDataQualityAnalyzer
from .fund_import import ImportedFundReturn


@dataclass(frozen=True)
class FundHistorySuitability:
    fund_identifier: str
    suitable_for_risk_metrics: bool
    suitable_for_projection: bool
    reason: str


class FundHistorySuitabilityAnalyzer:
    """Decide whether available history is adequate for specific modelling uses."""

    def __init__(
        self,
        *,
        risk_minimum_years: int = 5,
        projection_minimum_years: int = 10,
    ):
        if risk_minimum_years < 1 or projection_minimum_years < 1:
            raise ValueError("minimum history requirements must be at least 1")
        self.risk_minimum_years = risk_minimum_years
        self.projection_minimum_years = projection_minimum_years

    def analyze(
        self,
        records: Iterable[ImportedFundReturn],
    ) -> tuple[FundHistorySuitability, ...]:
        records = tuple(records)
        quality = FundDataQualityAnalyzer(
            minimum_history_years=self.risk_minimum_years
        ).analyze(records)

        results = []
        for item in quality:
            risk_ok = (
                item.coverage_rate == 1.0
                and item.record_count >= self.risk_minimum_years
            )
            projection_ok = (
                risk_ok
                and item.record_count >= self.projection_minimum_years
            )

            if projection_ok:
                reason = "sufficient continuous history for risk and projection modelling"
            elif risk_ok:
                reason = "sufficient continuous history for risk metrics only"
            elif item.missing_years:
                reason = "historical series contains missing years"
            else:
                reason = "insufficient historical data for risk modelling"

            results.append(
                FundHistorySuitability(
                    fund_identifier=item.fund_identifier,
                    suitable_for_risk_metrics=risk_ok,
                    suitable_for_projection=projection_ok,
                    reason=reason,
                )
            )

        return tuple(results)
