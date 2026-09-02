# Retirement Planner Architecture

## 1. Purpose

Retirement Planner is an engine-driven financial-planning system. Its architecture separates orchestration, calculation, analysis and presentation so that financial rules can be tested independently from reports and application entry points.

## 2. Layer model

```text
+-------------------------------+
| Application entry points      |
| main.py / recommend.py / ...  |
+---------------+---------------+
                |
                v
+-------------------------------+
| Planner / Scenario orchestration|
| RetirementPlanner              |
| ScenarioManager                |
+---------------+---------------+
                |
                v
+-------------------------------+
| Calculation engines            |
| Pension / Tax / ISA / Savings  |
| Withdrawal / Cashflow / State  |
| Pension / Inflation / Strategy |
+---------------+---------------+
                |
                v
+-------------------------------+
| Analysis engines               |
| Summary / Decision / Risk      |
| Recommendation / Goal          |
| Optimisation / Sensitivity     |
+---------------+---------------+
                |
                v
+-------------------------------+
| Report / presentation layer    |
| Console / PDF / Excel / charts |
+-------------------------------+
```

## 3. Responsibilities

### Application entry points

Application scripts coordinate a use case. They should not contain duplicated financial rules.

### `RetirementPlanner`

The planner owns the calculation sequence and returns the canonical planner result. It coordinates engines; it does not replace them.

### `ScenarioManager`

The scenario layer creates and compares alternative assumption sets, including retirement-age scenarios. It is the preferred route for recommendation-oriented scenario analysis.

### Calculation engines

Calculation engines transform the retirement timeline or calculate a defined financial quantity. Examples include:

- `PensionEngine`
- `StatePensionEngine`
- `TaxEngine`
- `ISAEngine`
- `SavingsEngine`
- `WithdrawalEngine`
- `CashflowEngine`
- `InflationEngine`
- `StrategyEngine`
- `OptimisationEngine`

### Analysis engines

Analysis engines interpret completed calculations. Examples include summary, decision, risk, goal, recommendation, Monte Carlo and sensitivity components.

### Reports

Reports consume prepared data and present it. They must not recalculate retirement outcomes.

## 4. Contracts

`planner/contracts.py` defines structural interfaces using `typing.Protocol`.

The current contracts cover:

- `AssumptionsProvider`
- `TimelineBuilderProtocol`
- `TimelineTransformerProtocol`
- `SummaryEngineProtocol`
- `ValidatorProtocol`

The contracts are structural rather than inheritance-based. Existing engines can satisfy a contract without being rewritten to inherit from a common base class.

## 5. Result objects

The project uses explicit result objects for major analysis boundaries. Compatibility with legacy mapping-style access is retained where required during migration.

The preferred direction is:

```text
engine -> typed result -> consumer/report
```

rather than exposing internal engine state directly.

## 6. Dependency rules

1. Reports do not call calculation engines to obtain missing values.
2. Engines do not import report classes.
3. Financial business rules are not duplicated between entry points.
4. `Assumptions` is the source of configuration values.
5. Public engine interfaces should remain stable during incremental refactoring.
6. New public methods should be typed.
7. Logging is preferred to diagnostic `print()` calls inside engines.
8. Compatibility shims are acceptable when they reduce migration risk.

## 7. Refactoring policy

The project favours incremental consolidation over wholesale rewrites. A refactor is considered successful when behaviour remains stable, the full test suite passes, and the resulting boundary is easier to understand and maintain.
