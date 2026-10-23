"""Provider-neutral historical data adapter and versioned fixture loader.

This module intentionally has no live provider and is not connected to planner
or projection engines. It establishes a typed seam for future historical replay.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Sequence, runtime_checkable

from planner.market.historical_data_contract import (
    HistoricalReturnObservation,
    HistoricalSeriesContract,
    validate_series,
)

FIXTURE_FORMAT = "retirement-planner-historical-series"
SUPPORTED_FIXTURE_VERSION = 1


@dataclass(frozen=True, slots=True)
class HistoricalSeriesDataset:
    """Validated series payload returned by an adapter."""

    contract: HistoricalSeriesContract
    observations: tuple[HistoricalReturnObservation, ...]
    format_version: int = SUPPORTED_FIXTURE_VERSION


@runtime_checkable
class HistoricalDataSourceAdapter(Protocol):
    """Future adapter contract; implementations must not silently fill gaps."""

    def load_series(self, series_id: str) -> HistoricalSeriesDataset:
        """Load and validate a named historical series or raise an error."""
        ...


class HistoricalFixtureError(ValueError):
    """Raised when a versioned historical fixture is malformed or invalid."""


def _require_object(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise HistoricalFixtureError(f"{label} must be a JSON object")
    return value


def _strict_keys(value: dict[str, object], required: set[str], optional: set[str], label: str) -> None:
    missing = sorted(required - value.keys())
    unknown = sorted(value.keys() - required - optional)
    if missing:
        raise HistoricalFixtureError(f"{label} missing required keys: {', '.join(missing)}")
    if unknown:
        raise HistoricalFixtureError(f"{label} has unknown keys: {', '.join(unknown)}")


def load_historical_fixture(path: str | Path) -> HistoricalSeriesDataset:
    """Load a strict version-1 JSON fixture and validate it without coercion."""
    try:
        with Path(path).open(encoding="utf-8") as stream:
            payload = json.load(stream)
    except (OSError, json.JSONDecodeError) as exc:
        raise HistoricalFixtureError(f"cannot read historical fixture: {exc}") from exc

    root = _require_object(payload, "fixture")
    _strict_keys(root, {"format", "format_version", "contract", "observations"}, set(), "fixture")
    if root["format"] != FIXTURE_FORMAT:
        raise HistoricalFixtureError(f"format must be {FIXTURE_FORMAT!r}")
    version = root["format_version"]
    if isinstance(version, bool) or not isinstance(version, int) or version != SUPPORTED_FIXTURE_VERSION:
        raise HistoricalFixtureError(f"unsupported format_version: {version!r}")

    raw_contract = _require_object(root["contract"], "contract")
    _strict_keys(
        raw_contract,
        {"series_id", "description", "currency", "return_basis", "missing_year_policy"},
        set(),
        "contract",
    )
    try:
        contract = HistoricalSeriesContract(**raw_contract)  # type: ignore[arg-type]
    except TypeError as exc:
        raise HistoricalFixtureError(f"invalid contract fields: {exc}") from exc

    raw_observations = root["observations"]
    if not isinstance(raw_observations, list):
        raise HistoricalFixtureError("observations must be a JSON array")
    observations: list[HistoricalReturnObservation] = []
    required = {
        "year", "equity_return", "bond_return", "inflation_rate", "source_id",
        "source_name", "status", "currency", "return_basis",
    }
    for index, raw in enumerate(raw_observations):
        item = _require_object(raw, f"observations[{index}]")
        _strict_keys(item, required, {"source_url"}, f"observations[{index}]")
        try:
            observations.append(HistoricalReturnObservation(**item))  # type: ignore[arg-type]
        except TypeError as exc:
            raise HistoricalFixtureError(f"invalid observation[{index}] fields: {exc}") from exc

    errors = validate_series(observations, contract)
    if errors:
        raise HistoricalFixtureError("invalid historical series: " + "; ".join(errors))
    return HistoricalSeriesDataset(contract, tuple(observations), int(version))


def validate_dataset(dataset: HistoricalSeriesDataset) -> None:
    """Raise a clear error if a constructed adapter dataset violates contract."""
    if dataset.format_version != SUPPORTED_FIXTURE_VERSION:
        raise HistoricalFixtureError(f"unsupported format_version: {dataset.format_version!r}")
    errors = validate_series(dataset.observations, dataset.contract)
    if errors:
        raise HistoricalFixtureError("invalid historical series: " + "; ".join(errors))
