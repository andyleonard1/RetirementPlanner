"""
Retirement Planner

Coordinates the retirement planning process by running
each engine in the correct order.
"""

from planner.timeline import TimelineEngine
from planner.pension_engine import PensionEngine
from planner.state_pension import StatePensionEngine
from planner.savings_engine import SavingsEngine
from planner.isa_engine import ISAEngine
from planner.cashflow_engine import CashFlowEngine
from planner.withdrawal_engine import WithdrawalEngine
from planner.tax_engine import TaxEngine
from planner.strategy_engine import StrategyEngine

class RetirementPlanner:

    def __init__(self, assumptions):
        self.assumptions = assumptions

    def run(self):

        # Build the timeline
        timeline = TimelineEngine(self.assumptions).build()

        # Populate financial data
        StatePensionEngine(self.assumptions).apply(timeline)
        SavingsEngine(self.assumptions).apply(timeline)
        ISAEngine(self.assumptions).apply(timeline)
        CashFlowEngine(self.assumptions).apply(timeline)
        WithdrawalEngine(self.assumptions).apply(timeline)
        TaxEngine(self.assumptions).apply(timeline)
        PensionEngine(self.assumptions).apply(timeline)
        CashFlowEngine(self.assumptions).apply(timeline)
        StrategyEngine(self.assumptions).apply(timeline)
        WithdrawalEngine(self.assumptions).apply(timeline)
        TaxEngine(self.assumptions).apply(timeline)
        PensionEngine(self.assumptions).apply(timeline)
        return timeline