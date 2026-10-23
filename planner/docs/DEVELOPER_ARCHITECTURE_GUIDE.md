# Developer Architecture Guide

## Purpose

This guide is the practical companion to `ARCHITECTURE.md`. It describes how a change should move through Retirement Planner without leaking business rules between layers.

## Change flow

```text
Assumptions / imported data
          |
          v
   Planner orchestration
          |
          v
  Calculation engine(s)
          |
          v
 Structured / typed result
          |
          +-------------------+
          |                   |
          v                   v
 Analysis engines        Report adapters
          |                   |
          +---------+---------+
                    v
             Presentation
```

## Where code belongs

| Change | Preferred location |
|---|---|
| A new financial rule | The owning calculation engine |
| A new scenario combination | Scenario/orchestration layer |
| Risk or trade-off interpretation | Analysis engine |
| Output formatting | Report adapter/report layer |
| GUI enablement or interaction state | `planner/gui/` |
| Configuration value | `Assumptions` / configuration documentation |
| External data ingestion | Import/source adapter layer |

Do not implement a rule in a report, GUI callback, or command-line script merely because that is where the value is first displayed.

## Stable contracts

The project uses explicit result objects and structural contracts at important boundaries. Consumers should depend on the smallest stable contract they need, rather than reaching into engine internals.

For new integrations:

1. Define or reuse a typed boundary.
2. Keep calculation ownership in one engine.
3. Add focused regression coverage for the contract.
4. Add an end-to-end test only where multiple boundaries interact.

## GUI boundary

The GUI is a presentation and interaction layer. Workflow actions are resolved through the canonical workflow-state/action contract before handlers execute. Button and keyboard entry points must therefore remain thin adapters to the shared dispatch boundary.

GUI changes must not duplicate retirement, tax, pension, ISA, savings, withdrawal, or investment calculations.

## Testing discipline

Run focused tests first, then the full suite:

```powershell
$env:PYTHONPATH='.'
python -m pytest -q --disable-warnings tests/test_gui_workflow_state.py tests/test_scenario_projection_gui.py
python -m pytest -q --disable-warnings
python -m compileall -q planner tests
```

A sprint is not complete until the full regression suite passes and the checkpoint package has been verified with `unzip -t`.

## Checkpoint discipline

Before a higher-risk refactor, create a named ZIP checkpoint containing the complete working tree. Record the sprint number, test count, and any deliberately unchanged calculation areas in `PROJECT_STATUS.md` and `RC4_ROADMAP.md`.

## Financial-calculation invariant

Unless a sprint explicitly states otherwise, retirement, tax, State Pension, ISA, savings and withdrawal calculations are regression-locked. Refactoring and documentation work must leave those results unchanged.
