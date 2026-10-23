# RC4 Release Readiness Checklist

This checklist is a repeatable release gate for the RetirementPlanner RC4 codebase. It is deliberately separate from the financial calculation engines: release preparation must not silently alter assumptions, calculation order, tax treatment, return precedence, or projection outputs.

## Required gates

1. **Regression suite** — run `python scripts/release_acceptance.py` from any directory for the assumptions-JSON, compile and full pytest gates together; run `python -m pytest -q` from the repository root for the regression suite alone. Record the discovered and passed test counts, failures/errors, skips, and any partitioning used. A partial run is not a full-suite pass.
2. **Compile check** — run `python -m compileall -q .` and investigate errors in maintained source and tests. Generated cache files are not release artifacts.
3. **Golden scenario** — run the golden-scenario tests and confirm the committed baseline is not regenerated as part of ordinary test execution.
4. **Financial boundary** — review changes to assumptions, tax, pension, State Pension, ISA, savings, investment returns, withdrawal, inflation and Monte Carlo code. Any intended semantic change requires explicit scope, tests and release notes. Documentation-only and test-only sprints must state that calculation behaviour is unchanged.
5. **Configuration** — confirm the shipped `data/assumptions.json` remains parseable and passes the current validation contract. Do not reset user assumptions to defaults during packaging.
6. **Entry points and reports** — run relevant CLI/health-check/report regression tests. Treat generated PDFs, charts, logs, caches and local output as runtime artifacts rather than source files unless explicitly required by the release.
7. **Package integrity** — create the checkpoint archive from the project root, inspect its top-level layout, and run `unzip -t` (or the equivalent archive integrity check). Ensure tests, documentation, configuration and source are included; exclude transient caches and machine-local virtual environments.
8. **Traceability** — update `RC4_ROADMAP.md`, `PROJECT_STATUS.md`, and this checklist's sprint/release notes where appropriate. State the exact checkpoint, test evidence, and any remaining limitations. Never label a release-ready checkpoint while a required gate is pending.

## Safe technical-debt policy

- Prefer small, auditable changes over broad cleanup during a release-readiness sprint.
- Do not remove compatibility adapters, legacy entry points, or apparently duplicated files without call-site and regression evidence.
- Do not modify the golden baseline merely to make a failing test pass; investigate the behavioural difference first.
- Keep report formatting and GUI presentation changes separate from financial calculations where practical.
- Treat `Downloads/`, generated reports, logs, charts and local caches as potentially useful diagnostic material; do not delete them automatically during a sweep.

## Sprint 253 audit scope

Sprint 253 adds this checklist and automated documentation/configuration traceability checks. It does not perform a speculative source rewrite or change calculation logic/default assumptions. Passing this checklist's documentation tests is not, by itself, proof that all release gates have run; report each gate's actual result independently.


## Sprint 254 acceptance runner

From the repository root, use `python scripts/release_acceptance.py` to run the non-destructive assumptions JSON parse check, compile check and full pytest suite from a single entry point. The runner exits non-zero if a requested gate fails and never rewrites assumptions or regenerates golden data. Optional `--skip-tests` and `--skip-compile` flags support targeted diagnostics; skipped gates are not release passes. If the environment cannot finish the suite in one process, use `--partition N --partitions M` and run every partition separately; the runner collects pytest node IDs and distributes them deterministically. A partition is not a full-suite pass until every partition has passed. Repeat `--pytest-arg=ARG` to pass extra arguments to pytest (including flags such as `-k`).


## Sprint 255 package audit

After creating a checkpoint archive from the project root, run `python scripts/package_audit.py path/to/checkpoint.zip`. The audit is read-only and checks ZIP integrity, required source/configuration/documentation/test entries, packaged assumptions JSON parseability, unsafe paths, and transient cache/bytecode exclusions. It complements rather than replaces the regression, compile, golden-scenario and financial-boundary gates above.
