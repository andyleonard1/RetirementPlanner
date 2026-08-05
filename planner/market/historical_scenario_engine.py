"""
Historical Scenario Engine

Assigns a sequence of historical market returns
to each retirement year.
"""

import logging

logger = logging.getLogger(__name__)


class HistoricalScenarioEngine:

    def __init__(self, market_data):

        self.market_data = market_data

    def apply(self, timeline, start_index=0):

        logger.info("Running HistoricalScenarioEngine")

        market_years = len(self.market_data)

        for i, year in enumerate(timeline):

            market = self.market_data.get_year(
                (start_index + i) % market_years
            )

            year.market_year = market.year
            year.market_data = market

        return timeline