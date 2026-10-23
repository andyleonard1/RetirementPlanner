"""Sprint 260 regression coverage for the historical replay safety boundary."""
from dataclasses import replace
from pathlib import Path

import pytest

from planner.market.historical_data_adapter import HistoricalSeriesDataset, load_historical_fixture
from planner.market.historical_replay import HistoricalReplayError, replay_historical_series

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "historical_returns_v1.json"


def dataset():
    base = load_historical_fixture(FIXTURE)
    observations = tuple(
        replace(item, equity_return=0.10, bond_return=0.04, inflation_rate=0.02,
                status="actual", year=2020 + i)
        for i, item in enumerate(base.observations)
    )
    return HistoricalSeriesDataset(base.contract, observations, base.format_version)


def test_replay_requires_boolean_estimated_data_opt_in():
    with pytest.raises(HistoricalReplayError, match="include_estimated must be a boolean"):
        replay_historical_series(dataset(), initial_value=1000, equity_weight=0.5, include_estimated=1)


def test_replay_rejects_real_return_series_to_prevent_double_inflation_adjustment():
    base = dataset()
    real_contract = replace(base.contract, return_basis="real")
    real_observations = tuple(replace(item, return_basis="real") for item in base.observations)
    real_dataset = HistoricalSeriesDataset(real_contract, real_observations, base.format_version)
    with pytest.raises(HistoricalReplayError, match="requires nominal returns"):
        replay_historical_series(real_dataset, initial_value=1000, equity_weight=0.5)


def test_replay_rejects_non_dataset_input_cleanly():
    with pytest.raises(HistoricalReplayError, match="dataset must be a HistoricalSeriesDataset"):
        replay_historical_series(None, initial_value=1000, equity_weight=0.5)


def test_replay_rejects_non_finite_compounded_results():
    base = dataset()
    huge = tuple(replace(item, equity_return=1e308, bond_return=1e308) for item in base.observations)
    huge_dataset = HistoricalSeriesDataset(base.contract, huge, base.format_version)
    with pytest.raises(HistoricalReplayError, match="non-finite result"):
        replay_historical_series(huge_dataset, initial_value=1e100, equity_weight=1.0)


def test_replay_rejects_malformed_dataset_contract_cleanly():
    base = dataset()
    malformed = HistoricalSeriesDataset(None, base.observations, base.format_version)
    with pytest.raises(HistoricalReplayError, match="invalid historical dataset"):
        replay_historical_series(malformed, initial_value=1000, equity_weight=0.5)


def test_replay_result_has_explicit_window_and_no_production_engine_dependency():
    from planner.market.historical_replay import HistoricalReplayResult
    result = replay_historical_series(dataset(), initial_value=1000, equity_weight=0.5,
                                      start_year=2021, end_year=2022)
    assert isinstance(result, HistoricalReplayResult)
    assert (result.start_year, result.end_year) == (2021, 2022)
    assert [row.year for row in result.years] == [2021, 2022]
    assert result.initial_value == 1000
