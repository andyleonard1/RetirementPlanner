# Assumptions and Configuration

`Assumptions` is the configuration boundary for the retirement model. Engines should obtain planning inputs through this boundary rather than embedding user-specific constants in calculation code.

The project currently supports assumptions covering areas such as:

- retirement age
- pension starting value
- withdrawal target/strategy
- investment growth assumptions
- ISA and savings assumptions
- inflation
- State Pension timing
- tax configuration
- planning horizon

The authoritative runtime values are held in `planner/assumptions.py` and the project's assumption data/configuration files. This document intentionally describes the boundary rather than duplicating every numeric value, so that documentation does not become a second source of truth.

## Rules

1. Add new model inputs to `Assumptions` first.
2. Give assumptions explicit names.
3. Avoid hard-coded financial policy values in report code.
4. Keep assumption access compatible with `AssumptionsProvider`.
5. When an assumption changes the financial result, add or update regression coverage.

## Configuration schema

`planner/assumptions_schema.py` is the structural contract for the JSON configuration.
It validates required keys, primitive types, finite numeric values and the structure of
`goals`. Unknown keys are retained and logged as warnings so that newer configuration
files remain usable by older code where possible.

Structural validation deliberately does not replace `ValidationEngine`. The schema answers
whether the configuration has the expected shape; `ValidationEngine` answers whether the
values satisfy the planner's business and range rules.

## Safe editing and saving

`Assumptions.validate()` validates the current in-memory configuration without writing it.
`Assumptions.save()` always validates first and therefore refuses to persist an invalid
configuration. Saving is atomic: the new JSON is written to a temporary file and then
replaced into place, reducing the risk of leaving a partially written assumptions file.

Recommended editing workflow:

1. Load `Assumptions`.
2. Make changes with `set()` or item assignment.
3. Call `validate()` if feedback is required before saving.
4. Call `save()` to validate again and persist the complete configuration.
5. Treat a validation exception as a failed edit; the existing file remains untouched.

The configuration JSON remains the source of truth. This documentation describes the
boundary and safety guarantees rather than duplicating all runtime values.

## Configuration change tracking

`Assumptions` also provides lightweight auditability for in-memory edits through
`changes()` and `has_changes()`.

The baseline is the configuration as last loaded or successfully saved. Each
reported `AssumptionChange` contains:

- `path` — the configuration key or nested path that changed;
- `before` — the baseline value;
- `after` — the current value.

Nested changes are detected as well, including edits to entries inside `goals`.
This means audit information does not depend on every caller using `set()`; the
complete configuration is compared with its baseline when `changes()` is called.

A successful `save()` establishes the newly persisted configuration as the new
baseline. `reset_change_tracking()` can be used when an application deliberately
wants to accept the current in-memory state without writing it.

This is intentionally a lightweight audit trail rather than a historical event
log. It answers the question **"what has changed since this configuration was
loaded or last saved?"** without adding timestamps, user identity or persistence
of audit history to the financial model.

## Projection audit context

Projection results also carry an `audit_context` describing why a projection was run:

- `user` — ordinary direct projection using user-edited assumptions.
- `scenario` — a ScenarioManager scenario comparison.
- `recommendation` — a retirement-age solver/recommendation projection.
- `analysis` — analytical projections such as sensitivity or Monte Carlo work.

The context does not alter calculations. It only helps reporting distinguish intentional scenario/analysis changes from actual user assumption changes.
