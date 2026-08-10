"""
Retirement Age Score

Represents the transparent scoring components used to compare
successful retirement ages without changing the recommendation engine.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class RetirementAgeScore:

    retirement_age: int
    success: bool
    earliest_age_score: float
    ending_assets_score: float
    waiting_efficiency_score: float
    total_score: float
