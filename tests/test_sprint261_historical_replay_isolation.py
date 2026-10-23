"""Sprint 261 guards against historical replay leaking into production planning."""
from __future__ import annotations

import ast
import hashlib
from dataclasses import replace
from pathlib import Path

import pytest

from planner.market.historical_data_adapter import HistoricalSeriesDataset, load_historical_fixture
from planner.market.historical_replay import HistoricalReplayError, replay_historical_series

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "historical_returns_v1.json"
PROTECTED_FILES = (ROOT / "data" / "assumptions.json", ROOT / "tests" / "golden" / "baseline.json")
REPLAY_MODULE = "planner.market.historical_replay"
FORBIDDEN_PRODUCTION_IMPORTS = {
    REPLAY_MODULE,
    "planner.planner",
    "planner.monte_carlo_engine",
}


def _dataset() -> HistoricalSeriesDataset:
    source = load_historical_fixture(FIXTURE)
    observations = tuple(
        replace(
            observation,
            year=2020 + index,
            equity_return=0.08 + index * 0.01,
            bond_return=0.03,
            inflation_rate=0.02,
            status="actual",
        )
        for index, observation in enumerate(source.observations)
    )
    return HistoricalSeriesDataset(source.contract, observations, source.format_version)


def _imports(tree: ast.AST) -> set[str]:
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "import_module" and node.args and isinstance(node.args[0], ast.Constant):
                if isinstance(node.args[0].value, str):
                    found.add(node.args[0].value)
    return found


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_production_source_does_not_import_historical_replay() -> None:
    """Replay must remain a leaf utility, not a projection/Monte Carlo dependency."""
    violations: list[str] = []
    replay_path = ROOT / "planner" / "market" / "historical_replay.py"
    for path in (ROOT / "planner").rglob("*.py"):
        if path == replay_path or any(part in {"__pycache__", ".venv"} for part in path.parts):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, UnicodeDecodeError) as exc:
            pytest.fail(f"could not inspect production source {path.relative_to(ROOT)}: {exc}")
        if REPLAY_MODULE in _imports(tree):
            violations.append(str(path.relative_to(ROOT)))
    assert violations == [], f"production source imports historical replay: {violations}"


def test_replay_module_has_no_projection_monte_carlo_or_gui_imports() -> None:
    path = ROOT / "planner" / "market" / "historical_replay.py"
    imports = _imports(ast.parse(path.read_text(encoding="utf-8")))
    forbidden = sorted(import_name for import_name in imports if any(
        import_name == name or import_name.startswith(name + ".")
        for name in FORBIDDEN_PRODUCTION_IMPORTS
    ))
    assert forbidden == []


def test_replay_success_does_not_mutate_assumptions_or_golden_baseline() -> None:
    before = {path: _digest(path) for path in PROTECTED_FILES}
    replay_historical_series(_dataset(), initial_value=25_000, equity_weight=0.6)
    after = {path: _digest(path) for path in PROTECTED_FILES}
    assert after == before


def test_replay_failure_does_not_mutate_dataset_or_protected_files() -> None:
    dataset = _dataset()
    observations_before = dataset.observations
    protected_before = {path: _digest(path) for path in PROTECTED_FILES}
    with pytest.raises(HistoricalReplayError, match="missing calendar years"):
        replay_historical_series(
            dataset,
            initial_value=25_000,
            equity_weight=0.6,
            start_year=2019,
            end_year=2020,
        )
    assert dataset.observations == observations_before
    assert {path: _digest(path) for path in PROTECTED_FILES} == protected_before


def test_replay_is_repeatable_and_has_no_cross_call_state() -> None:
    dataset = _dataset()
    last_year = dataset.observations[-1].year
    first = replay_historical_series(
        dataset, initial_value=10_000, equity_weight=0.65,
        start_year=2020, end_year=2021,
    )
    replay_historical_series(
        dataset, initial_value=80_000, equity_weight=0.1,
        start_year=last_year - 1, end_year=last_year,
    )
    repeated = replay_historical_series(
        dataset, initial_value=10_000, equity_weight=0.65,
        start_year=2020, end_year=2021,
    )
    assert repeated == first


def test_replay_uses_only_supplied_dataset_and_parameters() -> None:
    dataset = _dataset()
    result_a = replay_historical_series(dataset, initial_value=10_000, equity_weight=0.5)
    result_b = replay_historical_series(dataset, initial_value=20_000, equity_weight=0.5)
    assert result_b.final_nominal_value == pytest.approx(result_a.final_nominal_value * 2)
    assert result_b.final_real_value == pytest.approx(result_a.final_real_value * 2)


def test_replay_rejects_bad_window_without_partial_result() -> None:
    dataset = _dataset()
    with pytest.raises(HistoricalReplayError, match="start_year must be less than or equal"):
        replay_historical_series(
            dataset, initial_value=10_000, equity_weight=0.5,
            start_year=2022, end_year=2021,
        )
