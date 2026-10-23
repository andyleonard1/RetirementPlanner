"""
Inflation Engine

Calculates inflation-adjusted values for each retirement year.
"""

from planner.assumption_resolver import AssumptionResolver


class InflationEngine:

    def __init__(self, assumptions):
        self.assumptions = assumptions

    def apply(self, timeline):

        configured_inflation = AssumptionResolver(self.assumptions).inflation_rate()
        simulated_path = self.assumptions.get("_monte_carlo_inflation_path")

        factor = 1.0

        for index, year in enumerate(timeline):

            if simulated_path is not None and index < len(simulated_path):
                inflation = float(simulated_path[index])
            else:
                inflation = configured_inflation

            year.inflation_rate = inflation
            year.inflation_factor = round(factor, 6)

            factor *= (1 + inflation)

        return timeline
