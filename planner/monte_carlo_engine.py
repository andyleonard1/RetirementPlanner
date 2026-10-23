"""
Monte Carlo Engine

Runs multiple retirement simulations using random investment returns.
"""

import copy
import logging
import random

from planner.models import MonteCarloResult
from planner.planner import RetirementPlanner
from planner.investment_return import InvestmentReturnResolver
from planner.assumption_resolver import AssumptionResolver

logger = logging.getLogger(__name__)


class MonteCarloEngine:

    def __init__(self, assumptions):

        self.assumptions = assumptions

    def run(self, iterations=5000, seed=None):

        if iterations <= 0:
            raise ValueError("iterations must be greater than zero")

        rng = random.Random(seed)
        inflation_rng = random.Random(
            None if seed is None else seed + 1_000_003
        )

        logger.info(
            f"Running Monte Carlo ({iterations:,} iterations)"
        )

        ending_assets = []

        successes = 0
        return_config = InvestmentReturnResolver.resolve(self.assumptions)

        for _ in range(iterations):

            assumptions = copy.deepcopy(
                self.assumptions
            )

            growth = rng.gauss(

                return_config.net_monte_carlo_expected_return,

                AssumptionResolver(assumptions).investment_volatility(),

            )

            assumptions.data[
                "pension_growth"
            ] = growth

            # ``growth`` is the net simulated return. Feed the equivalent
            # gross return into the canonical projection assumption so the
            # existing charge boundary remains authoritative.
            charge_resolver = AssumptionResolver(assumptions)
            total_charge = (
                charge_resolver.platform_charge()
                + charge_resolver.fund_charge()
            )
            assumptions.data[
                "expected_investment_return"
            ] = growth + total_charge

            current_age = assumptions.get("current_age")
            projection_end_age = assumptions.get("projection_end_age")
            years = (
                max(1, int(projection_end_age) - int(current_age) + 1)
                if current_age is not None and projection_end_age is not None
                else 1
            )
            inflation_mean = float(AssumptionResolver(assumptions).get("inflation_rate", 0.0))
            inflation_volatility = AssumptionResolver(assumptions).inflation_volatility()
            assumptions.data[
                "_monte_carlo_inflation_path"
            ] = [
                inflation_rng.normalvariate(
                    inflation_mean,
                    inflation_volatility,
                )
                for _ in range(years)
            ]

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