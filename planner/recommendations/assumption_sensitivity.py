"""
Assumption Sensitivity

Runs recommendation-age sensitivity against a supplied set of
assumption variants. This layer is deliberately isolated from the
normal recommendation path.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class AssumptionSensitivityResult:
    baseline_age: int
    recommended_ages: tuple[int, ...]
    confidence: str
    min_age: int | None
    max_age: int | None


class AssumptionSensitivityEngine:
    def analyse(self, baseline_age, recommended_ages):
        ages = tuple(sorted(set(int(age) for age in recommended_ages)))

        if not ages:
            return AssumptionSensitivityResult(
                baseline_age=int(baseline_age),
                recommended_ages=(),
                confidence="Low",
                min_age=None,
                max_age=None,
            )

        spread = max(ages) - min(ages)

        if spread == 0:
            confidence = "High"
        elif spread <= 2:
            confidence = "Moderate"
        else:
            confidence = "Low"

        return AssumptionSensitivityResult(
            baseline_age=int(baseline_age),
            recommended_ages=ages,
            confidence=confidence,
            min_age=min(ages),
            max_age=max(ages),
        )
