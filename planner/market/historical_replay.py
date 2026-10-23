"""Opt-in historical market replay, isolated from production projections.

The replay compounds a weighted equity/bond portfolio through explicit annual
observations and tracks a cumulative inflation index. It is a standalone analysis
boundary: it does not alter the planner's deterministic or Monte Carlo engines.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from planner.market.historical_data_adapter import (
    HistoricalFixtureError,
    HistoricalSeriesDataset,
    validate_dataset,
)


class HistoricalReplayError(ValueError):
    """Raised when replay inputs cannot be interpreted safely."""


@dataclass(frozen=True, slots=True)
class HistoricalReplayYear:
    year: int
    equity_return: float
    bond_return: float
    inflation_rate: float
    portfolio_return: float
    nominal_value: float
    inflation_index: float
    real_value: float
    status: str


@dataclass(frozen=True, slots=True)
class HistoricalReplayResult:
    series_id: str
    currency: str
    start_year: int
    end_year: int
    initial_value: float
    equity_weight: float
    include_estimated: bool
    years: tuple[HistoricalReplayYear, ...]

    @property
    def final_nominal_value(self) -> float:
        return self.years[-1].nominal_value if self.years else self.initial_value

    @property
    def final_real_value(self) -> float:
        return self.years[-1].real_value if self.years else self.initial_value


def replay_historical_series(
    dataset: HistoricalSeriesDataset,
    *,
    initial_value: float,
    equity_weight: float,
    start_year: int | None = None,
    end_year: int | None = None,
    include_estimated: bool = False,
) -> HistoricalReplayResult:
    """Replay a weighted portfolio over a contiguous, explicitly selected window.

    Rates are decimal annual total returns. Estimated observations are rejected
    by default and included only when the caller opts in. Missing years are never
    interpolated or filled; the selected window must contain every calendar year.
    """
    if not isinstance(dataset, HistoricalSeriesDataset):
        raise HistoricalReplayError("dataset must be a HistoricalSeriesDataset")
    try:
        validate_dataset(dataset)
    except (HistoricalFixtureError, TypeError, AttributeError) as exc:
        raise HistoricalReplayError(f"invalid historical dataset: {exc}") from exc
    if dataset.contract.return_basis != "nominal":
        raise HistoricalReplayError(
            "historical replay requires nominal returns; real-return series cannot be inflation-adjusted again"
        )
    if not isinstance(include_estimated, bool):
        raise HistoricalReplayError("include_estimated must be a boolean opt-in")
    if isinstance(initial_value, bool) or not isinstance(initial_value, (int, float)) or not isfinite(initial_value) or initial_value <= 0:
        raise HistoricalReplayError("initial_value must be a finite number greater than zero")
    if isinstance(equity_weight, bool) or not isinstance(equity_weight, (int, float)) or not isfinite(equity_weight) or not 0.0 <= equity_weight <= 1.0:
        raise HistoricalReplayError("equity_weight must be a finite number between 0 and 1")

    observations = sorted(dataset.observations, key=lambda item: item.year)
    if not observations:
        raise HistoricalReplayError("historical series has no observations")
    first = observations[0].year if start_year is None else start_year
    last = observations[-1].year if end_year is None else end_year
    if isinstance(first, bool) or not isinstance(first, int) or isinstance(last, bool) or not isinstance(last, int):
        raise HistoricalReplayError("start_year and end_year must be integers")
    if first > last:
        raise HistoricalReplayError("start_year must be less than or equal to end_year")

    by_year = {item.year: item for item in observations}
    selected_years = list(range(first, last + 1))
    missing = [year for year in selected_years if year not in by_year]
    if missing:
        raise HistoricalReplayError("selected window has missing calendar years: " + ", ".join(map(str, missing)))
    selected = [by_year[year] for year in selected_years]
    estimated = [item.year for item in selected if item.status == "estimated"]
    if estimated and not include_estimated:
        raise HistoricalReplayError(
            "selected window contains estimated observations; set include_estimated=True to include them: "
            + ", ".join(map(str, estimated))
        )

    nominal = float(initial_value)
    inflation_index = 1.0
    rows: list[HistoricalReplayYear] = []
    for item in selected:
        portfolio_return = equity_weight * item.equity_return + (1.0 - equity_weight) * item.bond_return
        nominal *= 1.0 + portfolio_return
        inflation_index *= 1.0 + item.inflation_rate
        if not all(isfinite(value) for value in (portfolio_return, nominal, inflation_index)):
            raise HistoricalReplayError(
                f"replay produced a non-finite result in year {item.year}; check return magnitudes"
            )
        real_value = nominal / inflation_index
        if not isfinite(real_value):
            raise HistoricalReplayError(
                f"replay produced a non-finite inflation-adjusted value in year {item.year}"
            )
        rows.append(HistoricalReplayYear(
            year=item.year,
            equity_return=item.equity_return,
            bond_return=item.bond_return,
            inflation_rate=item.inflation_rate,
            portfolio_return=portfolio_return,
            nominal_value=nominal,
            inflation_index=inflation_index,
            real_value=real_value,
            status=item.status,
        ))

    return HistoricalReplayResult(
        series_id=dataset.contract.series_id,
        currency=dataset.contract.currency,
        start_year=first,
        end_year=last,
        initial_value=float(initial_value),
        equity_weight=float(equity_weight),
        include_estimated=include_estimated,
        years=tuple(rows),
    )
