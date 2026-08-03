"""
Planner Result

Contains everything produced by a planning run.
"""

from dataclasses import dataclass


@dataclass
class PlannerResult:

    timeline: list

    summary: dict

    recommendation: dict | None = None

    risk: dict | None = None