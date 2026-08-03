"""
Create a Retirement Planning PDF Report.
"""

from planner.assumptions import Assumptions
from planner.planner import RetirementPlanner
from planner.decision_engine import DecisionEngine
from planner.recommendation_engine import RecommendationEngine
from planner.chart_engine import ChartEngine

from reports.pdf_report import PDFReport


def main():

    #
    # Build retirement timeline
    #
    assumptions = Assumptions()

    planner = RetirementPlanner(assumptions)

    timeline, _ = planner.run()

    #
    # Generate charts
    #
    ChartEngine().create_all(timeline)

    #
    # Generate recommendation
    #
    decision = DecisionEngine().run()

    report = RecommendationEngine().apply(decision)

    #
    # Create PDF
    #
    PDFReport().create(report)


if __name__ == "__main__":
    main()