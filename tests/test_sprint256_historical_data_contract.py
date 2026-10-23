from dataclasses import replace

from planner.market.historical_data_contract import (
    HistoricalReturnObservation,
    HistoricalSeriesContract,
    validate_observation,
    validate_series,
)


def observation(year=2020, **changes):
    base = HistoricalReturnObservation(
        year=year,
        equity_return=0.07,
        bond_return=0.02,
        inflation_rate=0.03,
        source_id="official-series-1",
        source_name="Example Statistical Source",
    )
    return replace(base, **changes)


def contract(**changes):
    base = HistoricalSeriesContract(
        series_id="uk-balanced-market-v1",
        description="Annual UK equity, bond and inflation observations",
    )
    return replace(base, **changes)


def test_valid_observation_preserves_explicit_provenance_and_status():
    item = observation(status="estimated", source_url="https://example.test/data")
    assert validate_observation(item) == []
    assert item.status == "estimated"
    assert item.source_url == "https://example.test/data"


def test_rates_are_decimal_values_without_percent_coercion():
    item = observation(equity_return=5.2)
    assert validate_observation(item) == []
    assert item.equity_return == 5.2


def test_non_finite_and_boolean_rates_are_rejected():
    errors = validate_observation(observation(equity_return=float("nan"), bond_return=True))
    assert any("equity_return" in error for error in errors)
    assert any("bond_return" in error for error in errors)


def test_rates_at_or_below_minus_one_are_rejected():
    errors = validate_observation(observation(inflation_rate=-1.0))
    assert any("inflation_rate" in error for error in errors)


def test_empty_source_metadata_is_rejected():
    errors = validate_observation(observation(source_id=" ", source_name=""))
    assert any("source_id" in error for error in errors)
    assert any("source_name" in error for error in errors)


def test_invalid_status_and_return_basis_are_rejected():
    errors = validate_observation(observation(status="forecast", return_basis="unknown"))
    assert any("status" in error for error in errors)
    assert any("return_basis" in error for error in errors)


def test_series_accepts_contiguous_years_with_matching_metadata():
    items = [observation(2020), observation(2021)]
    assert validate_series(items, contract()) == []


def test_duplicate_calendar_year_is_rejected():
    errors = validate_series([observation(2020), observation(2020)], contract())
    assert "duplicate calendar year: 2020" in errors


def test_missing_year_is_rejected_by_default_policy():
    errors = validate_series([observation(2020), observation(2022)], contract())
    assert "missing calendar years: 2021" in errors


def test_allow_gaps_policy_does_not_invent_intermediate_observations():
    items = [observation(2020), observation(2022)]
    assert validate_series(items, contract(missing_year_policy="allow_gaps")) == []
    assert [item.year for item in items] == [2020, 2022]


def test_series_currency_and_basis_must_match_observations():
    item = observation(currency="USD", return_basis="real")
    errors = validate_series([item], contract())
    assert any("currency differs" in error for error in errors)
    assert any("return_basis differs" in error for error in errors)


def test_boolean_year_and_out_of_range_year_are_rejected():
    assert any("year" in error for error in validate_observation(observation(year=True)))
    assert any("year" in error for error in validate_observation(observation(year=2300)))


def test_design_documents_integration_boundary_and_preserves_calculation_scope():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    design = (root / "planner/docs/HISTORICAL_DATA_INTEGRATION.md").read_text(encoding="utf-8")
    roadmap = (root / "RC4_ROADMAP.md").read_text(encoding="utf-8")
    assert "does **not** connect a provider" in design
    assert "No production financial calculation logic" in roadmap
