"""Optional desktop presentation components for RetirementPlanner."""

from .scenario_projection_window import ScenarioProjectionWindow, format_currency, format_percent

__all__ = ["ScenarioProjectionWindow", "format_currency", "format_percent"]
from .scenario_projection_application import ScenarioProjectionApplication, ScenarioProjectionInputs
