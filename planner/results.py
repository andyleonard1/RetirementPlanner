"""
Standard result objects returned by legacy/standalone planning engines.

The main RetirementPlanner already returns PlannerResult.  These small
result objects bring the older scenario, decision, risk and chart helpers
onto the same attribute-based contract while retaining read-only mapping-
style access for existing callers during the migration.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class ScenarioResult:
    name: str
    timeline: list
    summary: dict
    final_year: object

    def __getitem__(self, key):
        return getattr(self, key)


@dataclass(slots=True)
class RiskResult:
    score: int
    rating: str
    risks: list[str]

    def __getitem__(self, key):
        return getattr(self, key)


@dataclass(slots=True)
class DecisionResult:
    recommended: str
    summary: dict
    runner_up: ScenarioResult | None
    all: list[ScenarioResult]
    risk: RiskResult

    def __getitem__(self, key):
        return getattr(self, key)


@dataclass(slots=True)
class HistogramResult:
    labels: list[str]
    counts: list[int]

    def __getitem__(self, key):
        return getattr(self, key)
