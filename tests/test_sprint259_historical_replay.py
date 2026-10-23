from dataclasses import replace

import pytest

from planner.market.historical_data_adapter import HistoricalSeriesDataset, load_historical_fixture
from planner.market.historical_replay import HistoricalReplayError, replay_historical_series

FIXTURE = __import__("pathlib").Path(__file__).resolve().parent / "fixtures" / "historical_returns_v1.json"


def dataset():
    base = load_historical_fixture(FIXTURE)
    # Use explicit, small synthetic observations; no live or real-market data.
    observations = tuple(
        replace(item, equity_return=0.10, bond_return=0.04, inflation_rate=0.02,
                status="actual", year=2020 + i)
        for i, item in enumerate(base.observations)
    )
    return HistoricalSeriesDataset(base.contract, observations, base.format_version)


def test_replay_uses_chronological_years_and_returns_ordered_rows():
    result = replay_historical_series(dataset(), initial_value=1000, equity_weight=0.5)
    assert [row.year for row in result.years] == [2020, 2021, 2022]
    assert result.start_year == 2020 and result.end_year == 2022


def test_replay_compounds_weighted_nominal_returns():
    result = replay_historical_series(dataset(), initial_value=1000, equity_weight=0.5)
    assert result.years[0].portfolio_return == pytest.approx(0.07)
    assert result.final_nominal_value == pytest.approx(1000 * 1.07**3)


def test_replay_applies_cumulative_inflation_to_real_value():
    result = replay_historical_series(dataset(), initial_value=1000, equity_weight=0.5)
    assert result.years[-1].inflation_index == pytest.approx(1.02**3)
    assert result.final_real_value == pytest.approx(result.final_nominal_value / 1.02**3)


def test_replay_is_repeatable_for_identical_inputs():
    args = dict(initial_value=1234.56, equity_weight=0.6, start_year=2020, end_year=2022)
    assert replay_historical_series(dataset(), **args) == replay_historical_series(dataset(), **args)


def test_replay_rejects_estimates_by_default():
    base = load_historical_fixture(FIXTURE)
    with pytest.raises(HistoricalReplayError, match="estimated observations"):
        replay_historical_series(base, initial_value=1000, equity_weight=0.5)


def test_replay_can_include_estimates_only_when_explicitly_enabled():
    base = load_historical_fixture(FIXTURE)
    result = replay_historical_series(base, initial_value=1000, equity_weight=0.5, include_estimated=True)
    assert any(row.status == "estimated" for row in result.years)
    assert result.include_estimated is True


def test_replay_rejects_missing_years_in_selected_window():
    base = dataset()
    gapped = HistoricalSeriesDataset(replace(base.contract, missing_year_policy="allow_gaps"), (base.observations[0], base.observations[2]), base.format_version)
    with pytest.raises(HistoricalReplayError, match="missing calendar years: 2021"):
        replay_historical_series(gapped, initial_value=1000, equity_weight=0.5)


def test_replay_rejects_invalid_initial_value():
    with pytest.raises(HistoricalReplayError, match="initial_value"):
        replay_historical_series(dataset(), initial_value=0, equity_weight=0.5)


def test_replay_rejects_out_of_range_allocation():
    with pytest.raises(HistoricalReplayError, match="equity_weight"):
        replay_historical_series(dataset(), initial_value=1000, equity_weight=1.1)


def test_replay_supports_equity_only_and_bond_only_allocations():
    equity = replay_historical_series(dataset(), initial_value=1000, equity_weight=1.0)
    bonds = replay_historical_series(dataset(), initial_value=1000, equity_weight=0.0)
    assert equity.years[0].portfolio_return == pytest.approx(0.10)
    assert bonds.years[0].portfolio_return == pytest.approx(0.04)


def test_replay_rejects_reversed_year_window():
    with pytest.raises(HistoricalReplayError, match="start_year"):
        replay_historical_series(dataset(), initial_value=1000, equity_weight=0.5, start_year=2022, end_year=2020)


def test_replay_rejects_empty_dataset():
    base = dataset()
    empty = HistoricalSeriesDataset(base.contract, (), base.format_version)
    with pytest.raises(HistoricalReplayError, match="no observations"):
        replay_historical_series(empty, initial_value=1000, equity_weight=0.5)
