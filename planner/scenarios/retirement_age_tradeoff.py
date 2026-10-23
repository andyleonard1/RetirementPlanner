"""
Retirement Age Trade-off

Represents the financial trade-off between retiring at the
recommended earliest successful age and waiting to a later
successful retirement age.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class RetirementAgeTradeoff:

    starting_age: int

    later_age: int

    years_waited: int

    starting_assets: float

    later_assets: float

    additional_assets: float

    additional_assets_per_year: float

    later_success: bool
