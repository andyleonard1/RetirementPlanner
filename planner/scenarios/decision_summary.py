"""
Decision Summary

Contains the key financial figures used to compare
the recommended retirement age with retiring one year later.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class DecisionSummary:

    recommended_age: int

    ending_pension: float

    ending_isa: float

    ending_savings: float

    ending_assets: float

    later_age: int | None = None

    later_ending_assets: float | None = None

    additional_assets_from_waiting: float | None = None

    earliest_age_score: float | None = None

    ending_assets_score: float | None = None

    waiting_efficiency_score: float | None = None

    total_score: float | None = None
