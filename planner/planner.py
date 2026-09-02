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
from planner.optimisation_decision_support import OptimisationDecisionSupport
from planner.strategy_engine import StrategyEngine
from planner.withdrawal_engine import WithdrawalEngine
from planner.tax_engine import TaxEngine
from planner.pension_engine import PensionEngine
from planner.funds.projection_engine_integration import ProjectionReturnDecision
from planner.funds.fund_informed_projection import FundInformedProjection
from planner.funds.portfolio_historical_statistics import PortfolioHistoricalStatistics
from planner.summary_engine import SummaryEngine

logger = logging.getLogger(__name__)


class RetirementPlanner:

    def __init__(
        self,
        assumptions,
        audit_context="user",
        projection_return_decision: ProjectionReturnDecision | None = None,
    ):

        self.assumptions = assumptions
        self.audit_context = audit_context
        self.projection_return_decision = projection_return_decision

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

            if engine_class is PensionEngine:
                engine = engine_class(
                    self.assumptions,
                    self.projection_return_decision,
                )
            else:
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

    def run_with_portfolio_statistics(
        self,
        statistics: PortfolioHistoricalStatistics,
        scenario_name: str,
        legacy_return: float | None = None,
    ):
        """Run the complete retirement projection using a portfolio scenario.

        The ordinary ``run()`` path remains unchanged. This method is the
        explicit application boundary for fund-informed projection.
        """
        if not isinstance(statistics, PortfolioHistoricalStatistics):
            raise TypeError("statistics must be PortfolioHistoricalStatistics")

        if legacy_return is None:
            legacy_return = float(self.assumptions.get("pension_growth"))

        starting_pension = float(self.assumptions.get("starting_pension"))
        decision = FundInformedProjection().build_from_statistics(
            starting_pension=starting_pension,
            legacy_return=float(legacy_return),
            statistics=statistics,
            scenario_name=scenario_name,
        )

        self.projection_return_decision = decision.projection_return
        return self.run()

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

        assumption_changes = (
            self.assumptions.changes()
            if hasattr(self.assumptions, "changes")
            else ()
        )

        # Read-only comparison of the supported optimisation policies.
        # This is deliberately performed after the live engines so the
        # decision-support layer cannot affect the retirement calculation.
        optimisation_comparison = OptimisationEngine(
            self.assumptions
        ).compare_policies(timeline)
        optimisation_decision = OptimisationDecisionSupport().assess(
            optimisation_comparison
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
            assumption_changes=assumption_changes,
            audit_context=self.audit_context,
            optimisation_decision=optimisation_decision,
    )