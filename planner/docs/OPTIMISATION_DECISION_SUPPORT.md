# Optimisation Decision Support

`OptimisationDecisionSupport` is a reporting/decision-support layer over the read-only results produced by `OptimisationEngine.compare_policies()`.

It does not modify the retirement timeline or tax calculations.

## Output

The assessment identifies:

- the policy with the higher average tax-efficient pension capacity;
- the policy with the lower capacity;
- the average difference across common ages;
- the largest difference and the age at which it occurs;
- whether the difference is material against a configurable threshold;
- human-readable recommendation and explanation text.

The default materiality threshold is £1,000 per year.

## Boundary

The decision-support layer interprets existing optimisation results. It must not duplicate or alter the financial rules implemented by `OptimisationEngine`.
