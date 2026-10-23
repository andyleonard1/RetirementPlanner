# Sprint 282 — Tax and Withdrawal Scenario Integration

## Scope

Sprint 282 adds full-planner regression coverage around the existing strategy, withdrawal, tax, and pension accounting pipeline. The suite covers pension-first versus ISA-first behavior, gross/net income reconciliation, the annual pension-income constraint, the lifetime tax-free cash ceiling, exhausted-asset shortfalls, summary totals, and finite numeric outputs.

## Interpretation

These checks protect current implementation contracts and scenario consistency. They do not establish that a withdrawal strategy is universally optimal, replace individual tax advice, or model every UK tax rule and allowance. Results depend on the configured assumptions and the engine's current tax simplifications.

## Change boundary

No production financial calculation code, default assumptions, or golden baseline values were changed for this sprint.
