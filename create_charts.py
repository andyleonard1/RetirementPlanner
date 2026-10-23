"""
Create retirement charts.
"""

from planner.assumptions import Assumptions
from planner.planner import RetirementPlanner
from planner.chart_engine import ChartEngine


def main():

    assumptions = Assumptions()

    planner = RetirementPlanner(assumptions)

    result = planner.run()

    timeline = result.timeline

    ChartEngine().create_all(timeline)

    print("Charts created.")


if __name__ == "__main__":
    main()