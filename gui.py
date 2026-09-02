"""Launch the RetirementPlanner scenario-comparison desktop GUI."""
from __future__ import annotations

from planner.assumptions import Assumptions
from planner.funds.portfolio_historical_statistics import PortfolioHistoricalStatisticsCalculator
from planner.projection.scenario_projection_comparison import ScenarioProjectionComparisonRunner
from planner.projection.scenario_projection_view_model import ScenarioProjectionViewModel
from planner.gui.scenario_projection_window import ScenarioProjectionWindow


def build_default_view_model() -> ScenarioProjectionViewModel:
    """Build the same deterministic three-scenario view model used by tests."""
    statistics = PortfolioHistoricalStatisticsCalculator().calculate(
        {"Aviva": 0.75, "Sky": 0.25},
        {"Aviva": [0.10, 0.02, 0.08], "Sky": [0.20, 0.04, 0.16]},
    )
    comparison = ScenarioProjectionComparisonRunner().run(
        assumptions=Assumptions(), statistics=statistics
    )
    return ScenarioProjectionViewModel.from_comparison(comparison)


def main() -> None:
    ScenarioProjectionWindow(build_default_view_model()).run()


if __name__ == "__main__":
    main()
