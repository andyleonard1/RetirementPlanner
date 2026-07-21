"""
Inflation Engine

Calculates inflation-adjusted values for each retirement year.
"""

class InflationEngine:

    def __init__(self, assumptions):
        self.assumptions = assumptions

    def apply(self, timeline):

        inflation = self.assumptions.get("inflation_rate")

        factor = 1.0

        for year in timeline:

            year.inflation_factor = round(factor, 6)

            factor *= (1 + inflation)

        return timeline