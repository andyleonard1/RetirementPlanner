# Sprint 56 — Recommendation Robustness

Sprint 56 hardens the overall recommendation layer without changing any retirement, tax, pension, savings, ISA or optimisation calculations.

## Behaviour

The recommendation layer now:

- refuses to manufacture a retirement-age recommendation when the retirement decision or recommended age is unavailable;
- handles a missing optimisation decision without failing;
- handles an unavailable score without formatting errors;
- treats an optimisation policy advantage peaking at a different age as a qualification, not a conflict with the selected retirement age;
- describes equivalent optimisation policies conservatively;
- tolerates incomplete optimisation decision objects;
- remains read-only and does not mutate either input decision.

## Principle

The retirement-age decision remains authoritative for the selected retirement age. Optimisation decision support explains the policy trade-off and does not override the retirement-age selection.

## Verification

Full test suite: **223 tests passing**.
