"""
Retirement Planner

Coordinates the retirement planning process by running
each engine in the correct order.
"""

from planner.timeline import TimelineEngine
from planner.pension_engine import PensionEngine
from planner.state_pension import StatePensionEngine


class RetirementPlanner:

    def __init__(self, assumptions):
        self.assumptions = assumptions

    def run(self):

        # Build the timeline
        timeline = TimelineEngine(self.assumptions).build()

        # Populate financial data
        PensionEngine(self.assumptions).apply(timeline)
        StatePensionEngine(self.assumptions).apply(timeline)

        return timeline