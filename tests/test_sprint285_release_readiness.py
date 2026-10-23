"""Sprint 285 release-readiness traceability and non-destructive gate checks."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_release_readiness_document_has_explicit_required_gates():
    text = (ROOT / "planner/docs/RELEASE_READINESS.md").read_text(encoding="utf-8")
    for phrase in ("Regression suite", "Compile check", "Golden scenario", "Financial boundary", "Configuration", "Package integrity", "Traceability"):
        assert phrase in text


def test_shipped_assumptions_and_golden_baseline_have_expected_reviewed_digests():
    expected = {
        "data/assumptions.json": "425ca566acdfa55c34b565c70f26c0ba2c670129b959a9188705cb4348e46692",
        "tests/golden/baseline.json": "a9c51cb9161e0874b42f5a4b62c92c8edc845aa83d8eb49b977bcb18475f6eb6",
    }
    for relative, digest in expected.items():
        content = (ROOT / relative).read_bytes()
        assert hashlib.sha256(content).hexdigest() == digest


def test_release_manifest_matches_current_sprint_and_file_inventory():
    manifest = json.loads((ROOT / "release_manifest.json").read_text(encoding="utf-8"))
    assert manifest["sprint"] == 285
    assert manifest["file_count"] == len(manifest["files"])
    assert "tests/test_sprint285_release_readiness.py" in manifest["files"]
    assert "planner/docs/SPRINT285_RELEASE_READINESS.md" in manifest["files"]


def test_acceptance_runner_defaults_to_full_suite_and_compile_gate():
    source = (ROOT / "scripts/release_acceptance.py").read_text(encoding="utf-8")
    assert '"--skip-tests"' in source
    assert '"--skip-compile"' in source
    assert '"Pytest suite"' in source
    assert "Compile check" in source


def test_release_readiness_notes_do_not_claim_unrun_full_suite_pass():
    text = (ROOT / "planner/docs/SPRINT285_RELEASE_READINESS.md").read_text(encoding="utf-8")
    assert "pending" in text.lower()
    assert "does not show that they passed" in text.lower()
