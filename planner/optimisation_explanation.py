"""
Optimisation outcome explanation.

Provides human-readable explanations of policy comparisons without performing
or changing any retirement calculations.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OptimisationExplanation:
    policy: str
    compared_with: str
    age: int | None
    policy_limit: float | None
    comparison_limit: float | None
    difference: float | None
    headline: str
    detail: str


class OptimisationExplanationEngine:
    """Explain the outcome of a read-only optimisation policy comparison."""

    @staticmethod
    def _rows(comparison, policy):
        return {age: value for age, value in comparison.get(policy, ())}

    def explain(self, comparison, policy, compared_with):
        if policy not in comparison:
            raise ValueError(f"Unknown optimisation policy in comparison: {policy!r}")
        if compared_with not in comparison:
            raise ValueError(
                f"Unknown optimisation policy in comparison: {compared_with!r}"
            )
        if policy == compared_with:
            raise ValueError("Optimisation policies must be different")

        left = self._rows(comparison, policy)
        right = self._rows(comparison, compared_with)
        ages = sorted(set(left) & set(right))

        if not ages:
            return OptimisationExplanation(
                policy=policy,
                compared_with=compared_with,
                age=None,
                policy_limit=None,
                comparison_limit=None,
                difference=None,
                headline="No common ages were available for comparison.",
                detail="The optimisation policies could not be compared over a shared timeline.",
            )

        differences = [(age, left[age] - right[age]) for age in ages]
        age, difference = max(differences, key=lambda item: abs(item[1]))
        policy_limit = left[age]
        comparison_limit = right[age]

        if difference > 0:
            direction = "higher"
            detail = (
                f"At age {age}, {policy} permits £{difference:,.0f} more "
                f"tax-efficient pension income than {compared_with}."
            )
        elif difference < 0:
            direction = "lower"
            detail = (
                f"At age {age}, {policy} permits £{abs(difference):,.0f} less "
                f"tax-efficient pension income than {compared_with}."
            )
        else:
            direction = "the same"
            detail = (
                f"At age {age}, both policies permit the same tax-efficient "
                "pension income."
            )

        if difference == 0:
            headline = (
                f"{policy.replace('_', ' ').title()} and "
                f"{compared_with.replace('_', ' ')} produce the same limit."
            )
        else:
            headline = (
                f"{policy.replace('_', ' ').title()} produces {direction} limits "
                f"than {compared_with.replace('_', ' ' )}."
            )

        return OptimisationExplanation(
            policy=policy,
            compared_with=compared_with,
            age=age,
            policy_limit=policy_limit,
            comparison_limit=comparison_limit,
            difference=difference,
            headline=headline,
            detail=detail,
        )

    def explain_all(self, comparison):
        policies = list(comparison)
        return [
            self.explain(comparison, policy, other)
            for index, policy in enumerate(policies)
            for other in policies[index + 1 :]
        ]
