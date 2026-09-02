"""Launch the RetirementPlanner scenario-comparison desktop GUI."""
from __future__ import annotations

from planner.assumptions import Assumptions
from planner.funds.portfolio_historical_statistics import PortfolioHistoricalStatisticsCalculator
from planner.gui.scenario_projection_application import ScenarioProjectionApplication
from planner.gui.scenario_projection_window import ScenarioProjectionWindow
from planner.projection.scenario_projection_view_model import ScenarioProjectionViewModel


DEFAULT_ALLOCATIONS = {"Aviva": 0.75, "Sky": 0.25}
DEFAULT_FUND_RETURNS = {
    "Aviva": [0.10, 0.02, 0.08],
    "Sky": [0.20, 0.04, 0.16],
}


def build_default_application() -> tuple[ScenarioProjectionApplication, ScenarioProjectionViewModel]:
    """Build the application boundary and its initial deterministic view model."""
    assumptions = Assumptions()
    application = ScenarioProjectionApplication(assumptions)
    view_model = application.build_view_model(
        allocations=DEFAULT_ALLOCATIONS,
        fund_returns=DEFAULT_FUND_RETURNS,
    )
    return application, view_model


def build_default_view_model() -> ScenarioProjectionViewModel:
    """Backward-compatible helper returning the initial view model."""
    _, view_model = build_default_application()
    return view_model


def main() -> None:
    application, view_model = build_default_application()
    ScenarioProjectionWindow(
        view_model,
        application=application,
        allocations=DEFAULT_ALLOCATIONS,
        fund_returns=DEFAULT_FUND_RETURNS,
    ).run()


if __name__ == "__main__":
    main()
