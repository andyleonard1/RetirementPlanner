# RC4 Checkpoint Reconciliation — 2026-10-11

## Authoritative checkpoint

The uploaded project worktree contained Sprint 256 at initial reconciliation; Sprint 257 adapter/fixture work is now layered on top of that verified checkpoint. The user-confirmed count of 1,294 tests corresponds to Sprint 253. Sprint 254 added 12 tests, Sprint 255 added 8, and Sprint 256 added 13, so the current collection is 1,327.

## Verified evidence

- Pytest collection: 1,327 tests.
- Partition 1: 332 passed, 11 subtests passed.
- Partition 2: 332 passed, 6 subtests passed.
- Partition 3: 332 passed.
- Partition 4: 331 passed, 3 subtests passed.
- Total: 1,327 tests passed and 20 subtests passed.
- `python -m compileall -q .`: passed.
- Focused Sprint 252–256 tests: 47 passed, 8 subtests passed.
- Assumptions JSON parse gate: passed.

Commands used from the repository root:

```bash
PYTHONPATH=. python scripts/release_acceptance.py --partition 1 --partitions 4 --skip-compile
PYTHONPATH=. python scripts/release_acceptance.py --partition 2 --partitions 4 --skip-compile
PYTHONPATH=. python scripts/release_acceptance.py --partition 3 --partitions 4 --skip-compile
PYTHONPATH=. python scripts/release_acceptance.py --partition 4 --partitions 4 --skip-compile
python -m compileall -q .
PYTHONPATH=. python -m pytest -q tests/test_sprint252_golden_scenario_pack.py tests/test_sprint253_release_readiness.py tests/test_sprint254_release_acceptance.py tests/test_sprint255_package_audit.py tests/test_sprint256_historical_data_contract.py
```

## Discrepancies and handling

1. The 1,294 count is the earlier Sprint 253 checkpoint, not the current Sprint 256 test collection.
2. The worktree has Sprint 256 content but Git HEAD is labelled Sprint 140. Since many files are uncommitted, Git history cannot be treated as the complete sprint chronology. The worktree is preserved; no history rewrite or destructive reset was performed.
3. The uploaded ZIP included `.git`, `.pytest_cache`, `__pycache__`, `.pyc` files and a top-level wrapper directory. It fails the project's own package-audit criteria. The clean checkpoint archive excludes those artifacts and is checked with `scripts/package_audit.py`.

## Preservation boundary

This reconciliation updates checkpoint documentation and packaging only. It does not edit `data/assumptions.json`, `tests/golden/baseline.json`, or financial calculation source files. Historical-data contract work remains validation-only and is not connected to projection calculations.

## Sprint 257 addition

Sprint 257 adds a provider-neutral protocol and version-1 fixture loader only. Its 14 focused tests passed. The complete Sprint 257 suite collected 1,341 tests and all passed across four partitions (336 + 335 + 335 + 335), with 20 subtests passed. Compilation and the combined Sprint 252–257 focused group passed.
