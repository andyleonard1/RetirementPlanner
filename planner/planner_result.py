"""
Planner Result

Contains everything produced by a planning run.
"""

from dataclasses import dataclass, field


@dataclass
class PlannerResult:

    #
    # Full year-by-year retirement timeline.
    #
    timeline: list

    #
    # Summary statistics.
    #
    summary: dict

    #
    # Goal evaluation.
    #
    goals: list = field(default_factory=list)

    #
    # Overall success flag.
    #
    success: bool = False

    #
    # Optional future features.
    #
    recommendation: dict | None = None

    risk: dict | None = None

    # Configuration changes present when this projection was run.
    assumption_changes: tuple = field(default_factory=tuple)
    # Why this projection differs from the saved/base configuration.
    audit_context: str = "user"
