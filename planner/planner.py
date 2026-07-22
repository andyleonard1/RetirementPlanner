"""
Retirement Planner

Coordinates the retirement planning process by running
each engine in the correct order.
"""

from planner.timeline import TimelineEngine

from planner.state_pension import StatePensionEngine
from planner.savings_engine import SavingsEngine
from planner.isa_engine import ISAEngine

from planner.cashflow_engine import CashFlowEngine
from planner.tax_optimizer_engine import TaxOptimizerEngine
from planner.strategy_engine import StrategyEngine
from planner.withdrawal_engine import WithdrawalEngine
from planner.tax_engine import TaxEngine
from planner.pension_engine import PensionEngine

from planner.summary_engine import SummaryEngine


class RetirementPlanner:

    def __init__(self, assumptions):
        self.assumptions = assumptions

    def run(self):

        #
        # Build retirement timeline
        #
        timeline = TimelineEngine(self.assumptions).build()

        #
        # Populate yearly balances and incomes
        #
        StatePensionEngine(self.assumptions).apply(timeline)
        SavingsEngine(self.assumptions).apply(timeline)
        ISAEngine(self.assumptions).apply(timeline)

        #
        # Calculate spending requirement
        #
        CashFlowEngine(self.assumptions).apply(timeline)

        #
        # Calculate tax-efficient pension limit
        #
        TaxOptimizerEngine(self.assumptions).apply(timeline)

        #
        # Decide where income comes from
        #
        StrategyEngine(self.assumptions).apply(timeline)

        #
        # Convert strategy into withdrawals
        #
        WithdrawalEngine(self.assumptions).apply(timeline)

        #
        # Gross-up withdrawals for tax
        #
        TaxEngine(self.assumptions).apply(timeline)

        #
        # Apply pension growth and withdrawals
        #
        PensionEngine(self.assumptions).apply(timeline)

        #
        # Produce summary
        #
        summary = SummaryEngine(self.assumptions).apply(timeline)

        return timeline, summary