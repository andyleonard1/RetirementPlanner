"""Human-readable decision support for optimisation policy comparisons."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OptimisationDecision:
    higher_policy: str | None
    lower_policy: str | None
    average_difference: float
    maximum_difference: float
    maximum_difference_age: int | None
    material: bool
    recommendation: str
    explanation: str


class OptimisationDecisionSupport:
    """Interpret read-only optimisation results without changing calculations."""

    def __init__(self, materiality_threshold: float = 1_000.0):
        if materiality_threshold < 0:
            raise ValueError("materiality_threshold must not be negative")
        self.materiality_threshold = float(materiality_threshold)

    def assess(self, comparisons: dict[str, list[tuple[int, float]]]) -> OptimisationDecision:
        if not comparisons:
            raise ValueError("At least one optimisation policy is required")

        policies = tuple(comparisons)
        if len(policies) < 2:
            return OptimisationDecision(
                higher_policy=None,
                lower_policy=None,
                average_difference=0.0,
                maximum_difference=0.0,
                maximum_difference_age=None,
                material=False,
                recommendation="No policy comparison is available.",
                explanation="At least two optimisation policies are needed to assess a practical difference.",
            )

        first = dict(comparisons[policies[0]])
        second = dict(comparisons[policies[1]])
        ages = sorted(set(first) & set(second))
        if not ages:
            raise ValueError("Optimisation policies have no common ages")

        signed = [second[age] - first[age] for age in ages]
        absolute = [(age, abs(value)) for age, value in zip(ages, signed)]
        average_difference = sum(abs(value) for value in signed) / len(signed)
        maximum_difference_age, maximum_difference = max(
            absolute, key=lambda item: (item[1], -item[0])
        )

        signed_average = sum(signed) / len(signed)
        if signed_average > 0:
            higher_policy, lower_policy = policies[1], policies[0]
        elif signed_average < 0:
            higher_policy, lower_policy = policies[0], policies[1]
        else:
            higher_policy = lower_policy = None

        material = average_difference >= self.materiality_threshold

        if higher_policy is None:
            recommendation = "The compared optimisation policies produce the same average pension capacity."
            explanation = "There is no average policy advantage in the tested common ages."
        elif material:
            recommendation = (
                f"{higher_policy} provides materially greater tax-efficient pension capacity "
                f"than {lower_policy} across the tested common ages."
            )
            explanation = (
                f"The average difference is £{average_difference:,.0f} per year, "
                f"with the largest difference of £{maximum_difference:,.0f} at age "
                f"{maximum_difference_age}."
            )
        else:
            recommendation = (
                f"{higher_policy} provides greater tax-efficient pension capacity, "
                "but the average difference is not material at the configured threshold."
            )
            explanation = (
                f"The average difference is £{average_difference:,.0f} per year; "
                f"the largest difference is £{maximum_difference:,.0f} at age "
                f"{maximum_difference_age}."
            )

        return OptimisationDecision(
            higher_policy=higher_policy,
            lower_policy=lower_policy,
            average_difference=round(average_difference, 2),
            maximum_difference=round(maximum_difference, 2),
            maximum_difference_age=maximum_difference_age,
            material=material,
            recommendation=recommendation,
            explanation=explanation,
        )
