"""Sprint 254 checks for the repeatable release-acceptance entry point."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "release_acceptance.py"

spec = importlib.util.spec_from_file_location("rc4_release_acceptance", SCRIPT)
release_acceptance = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(release_acceptance)


def test_acceptance_script_is_in_repository_root_scripts_directory():
    assert SCRIPT.is_file()
    assert release_acceptance.ROOT == ROOT


def test_default_acceptance_runs_tests_and_compile():
    args = release_acceptance.build_parser().parse_args([])
    assert not args.skip_tests
    assert not args.skip_compile


def test_test_gate_can_be_skipped_explicitly():
    args = release_acceptance.build_parser().parse_args(["--skip-tests"])
    assert args.skip_tests
    assert not args.skip_compile


def test_compile_gate_can_be_skipped_explicitly():
    args = release_acceptance.build_parser().parse_args(["--skip-compile"])
    assert args.skip_compile
    assert not args.skip_tests


def test_extra_pytest_arguments_preserve_order():
    args = release_acceptance.build_parser().parse_args(
        ["--pytest-arg", "tests/test_tax.py", "--pytest-arg=-q"]
    )
    assert args.pytest_arg == ["tests/test_tax.py", "-q"]


def test_assumptions_file_is_parseable_without_mutation():
    path = ROOT / "data" / "assumptions.json"
    before = path.read_bytes()
    json.loads(before)
    assert path.read_bytes() == before


def test_release_checklist_documents_the_acceptance_command():
    checklist = (ROOT / "planner" / "docs" / "RELEASE_READINESS.md").read_text(
        encoding="utf-8"
    )
    assert "release_acceptance.py" in checklist


def test_runner_uses_repository_root_as_subprocess_working_directory():
    source = SCRIPT.read_text(encoding="utf-8")
    assert "cwd=ROOT" in source


def test_runner_returns_nonzero_when_a_gate_fails():
    source = SCRIPT.read_text(encoding="utf-8")
    assert "return 1" in source
    assert "FAIL (exit " in source


def test_partitioning_is_balanced_and_preserves_collection_order():
    items = [f"tests/test_sample.py::test_{i}" for i in range(11)]
    partitions = [release_acceptance.partition_items(items, i, 3) for i in (1, 2, 3)]
    assert [len(part) for part in partitions] == [4, 4, 3]
    assert [item for part in partitions for item in part] != items  # round-robin grouping
    assert sorted(item for part in partitions for item in part) == sorted(items)


def test_partitioning_rejects_out_of_range_partition():
    try:
        release_acceptance.partition_items(["x"], 3, 2)
    except ValueError as exc:
        assert "between 1 and partitions" in str(exc)
    else:
        raise AssertionError("invalid partition should be rejected")


def test_partitioning_rejects_zero_partitions():
    try:
        release_acceptance.partition_items(["x"], 1, 0)
    except ValueError as exc:
        assert "at least 1" in str(exc)
    else:
        raise AssertionError("zero partitions should be rejected")
