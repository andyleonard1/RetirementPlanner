"""
ISA Engine

Projects ISA value over retirement.
"""
import logging

from planner.contracts import AssumptionsProvider, Timeline
from planner.assumption_resolver import AssumptionResolver
from planner.investment_return import InvestmentReturnResolver

logger = logging.getLogger(__name__)


class ISAEngine:

    def __init__(self, assumptions: AssumptionsProvider):

        self.assumptions = assumptions
        self.starting_isa = assumptions.get("starting_isa")
        self.growth_rate = AssumptionResolver(assumptions).isa_growth_rate()

    def apply(self, timeline: Timeline) -> Timeline:
        logger.info("Running ISA Engine")
        isa = self.starting_isa

        for year in timeline:

            opening = isa
            growth_rate = InvestmentReturnResolver.scheduled_isa_return(self.assumptions, year.calendar_year)
            growth = opening * growth_rate
            year.isa_growth_rate = growth_rate
            contribution = float(year.isa_contribution)
            withdrawal = year.isa_used

            closing = (
                opening
                + growth
                + contribution
                - year.isa_used
            )

            year.isa_opening = round(opening, 2)
            year.isa_growth = round(growth, 2)
            year.isa_contribution = round(contribution, 2)
            year.isa_withdrawal = round(withdrawal, 2)
            year.isa_closing = round(closing, 2)

            isa = closing

        return timeline
