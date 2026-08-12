"""
Recommendation Sensitivity

Measures how stable the recommended retirement age is when the
recommended age is recalculated under small assumption changes.

This layer is deliberately isolated from the existing recommendation
engine so that sensitivity analysis cannot change the current decision.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class RecommendationSensitivity:
    baseline_age: int
    ages: tuple[int, ...]
    confidence: str
    stable: bool


class RecommendationSensitivityEngine:
    """
    Evaluate recommendation stability from a collection of recommended ages.

    The input is a sequence of ages produced by independent scenario runs.
    """

    def analyse(self, baseline_age, scenario_ages):
        ages = tuple(sorted(set(int(age) for age in scenario_ages)))

        if not ages:
            return RecommendationSensitivity(
                baseline_age=baseline_age,
                ages=(),
                confidence="Low",
                stable=False,
            )

        spread = max(ages) - min(ages)

        if spread == 0:
            confidence = "High"
        elif spread <= 2:
            confidence = "Moderate"
        else:
            confidence = "Low"

        return RecommendationSensitivity(
            baseline_age=int(baseline_age),
            ages=ages,
            confidence=confidence,
            stable=(spread == 0),
        )
