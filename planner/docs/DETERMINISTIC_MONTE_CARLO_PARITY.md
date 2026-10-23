# Sprint 283 — Deterministic and Monte Carlo Parity

This sprint strengthens regression coverage at the boundary between the deterministic projection and seeded Monte Carlo simulation. It does not change either engine's financial calculations.

## Covered contracts

- With investment and inflation volatility set to zero, a one-iteration Monte Carlo run matches the deterministic projection's ending assets to the penny.
- Repeating a seeded simulation reproduces the ordered ending-asset sample and success rate.
- Percentile outputs remain ordered from minimum through maximum, and financial summaries remain finite.
- Different seeds produce different samples when investment volatility is non-zero.
- Monte Carlo runs do not mutate the caller's original assumptions.

## Interpretation and limitations

Parity is asserted only for the zero-volatility scenario where the deterministic and Monte Carlo return assumptions are deliberately aligned. With non-zero volatility, Monte Carlo represents a distribution of possible outcomes and is not expected to equal the deterministic projection. Seed reproducibility is a software regression contract, not a claim that future market returns are predictable.

## Validation

Focused Sprint 250 / 281 / 282 / 283 regression set: 31 passed in the authoring environment. The full suite remains pending the user's local `python -m pytest -ra` acceptance run. Collection and release-evidence reports do not represent test execution results.
