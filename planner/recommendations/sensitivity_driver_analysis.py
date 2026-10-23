"""
Analyse which assumption dimension is associated with changes in the
recommended retirement age.

This is an analysis-only layer. It does not modify the live recommendation.
"""

from dataclasses import dataclass
from collections import Counter


@dataclass(frozen=True, slots=True)
class DriverAnalysis:
    dimension: str
    groups: tuple[tuple[object, tuple[int | None, ...]], ...]


class SensitivityDriverAnalysis:
    def _group(self, runs, attribute):
        grouped = {}
        for run in runs:
            value = getattr(run.case, attribute)
            grouped.setdefault(value, []).append(run.recommended_age)
        return tuple(
            (value, tuple(ages))
            for value, ages in sorted(grouped.items(), key=lambda item: item[0])
        )

    def analyse(self, runs):
        return (
            DriverAnalysis("pension_growth", self._group(runs, "pension_growth")),
            DriverAnalysis("net_spending", self._group(runs, "net_spending")),
            DriverAnalysis("isa_growth", self._group(runs, "isa_growth")),
        )

    def recommendation_counts(self, runs):
        return Counter(
            run.recommended_age
            for run in runs
            if run.recommended_age is not None
        )
