# Assumption Coverage Audit (Sprint 277)

## Purpose

The audit checks that the public `data/assumptions.json` document is structurally aligned with the declared schema and the application's metadata boundaries. It reports:

- default top-level keys that are not schema-defined, and schema keys missing from defaults;
- schema paths missing operational roles or audit descriptions;
- operational roles without consumer boundaries;
- consumer module paths that do not exist in the source tree;
- presence of the GUI's complete JSON editing/serialization boundary.

## Run

From the repository root:

```bash
python scripts/audit_assumption_coverage.py
python scripts/audit_assumption_coverage.py --output reports/sprint277_assumption_coverage_audit.json
python -m pytest -q tests/test_sprint277_assumption_coverage_audit.py tests/test_sprint230_assumption_catalog_gui_coverage.py tests/test_sprint241_assumption_end_to_end_consumer_trace.py
```

The command returns exit code 0 for `PASS`, and 1 when static consistency gaps are found. `--root` supports auditing a separate extracted project tree.

## Interpretation and limitations

A `PASS` means only that these static contract/catalogue checks are consistent. It does **not** prove every listed module reads every assumption at runtime, nor does it establish financial correctness or tax-law correctness. Runtime consumer-trace tests and GUI round-trip tests complement the report. Any new assumption should be added deliberately to the schema/defaults, role and consumer catalogs, audit descriptions, GUI behavior where applicable, and focused regression tests.

The audit does not change assumption defaults or production calculation logic.
