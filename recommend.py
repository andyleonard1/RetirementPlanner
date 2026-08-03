"""
Recommend the best retirement strategy.
"""

from planner.decision_engine import DecisionEngine
from planner.recommendation_engine import RecommendationEngine

from reports.recommendation_report import RecommendationReport


def main():

    decision = DecisionEngine().run()

    report = RecommendationEngine().apply(decision)

    RecommendationReport().print(report)


if __name__ == "__main__":
    main()