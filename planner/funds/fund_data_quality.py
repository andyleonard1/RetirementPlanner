"""Historical fund-data quality and coverage checks for RC4 Sprint 75."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from .fund_import import ImportedFundReturn

@dataclass(frozen=True)
class FundDataQuality:
    fund_identifier: str
    record_count: int
    first_year: int | None
    last_year: int | None
    expected_years: int
    missing_years: tuple[int, ...]
    coverage_rate: float
    sufficient_history: bool

class FundDataQualityAnalyzer:
    def __init__(self, minimum_history_years: int = 5):
        if minimum_history_years < 1:
            raise ValueError("minimum_history_years must be at least 1")
        self.minimum_history_years = minimum_history_years

    def analyze(self, records: Iterable[ImportedFundReturn]) -> tuple[FundDataQuality, ...]:
        grouped: dict[str, list[ImportedFundReturn]] = {}
        for record in records:
            grouped.setdefault(record.fund_identifier, []).append(record)
        results=[]
        for fund_identifier, values in sorted(grouped.items()):
            years=sorted({r.year for r in values}); first=years[0]; last=years[-1]
            expected=last-first+1
            missing=tuple(y for y in range(first,last+1) if y not in years)
            coverage=len(years)/expected
            results.append(FundDataQuality(fund_identifier,len(values),first,last,expected,missing,coverage,len(years)>=self.minimum_history_years and not missing))
        return tuple(results)
