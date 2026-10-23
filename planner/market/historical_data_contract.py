"""Validation contract for historical annual market-return observations.

This module defines an integration boundary only. It does not load live data,
change the existing CSV adapter, or feed observations into projection engines.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable, Literal

ObservationStatus = Literal["actual", "estimated"]
ReturnBasis = Literal["nominal", "real"]


@dataclass(frozen=True, slots=True)
class HistoricalReturnObservation:
    """One annual observation with explicit units and source provenance.

    Rates are decimals (for example, 0.052 means 5.2%), and annual returns
    are total returns for the named calendar year. Inflation is a decimal rate.
    """

    year: int
    equity_return: float
    bond_return: float
    inflation_rate: float
    source_id: str
    source_name: str
    status: ObservationStatus = "actual"
    currency: str = "GBP"
    return_basis: ReturnBasis = "nominal"
    source_url: str | None = None


@dataclass(frozen=True, slots=True)
class HistoricalSeriesContract:
    """Series-level metadata and explicit missing-year policy."""

    series_id: str
    description: str
    currency: str = "GBP"
    return_basis: ReturnBasis = "nominal"
    missing_year_policy: Literal["reject", "allow_gaps"] = "reject"


def validate_observation(observation: HistoricalReturnObservation) -> list[str]:
    """Return all contract violations for one observation, without coercion."""
    errors: list[str] = []
    if isinstance(observation.year, bool) or not isinstance(observation.year, int):
        errors.append("year must be an integer calendar year")
    elif not 1800 <= observation.year <= 2200:
        errors.append("year must be between 1800 and 2200")

    for field_name in ("equity_return", "bond_return", "inflation_rate"):
        value = getattr(observation, field_name)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
            errors.append(f"{field_name} must be a finite numeric decimal rate")
        elif value <= -1.0:
            errors.append(f"{field_name} must be greater than -1.0")

    if not isinstance(observation.source_id, str) or not observation.source_id.strip():
        errors.append("source_id must be non-empty")
    if not isinstance(observation.source_name, str) or not observation.source_name.strip():
        errors.append("source_name must be non-empty")
    if observation.status not in ("actual", "estimated"):
        errors.append("status must be 'actual' or 'estimated'")
    if observation.return_basis not in ("nominal", "real"):
        errors.append("return_basis must be 'nominal' or 'real'")
    if not isinstance(observation.currency, str) or len(observation.currency.strip()) != 3:
        errors.append("currency must be a three-character currency code")
    if observation.source_url is not None and not isinstance(observation.source_url, str):
        errors.append("source_url must be a string or None")
    return errors


def validate_series(
    observations: Iterable[HistoricalReturnObservation],
    contract: HistoricalSeriesContract,
) -> list[str]:
    """Validate series metadata, observation consistency, duplicates and gaps."""
    items = list(observations)
    errors: list[str] = []
    if not contract.series_id.strip():
        errors.append("series_id must be non-empty")
    if not contract.description.strip():
        errors.append("description must be non-empty")
    if contract.return_basis not in ("nominal", "real"):
        errors.append("series return_basis must be 'nominal' or 'real'")
    if contract.missing_year_policy not in ("reject", "allow_gaps"):
        errors.append("missing_year_policy must be 'reject' or 'allow_gaps'")

    years: list[int] = []
    for index, item in enumerate(items):
        for error in validate_observation(item):
            errors.append(f"observation[{index}]: {error}")
        if isinstance(item.year, int) and not isinstance(item.year, bool):
            years.append(item.year)
        if item.currency != contract.currency:
            errors.append(f"observation[{index}]: currency differs from series contract")
        if item.return_basis != contract.return_basis:
            errors.append(f"observation[{index}]: return_basis differs from series contract")

    seen: set[int] = set()
    for year in years:
        if year in seen:
            errors.append(f"duplicate calendar year: {year}")
        seen.add(year)
    if contract.missing_year_policy == "reject" and years:
        ordered = sorted(seen)
        missing = [year for year in range(ordered[0], ordered[-1] + 1) if year not in seen]
        if missing:
            errors.append("missing calendar years: " + ", ".join(map(str, missing)))
    return errors
