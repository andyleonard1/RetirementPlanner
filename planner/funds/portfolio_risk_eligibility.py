"""Portfolio-level integration of fund risk eligibility."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .fund_import import ImportedFundReturn
from .fund_risk_eligibility import FundRiskEligibilityAnalyzer


@dataclass(frozen=True)
class PortfolioRiskEligibility:
    included_funds: tuple[str, ...]
    excluded_funds: tuple[str, ...]
    exclusion_reasons: tuple[tuple[str, str], ...]


class PortfolioRiskEligibilityIntegrator:
    """Produce an auditable inclusion/exclusion set for portfolio risk."""

    def __init__(self, *, risk_minimum_years: int = 5,
                 projection_minimum_years: int = 10):
        self._analyzer = FundRiskEligibilityAnalyzer(
            risk_minimum_years=risk_minimum_years,
            projection_minimum_years=projection_minimum_years,
        )

    def evaluate(self, records: Iterable[ImportedFundReturn]) -> PortfolioRiskEligibility:
        eligibility = self._analyzer.analyze(records)
        included = tuple(item.fund_identifier for item in eligibility if item.eligible)
        excluded = tuple(item.fund_identifier for item in eligibility if not item.eligible)
        reasons = tuple(
            (item.fund_identifier, item.reason)
            for item in eligibility if not item.eligible
        )
        return PortfolioRiskEligibility(included, excluded, reasons)

    def filter_records(self, records: Iterable[ImportedFundReturn]) -> tuple[ImportedFundReturn, ...]:
        records = tuple(records)
        included = set(self.evaluate(records).included_funds)
        return tuple(r for r in records if r.fund_identifier in included)
