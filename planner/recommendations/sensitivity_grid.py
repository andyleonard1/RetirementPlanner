"""
Retirement recommendation sensitivity grid.

Defines the initial 27-case grid used to test recommendation stability
across pension growth, net spending and ISA growth. This module only
describes the cases; it does not alter the live recommendation.
"""

from dataclasses import dataclass
from itertools import product


@dataclass(frozen=True, slots=True)
class SensitivityCase:
    pension_growth: float
    net_spending: float
    isa_growth: float


class SensitivityGrid:
    PENSION_GROWTH_RATES = (0.03, 0.04, 0.05)
    NET_SPENDING = (34000, 35000, 36000)
    ISA_GROWTH_RATES = (0.03, 0.04, 0.05)

    def cases(self):
        return tuple(
            SensitivityCase(
                pension_growth=pension_growth,
                net_spending=net_spending,
                isa_growth=isa_growth,
            )
            for pension_growth, net_spending, isa_growth
            in product(
                self.PENSION_GROWTH_RATES,
                self.NET_SPENDING,
                self.ISA_GROWTH_RATES,
            )
        )
