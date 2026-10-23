"""
Create a Retirement Planning PDF Report.
"""

import copy

from planner.assumptions import Assumptions
from planner.planner import RetirementPlanner
from planner.scenarios.scenario import Scenario
from planner.scenarios.scenario_manager import ScenarioManager
from planner.chart_engine import ChartEngine
from planner.recommendations.sensitivity_runner import SensitivityRunner
from planner.recommendations.sensitivity_driver_analysis import SensitivityDriverAnalysis

from reports.pdf_report import PDFReport


def build_scenarios(
    assumptions,
    minimum_age=55,
    maximum_age=75,
):
    """
    Build one scenario for each retirement age.
    """

    scenarios = []

    for age in range(
        minimum_age,
        maximum_age + 1,
    ):

        scenario_assumptions = copy.deepcopy(
            assumptions
        )

        scenario_assumptions.set(
            "retirement_age",
            age,
        )

        scenarios.append(
            Scenario(
                name=f"Retire {age}",
                assumptions=scenario_assumptions,
            )
        )

    return scenarios


def main():

    #
    # Base assumptions
    #
    assumptions = Assumptions()

    #
    # Build retirement-age scenarios
    #
    manager = ScenarioManager()

    for scenario in build_scenarios(
        assumptions,
        minimum_age=55,
        maximum_age=75,
    ):
        manager.add(scenario)

    #
    # Generate decision and comparison data
    #
    decision = manager.decision_summary()

    age_comparison = (
        manager.retirement_age_comparison()
    )

    #
    # Test recommendation stability across the 27-case
    # assumption sensitivity grid.
    #
    sensitivity = SensitivityRunner().run_real(
        assumptions,
        minimum_age=55,
        maximum_age=75,
    )

    driver_analysis = SensitivityDriverAnalysis().analyse(
        sensitivity.runs
    )

    #
    # Determine recommended age
    #
    if decision is not None:
        recommended_age = (
            decision.recommended_age
        )
    else:
        recommended_age = (
            assumptions.get("retirement_age")
        )

    #
    # Run planner at recommended age
    #
    recommended_assumptions = copy.deepcopy(
        assumptions
    )

    recommended_assumptions.set(
        "retirement_age",
        recommended_age,
    )

    planner = RetirementPlanner(
        recommended_assumptions
    )

    result = planner.run()

    #
    # Generate charts
    #
    ChartEngine().create_all(
        result.timeline
    )

    #
    # Create PDF report using the current reporting architecture
    #
    PDFReport().create(
        result,
        decision,
        age_comparison,
        sensitivity=sensitivity,
        driver_analysis=driver_analysis,
    )


if __name__ == "__main__":
    main()