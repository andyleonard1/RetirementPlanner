"""
Compare retirement strategies.
"""

from planner.scenario_engine import ScenarioEngine

from reports.comparison_report import ComparisonReport


def main():

    engine = ScenarioEngine()

    results = engine.compare_strategies()

    ComparisonReport().print(results)


if __name__ == "__main__":
    main()