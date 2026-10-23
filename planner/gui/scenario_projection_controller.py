"""Calculation-free controller boundary for the scenario projection GUI."""
from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from math import isfinite
from typing import Any, Mapping, Sequence

from planner.projection import (
    ScenarioProjectionApplication,
    ScenarioProjectionInputs,
    ScenarioProjectionWorkflowResult,
)
from planner.projection.scenario_projection_view_model import ScenarioProjectionViewModel


@dataclass(frozen=True)
class ScenarioProjectionRunResult:
    """Immutable result of a GUI projection run and its shared report boundary."""

    inputs: ScenarioProjectionInputs
    view_model: ScenarioProjectionViewModel
    workflow_result: ScenarioProjectionWorkflowResult


class ScenarioProjectionGuiController:
    """Coordinate GUI events without owning widgets or financial calculations."""

    def __init__(
        self,
        application: ScenarioProjectionApplication,
        allocations: Mapping[str, float],
        fund_returns: Mapping[str, Sequence[float]],
    ) -> None:
        if not isinstance(application, ScenarioProjectionApplication):
            raise TypeError("application must be ScenarioProjectionApplication")
        self.application = application
        self.allocations = dict(allocations)
        self.fund_returns = {name: tuple(values) for name, values in fund_returns.items()}
        self._selected_scenarios = self.application.inputs().scenarios

    @property
    def selected_scenarios(self) -> tuple[str, ...]:
        return self._selected_scenarios

    @staticmethod
    def parse_inputs(
        starting_pension: str,
        retirement_age: str,
        projection_end_age: str,
        selected_scenarios: Sequence[str],
    ) -> ScenarioProjectionInputs:
        """Parse GUI strings into the validated application input contract."""
        try:
            pension = float(starting_pension.replace(",", "").replace("£", "").strip())
            retirement = int(retirement_age.strip())
            end_age = int(projection_end_age.strip())
        except (AttributeError, ValueError) as exc:
            raise ValueError("pension and ages must be valid numeric values") from exc
        if not isfinite(pension):
            raise ValueError("starting pension must be a finite numeric value")
        scenarios = tuple(
            dict.fromkeys(str(name).strip().lower() for name in selected_scenarios if str(name).strip())
        )
        supported = {"conservative", "central", "optimistic"}
        invalid = tuple(name for name in scenarios if name not in supported)
        if invalid:
            raise ValueError(f"unsupported scenario(s): {', '.join(invalid)}")
        return ScenarioProjectionInputs(pension, retirement, end_age, scenarios)

    def run(
        self,
        starting_pension: str,
        retirement_age: str,
        projection_end_age: str,
        selected_scenarios: Sequence[str],
    ) -> ScenarioProjectionRunResult:
        """Parse, validate, apply and rebuild through the application boundary."""
        inputs = self.parse_inputs(
            starting_pension, retirement_age, projection_end_age, selected_scenarios
        )
        previous_inputs = self.application.inputs()
        try:
            self.application.apply_inputs(inputs)
            workflow_result = self.application.run_report_workflow(
                allocations=self.allocations,
                fund_returns=self.fund_returns,
                scenarios=inputs.scenarios,
            )
        except Exception:
            # Keep a failed GUI run from leaving the planner in a half-applied
            # state. The prior in-memory values remain the active inputs; the
            # caller can still inspect/handle the original exception.
            self.application.apply_inputs(previous_inputs)
            raise
        self._selected_scenarios = inputs.scenarios
        return ScenarioProjectionRunResult(
            workflow_result.inputs,
            workflow_result.view_model,
            workflow_result,
        )

    def assumptions_json(self) -> str:
        """Return the complete editable assumptions document as formatted JSON."""
        return json.dumps(
            self.application.assumptions.data,
            indent=4,
            ensure_ascii=False,
            allow_nan=False,
        ) + "\n"

    @staticmethod
    def parse_assumptions_json(text: str) -> dict[str, Any]:
        """Parse a complete assumptions document without mutating application state."""
        if not isinstance(text, str):
            raise TypeError("assumptions JSON must be text")
        try:
            candidate = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid assumptions JSON: {exc.msg}") from exc
        if not isinstance(candidate, dict):
            raise ValueError("assumptions JSON root must be an object")
        return candidate

    def validate_assumptions_json(self, text: str) -> dict[str, Any]:
        """Parse and validate an assumptions document without applying it."""
        candidate = self.parse_assumptions_json(text)
        assumptions = self.application.assumptions
        previous = deepcopy(assumptions.data)
        try:
            assumptions.data = deepcopy(candidate)
            assumptions.validate()
        except Exception:
            assumptions.data = previous
            raise
        assumptions.data = previous
        return candidate

    def format_assumptions_json(self, text: str) -> str:
        """Return canonically formatted validated assumptions JSON."""
        candidate = self.validate_assumptions_json(text)
        return json.dumps(candidate, indent=4, ensure_ascii=False, allow_nan=False) + "\n"

    def apply_assumptions_json(self, text: str) -> None:
        """Validate and apply a complete assumptions JSON document in memory.

        The existing in-memory assumptions are restored when parsing or
        validation fails, so an advanced GUI edit cannot leave a partial
        configuration behind. Persistence remains an explicit Save action.
        """
        candidate = self.parse_assumptions_json(text)
        assumptions = self.application.assumptions
        previous = deepcopy(assumptions.data)
        try:
            assumptions.data = candidate
            assumptions.validate()
        except Exception:
            assumptions.data = previous
            raise
        self._selected_scenarios = self.application.inputs().scenarios

    def assumptions_changes(self) -> tuple[str, ...]:
        """Return changed assumption paths in deterministic order for GUI display."""
        return tuple(change.path for change in self.application.assumptions.changes())

    def assumptions_text_has_unapplied_changes(self, text: str) -> bool:
        """Return whether editor text differs from the active assumptions document.

        Parsing is deliberately non-mutating. Invalid editor text is treated as
        pending work so a close action cannot silently discard an edit merely
        because the JSON is currently malformed.
        """
        if not isinstance(text, str):
            raise TypeError("assumptions JSON must be text")
        try:
            candidate = self.parse_assumptions_json(text)
        except (TypeError, ValueError):
            return text != self.assumptions_json()
        return candidate != self.application.assumptions.data

    def assumptions_editor_status(self, text: str) -> str:
        """Return a deterministic editor status for text and applied changes."""
        pending_text = self.assumptions_text_has_unapplied_changes(text)
        applied = self.assumptions_changes()
        if pending_text and applied:
            return f"Editor has unapplied text; {len(applied)} applied assumption change(s) are unsaved."
        if pending_text:
            return "Editor has unapplied text changes."
        if applied:
            return f"{len(applied)} applied assumption change(s) are unsaved."
        return "Editor matches the active assumptions; no unsaved changes."

    def discard_assumptions_changes(self) -> None:
        """Restore the last persisted assumptions baseline in memory."""
        assumptions = self.application.assumptions
        previous = deepcopy(assumptions.data)
        try:
            assumptions.data = deepcopy(assumptions._baseline_data)
            assumptions.validate()
        except Exception:
            assumptions.data = previous
            raise
        self._selected_scenarios = self.application.inputs().scenarios

    def save(self) -> None:
        """Persist assumptions only after an explicit GUI save action."""
        self.application.assumptions.save()

    def reload_saved(self) -> ScenarioProjectionInputs:
        """Reload validated saved assumptions without leaving partial state on failure."""
        assumptions = self.application.assumptions
        previous = deepcopy(assumptions.data)
        previous_baseline = deepcopy(assumptions._baseline_data)
        try:
            assumptions.load()
            assumptions.validate()
        except Exception:
            assumptions.data = previous
            assumptions._baseline_data = previous_baseline
            raise
        self._selected_scenarios = self.application.inputs().scenarios
        return self.application.inputs()
