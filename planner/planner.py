"""
Retirement Planner

Coordinates the retirement planning process by running each
planning engine in sequence and returning a PlannerResult.
"""

import logging
import time

from planner.planner_result import PlannerResult
from planner.timeline import TimelineEngine

from planner.state_pension import StatePensionEngine
from planner.savings_engine import SavingsEngine
from planner.isa_engine import ISAEngine
from planner.cashflow_engine import CashFlowEngine
from planner.optimisation_engine import OptimisationEngine
from planner.strategy_engine import StrategyEngine
from planner.withdrawal_engine import WithdrawalEngine
from planner.tax_engine import TaxEngine
from planner.pension_engine import PensionEngine
from planner.summary_engine import SummaryEngine

logger = logging.getLogger(__name__)


class RetirementPlanner:

    def __init__(self, assumptions):

        self.assumptions = assumptions

        #
        # Order matters!
        #
        self.engines = [

            StatePensionEngine,

            SavingsEngine,

            ISAEngine,

            CashFlowEngine,

            OptimisationEngine,

            StrategyEngine,

            WithdrawalEngine,

            TaxEngine,

            PensionEngine,

        ]

    # -----------------------------------------------------

    def build_timeline(self):

        logger.info("Building retirement timeline")

        return TimelineEngine(
            self.assumptions
        ).build()

    # -----------------------------------------------------

    def run_engines(self, timeline):

        for engine_class in self.engines:

            logger.info(
                "Running %s",
                engine_class.__name__,
            )

            engine = engine_class(
                self.assumptions
            )

            engine.apply(timeline)

    # -----------------------------------------------------

    def build_summary(self, timeline):

        logger.info("Running SummaryEngine")

        return SummaryEngine(
            self.assumptions
        ).apply(timeline)

    # -----------------------------------------------------

    def run(self):

        logger.info(
            "Starting retirement calculation"
        )

        start = time.perf_counter()

        timeline = self.build_timeline()

        self.run_engines(timeline)

        summary = self.build_summary(timeline)

        elapsed = (
            time.perf_counter() - start
        )

        logger.info(
            "Calculation complete (%.3f sec)",
            elapsed,
        )

        return PlannerResult(
            timeline=timeline,
            summary=summary,

    #
    # Overall success of the plan.
    #
            success=summary.get(
                "success",
                False,
            ),
    )