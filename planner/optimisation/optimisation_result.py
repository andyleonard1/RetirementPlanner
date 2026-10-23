"""
Optimisation Result

Represents the outcome of an optimisation run.
"""

from dataclasses import dataclass

from planner.planner_result import PlannerResult


@dataclass
class OptimisationResult:

    success: bool

    objective: str

    value: float

    planner_result: PlannerResult

    iterations: int