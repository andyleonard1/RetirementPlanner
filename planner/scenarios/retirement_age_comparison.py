"""
Retirement Age Comparison

Represents the financial outcome of retiring at a
specific age compared with the previous tested age.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class RetirementAgeComparison:

    retirement_age: int

    success: bool

    ending_assets: float

    ending_pension: float

    ending_isa: float

    ending_savings: float

    total_tax: float

    change_from_previous_age: float | None = None
