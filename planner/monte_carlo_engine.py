"""
Monte Carlo Engine

Runs multiple retirement simulations using random investment returns.
"""

import copy
import logging
import random

from planner.models import MonteCarloResult
from planner.planner import RetirementPlanner

logger = logging.getLogger(__name__)


class MonteCarloEngine:

    def __init__(self, assumptions):

        self.assumptions = assumptions

    def run(self, iterations=5000):

        logger.info(
            f"Running Monte Carlo ({iterations:,} iterations)"
        )

        ending_assets = []

        successes = 0

        for _ in range(iterations):

            assumptions = copy.deepcopy(
                self.assumptions
            )

            growth = random.gauss(

                assumptions.get("expected_return"),

                assumptions.get(
                    "investment_volatility"
                ),

            )

            assumptions.data[
                "pension_growth"
            ] = growth

            planner = RetirementPlanner(
                assumptions,
                audit_context="analysis",
            )

            result = planner.run()

            assets = result.summary["ending_assets"]

            ending_assets.append(assets)

            if assets > 0:
                successes += 1

        ending_assets.sort()

        count = len(ending_assets)

        minimum = ending_assets[0]

        maximum = ending_assets[-1]

        median = ending_assets[count // 2]

        percentile_5 = ending_assets[
            int(count * 0.05)
        ]

        percentile_95 = ending_assets[
            int(count * 0.95)
        ]

        success_rate = (
            successes / iterations
        ) * 100

        return MonteCarloResult(

            iterations=iterations,

            minimum=minimum,

            percentile_5=percentile_5,

            median=median,

            percentile_95=percentile_95,

            maximum=maximum,

            success_rate=success_rate,

            results=ending_assets,

        )