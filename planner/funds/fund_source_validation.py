"""Validation and provenance checks for imported fund source data."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .fund_import import ImportedFundReturn


@dataclass(frozen=True)
class FundSourceValidation:
    valid: bool
    record_count: int
    fund_count: int
    first_year: int | None
    last_year: int | None
    duplicate_years: tuple[tuple[str, int], ...]


class FundSourceValidator:
    """Validate imported records before they enter risk/projection engines."""

    def validate(
        self,
        records: Iterable[ImportedFundReturn],
    ) -> FundSourceValidation:
        values = tuple(records)

        seen: set[tuple[str, int]] = set()
        duplicates: set[tuple[str, int]] = set()

        for record in values:
            key = (record.fund_identifier, record.year)
            if key in seen:
                duplicates.add(key)
            seen.add(key)

        years = [record.year for record in values]
        funds = {record.fund_identifier for record in values}

        return FundSourceValidation(
            valid=not duplicates,
            record_count=len(values),
            fund_count=len(funds),
            first_year=min(years) if years else None,
            last_year=max(years) if years else None,
            duplicate_years=tuple(sorted(duplicates)),
        )
