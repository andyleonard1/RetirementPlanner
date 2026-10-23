"""
Market History Engine

Applies historical market returns
to each RetirementYear.
"""

import logging

from planner.market.market_data import MarketData
from planner.market.portfolio import Portfolio

logger = logging.getLogger(__name__)


class MarketHistoryEngine:

    def __init__(self, assumptions):

        self.assumptions = assumptions

        self.market = MarketData()

        self.market.load()

        self.portfolio = Portfolio(

            equity_weight=assumptions.get(
                "equity_weight",
                0.60,
            ),

            bond_weight=assumptions.get(
                "bond_weight",
                0.40,
            ),
        )

    def apply(self, timeline):

        logger.info(
            "Running MarketHistoryEngine"
        )

        market_years = len(self.market)

        for index, year in enumerate(timeline):

            market = self.market.get_year(

                index % market_years

            )

            market = year.market_data

            year.market_year = market.year

            year.portfolio_return = annual_return

            year.pension_growth_rate = annual_return

            year.isa_growth_rate = annual_return

        return timeline