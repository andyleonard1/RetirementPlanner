"""Optional desktop presentation components for RetirementPlanner."""

from planner.projection import (
    ScenarioProjectionApplication,
    ScenarioProjectionInputs,
    ScenarioProjectionWorkflowResult,
)
from .scenario_projection_controller import ScenarioProjectionGuiController, ScenarioProjectionRunResult
from .scenario_projection_window import ScenarioProjectionWindow, format_currency, format_percent
from .event_services import GuiEventService, TkEventService, RecordingEventService
from .testability import DialogService, FileDialogService, RecordingDialog, RecordingFileDialog
from .workflow_state import ScenarioProjectionGuiState

__all__ = [
    "ScenarioProjectionApplication",
    "ScenarioProjectionInputs",
    "ScenarioProjectionWorkflowResult",
    "ScenarioProjectionGuiController",
    "ScenarioProjectionRunResult",
    "ScenarioProjectionWindow",
    "format_currency",
    "format_percent",
    "DialogService",
    "FileDialogService",
    "RecordingDialog",
    "RecordingFileDialog",
    "GuiEventService",
    "TkEventService",
    "RecordingEventService",
    "ScenarioProjectionGuiState",
]
