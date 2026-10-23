"""Sprint 264 guards against stale test-count evidence being treated as current."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "test_collection_report.py"
spec = importlib.util.spec_from_file_location("rc4_collection_report_sprint264", SCRIPT)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def comparison(**overrides: object) -> dict:
    result = {
        "only_current_count": 0,
        "only_other_count": 0,
        "files_only_current": [],
        "files_only_other": [],
        "files_with_different_hashes": [],
        "config_hashes_differ": False,
    }
    result.update(overrides)
    return result


def test_identical_collection_evidence_is_clean() -> None:
    assert module.comparison_is_clean(comparison())


def test_node_id_difference_makes_evidence_stale() -> None:
    assert not module.comparison_is_clean(comparison(only_current_count=11))


def test_missing_test_file_makes_evidence_stale() -> None:
    assert not module.comparison_is_clean(comparison(files_only_current=["tests/test_new.py"]))


def test_removed_test_file_makes_evidence_stale() -> None:
    assert not module.comparison_is_clean(comparison(files_only_other=["tests/test_old.py"]))


def test_changed_test_source_hash_makes_evidence_stale() -> None:
    assert not module.comparison_is_clean(comparison(files_with_different_hashes=["tests/test_a.py"]))


def test_changed_pytest_configuration_makes_evidence_stale() -> None:
    assert not module.comparison_is_clean(comparison(config_hashes_differ=True))


def test_sprint264_is_opted_into_release_package_audit() -> None:
    audit = (ROOT / "scripts" / "package_audit.py").read_text(encoding="utf-8")
    assert "tests/test_sprint264_collection_evidence_freshness.py" in audit
    assert "FORBIDDEN_LOCAL_EVIDENCE" in audit
