"""Tkinter presentation for the scenario projection view model and inputs."""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import NamedTemporaryFile

from math import isfinite
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from planner.projection import ScenarioProjectionApplication, ScenarioProjectionInputs
from planner.gui.scenario_projection_controller import ScenarioProjectionGuiController
from planner.gui.testability import DialogService, FileDialogService
from planner.gui.event_services import GuiEventService, TkEventService
from planner.gui.workflow_state import WORKFLOW_ACTIONS, ScenarioProjectionGuiState
from planner.projection.scenario_projection_export import export_snapshot_bundle
from planner.projection.scenario_projection_view_model import ScenarioProjectionViewModel


SUPPORTED_SCENARIOS = ("conservative", "central", "optimistic")

# Canonical presentation wiring for the workflow action vocabulary.  The
# workflow-state model owns permission decisions; this adapter owns only the
# presentation-side handler and control bindings.
@dataclass(frozen=True)
class WorkflowActionPresentation:
    """Immutable presentation descriptor for one workflow action."""

    action: str
    handler_name: str
    button_name: str


@dataclass(frozen=True)
class WorkflowActionBinding:
    """Immutable resolved presentation binding for one workflow action."""

    action: str
    handler: Any
    button: Any | None


EMPTY_WORKFLOW_ACTION_MAP: Mapping[str, Any] = MappingProxyType({})

WORKFLOW_ACTION_PRESENTATION = (
    WorkflowActionPresentation("run", "_run_projection", "_run_button"),
    WorkflowActionPresentation("save", "_save_assumptions", "_save_button"),
    WorkflowActionPresentation("reset", "_reset_inputs", "_reset_button"),
    WorkflowActionPresentation("reload", "_reload_saved_assumptions", "_reload_button"),
)

# Canonical keyboard aliases for the same workflow action vocabulary.  Keep
# event wiring declarative so shortcut coverage cannot silently drift from the
# button/event entry-point contract.
WORKFLOW_KEYBOARD_BINDINGS = (
    ("<Return>", "run", "_run_from_event"),
    ("<Escape>", "reset", "_reset_from_event"),
    ("<Alt-r>", "run", "_run_from_event"),
    ("<Alt-s>", "save", "_save_from_event"),
    ("<Alt-t>", "reset", "_reset_from_event"),
    ("<Alt-l>", "reload", "_reload_from_event"),
)


def format_currency(value: float) -> str:
    """Format a monetary value for display without changing its value."""
    return f"£{value:,.0f}"


def format_percent(value: float) -> str:
    """Format a decimal return as a percentage for display."""
    return f"{value:.1%}"


class ScenarioProjectionWindow:
    """Desktop window for editing projection inputs and refreshing results.

    The window owns presentation/event handling only. All financial calculations
    remain behind ``ScenarioProjectionApplication`` and its existing domain
    calculation boundaries.
    """

    def __init__(
        self,
        view_model: ScenarioProjectionViewModel,
        root: Any | None = None,
        *,
        application: ScenarioProjectionApplication | None = None,
        allocations: Mapping[str, float] | None = None,
        fund_returns: Mapping[str, Sequence[float]] | None = None,
        dialog: DialogService | None = None,
        file_dialog: FileDialogService | None = None,
        event_service: GuiEventService | None = None,
        report_suite_exporter: Any | None = None,
        report_pack_exporter: Any | None = None,
    ):
        if not isinstance(view_model, ScenarioProjectionViewModel):
            raise TypeError("view_model must be ScenarioProjectionViewModel")
        if application is not None and not isinstance(application, ScenarioProjectionApplication):
            raise TypeError("application must be ScenarioProjectionApplication")
        if application is not None and (allocations is None or fund_returns is None):
            raise ValueError("allocations and fund_returns are required with application")

        self.view_model = view_model
        self.application = application
        self.allocations = dict(allocations or {})
        self.fund_returns = {name: tuple(values) for name, values in (fund_returns or {}).items()}
        self.controller = (
            ScenarioProjectionGuiController(application, self.allocations, self.fund_returns)
            if application is not None else None
        )
        self._last_result_snapshot: Mapping[str, Any] | None = None
        self._last_workflow_result = None
        self._last_projection_signature = (
            application.inputs() if application is not None else None,
            json.dumps(application.assumptions.data, sort_keys=True, ensure_ascii=False, allow_nan=False) if application is not None else "",
        )
        self._root = root
        self._dialog = dialog
        self._file_dialog = file_dialog
        self._event_service = event_service
        self._report_suite_exporter = report_suite_exporter
        self._report_pack_exporter = report_pack_exporter
        self._keyboard_shortcuts_bound_service = None
        self._owns_root = root is None
        self._cards_frame = None
        self._table = None
        self._chart_canvas = None
        self._chart_accessibility_var = None
        self._chart_focus_index = 0
        self._content = None
        self._pension_var = None
        self._retirement_age_var = None
        self._end_age_var = None
        self._scenario_vars: dict[str, Any] = {}
        self._status_var = None
        self._selection_var = None
        self._validation_var = None
        self._validation_label = None
        self._results_status_var = None
        self._entry_widgets = []
        self._scenario_checkbuttons = {}
        self._run_button = None
        self._save_button = None
        self._reset_button = None
        self._reload_button = None
        self._reports_button = None
        self._report_pack_button = None
        self._assumptions_editor = None
        self._assumptions_text = None
        self._built = False
        self._closed = False
        self._workflow_state = ScenarioProjectionGuiState()
        self._workflow_action_binding_registry: Mapping[str, WorkflowActionBinding] | None = None
        self._workflow_action_button_map: Mapping[str, Any] | None = None
        self._workflow_action_handler_map: Mapping[str, Any] | None = None
        self._workflow_action_button_map_source: Mapping[str, WorkflowActionBinding] | None = None
        self._workflow_action_handler_map_source: Mapping[str, WorkflowActionBinding] | None = None

    @property
    def workflow_state(self) -> ScenarioProjectionGuiState:
        """Return the immutable workflow state used by the presentation adapter."""
        return self._workflow_state

    @property
    def is_closed(self) -> bool:
        """Whether the desktop window has been closed."""
        return self._closed

    @staticmethod
    def parse_inputs(
        starting_pension: str,
        retirement_age: str,
        projection_end_age: str,
        selected_scenarios: Sequence[str],
    ) -> ScenarioProjectionInputs:
        """Backward-compatible parsing helper delegated to the controller."""
        return ScenarioProjectionGuiController.parse_inputs(
            starting_pension, retirement_age, projection_end_age, selected_scenarios
        )

    @property
    def results_are_current(self) -> bool:
        """Whether the displayed projection matches the current GUI assumptions and inputs."""
        if self.application is None or self.controller is None:
            return True
        if self._pension_var is not None and self.has_pending_changes:
            return False
        base_inputs = self.application.inputs()
        expected_inputs = ScenarioProjectionInputs(
            base_inputs.starting_pension,
            base_inputs.retirement_age,
            base_inputs.projection_end_age,
            self.selected_scenarios,
        )
        expected_signature = (
            expected_inputs,
            json.dumps(self.application.assumptions.data, sort_keys=True, ensure_ascii=False, allow_nan=False),
        )
        return expected_signature == getattr(self, "_last_projection_signature", expected_signature)

    def _current_result_snapshot(self) -> Mapping[str, Any]:
        """Return the single published presentation snapshot for current results."""
        if self._closed:
            raise RuntimeError("projection window is closed; result export is unavailable")
        if not self.results_are_current:
            raise RuntimeError("projection results are stale; run projection before exporting results")
        snapshot = self._last_result_snapshot
        if snapshot is None:
            snapshot = self.view_model.report_snapshot()
            self._last_result_snapshot = snapshot
        return snapshot

    @staticmethod
    def _mutable_result_value(value: Any) -> Any:
        """Recreate ordinary dict/list containers from an immutable snapshot."""
        if isinstance(value, Mapping):
            return {key: ScenarioProjectionWindow._mutable_result_value(item) for key, item in value.items()}
        if isinstance(value, tuple):
            return [ScenarioProjectionWindow._mutable_result_value(item) for item in value]
        return value

    def _current_workflow_result(self):
        """Return the current workflow boundary without triggering recalculation."""
        if self._closed:
            raise RuntimeError("projection window is closed; result export is unavailable")
        self._current_result_snapshot()
        result = self._last_workflow_result
        if result is not None:
            return result
        if self.application is None or self.controller is None:
            raise RuntimeError("a live application is required for report-suite export")
        from planner.projection import ScenarioProjectionWorkflowResult
        from planner.projection.scenario_projection_report import ScenarioProjectionReport

        snapshot = self._last_result_snapshot
        if snapshot is None:
            raise RuntimeError("projection results are unavailable; run projection before exporting reports")
        inputs = self.application.inputs()
        report = ScenarioProjectionReport()
        result = ScenarioProjectionWorkflowResult(
            inputs=ScenarioProjectionInputs(
                inputs.starting_pension,
                inputs.retirement_age,
                inputs.projection_end_age,
                self.selected_scenarios,
            ),
            view_model=self.view_model,
            snapshot=snapshot,
            report_payload=report.build_from_snapshot(snapshot),
            report_text=report.render_text_from_snapshot(snapshot),
        )
        self._last_workflow_result = result
        return result

    def current_result_snapshot(self) -> Mapping[str, Any]:
        """Return the immutable snapshot published for the current projection result."""
        return self._current_result_snapshot()

    def current_result_report_payload(self) -> dict:
        """Return a defensive copy of the published current-result payload."""
        return self._mutable_result_value(self.current_result_snapshot()["payload"])

    def current_result_report_text(self) -> str:
        """Return the published deterministic report text for current results."""
        return str(self.current_result_snapshot()["text"])

    @staticmethod
    def _atomic_write_text(destination: Path, text: str) -> None:
        """Atomically publish text while cleaning up failed temporary writes."""
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary_name = None
        try:
            with NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=destination.parent,
                prefix=f".{destination.name}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                temporary_name = Path(handle.name)
                handle.write(text)
                handle.flush()
            temporary_name.replace(destination)
            temporary_name = None
        finally:
            if temporary_name is not None:
                temporary_name.unlink(missing_ok=True)

    def export_current_result_json(self, path: str | Any) -> None:
        """Write the current result snapshot payload to JSON without recalculating."""
        snapshot = self.current_result_snapshot()
        destination = Path(path)
        payload = self._mutable_result_value(snapshot["payload"])
        self._atomic_write_text(
            destination,
            json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        )

    def export_current_result_text(self, path: str | Any) -> None:
        """Write the current deterministic result report text without recalculating."""
        text = self.current_result_report_text()
        self._atomic_write_text(Path(path), text + "\n")

    @staticmethod
    def _atomic_write_bundle(files: Mapping[Path, str], *, overwrite: bool = False) -> None:
        """Backward-compatible forwarding seam for the shared export boundary."""
        from planner.projection.scenario_projection_export import _atomic_write_bundle

        _atomic_write_bundle(files, overwrite=overwrite)

    def export_current_result_bundle(
        self,
        directory: str | Any,
        stem: str = "retirement_projection",
        *,
        overwrite: bool = False,
    ) -> dict[str, Path]:
        """Export JSON/text companions from the shared current-result snapshot."""
        snapshot = self.current_result_snapshot()
        return export_snapshot_bundle(
            snapshot,
            directory,
            stem,
            overwrite=overwrite,
        )

    @property
    def is_dirty(self) -> bool:
        """Whether assumptions have changed since the last load/save baseline."""
        return bool(self.application and self.application.assumptions.has_changes())

    @property
    def selected_scenarios(self) -> tuple[str, ...]:
        """Return the currently applied scenario selection."""
        if self.controller is not None:
            return self.controller.selected_scenarios
        return self.view_model.scenario_names

    @property
    def pending_selected_scenarios(self) -> tuple[str, ...]:
        """Return scenario checkbutton selection waiting for the next run."""
        if self._scenario_vars:
            return tuple(name for name, variable in self._scenario_vars.items() if bool(variable.get()))
        return self.selected_scenarios

    @property
    def has_pending_changes(self) -> bool:
        """Whether editable controls differ from the currently applied state."""
        if self.application is None or self._pension_var is None:
            return False
        try:
            pension, retirement, end_age, scenarios = self._current_input_strings()
            inputs = self.application.inputs()
            parsed = self.parse_inputs(pension, retirement, end_age, scenarios)
        except (ValueError, TypeError):
            return True
        return (
            parsed.starting_pension != inputs.starting_pension
            or parsed.retirement_age != inputs.retirement_age
            or parsed.projection_end_age != inputs.projection_end_age
            or parsed.scenarios != self.selected_scenarios
        )

    def _current_input_strings(self) -> tuple[str, str, str, tuple[str, ...]]:
        if self._pension_var is None:
            inputs = self.application.inputs() if self.application else None
            if inputs is None:
                raise RuntimeError("editable inputs require an application")
            return (
                str(inputs.starting_pension),
                str(inputs.retirement_age),
                str(inputs.projection_end_age),
                self.selected_scenarios,
            )
        selected = tuple(name for name, var in self._scenario_vars.items() if bool(var.get()))
        return (
            self._pension_var.get(),
            self._retirement_age_var.get(),
            self._end_age_var.get(),
            selected,
        )

    def _set_input_controls(self, inputs: ScenarioProjectionInputs, scenarios: Sequence[str] | None = None) -> None:
        if self._pension_var is not None:
            self._pension_var.set(str(inputs.starting_pension))
            self._retirement_age_var.set(str(inputs.retirement_age))
            self._end_age_var.set(str(inputs.projection_end_age))
            selected = set(scenarios if scenarios is not None else self.selected_scenarios)
            for name, variable in self._scenario_vars.items():
                variable.set(name in selected)
        self._refresh_status()

    def _pending_validation_message(self) -> str:
        """Return actionable validation feedback for the current GUI controls."""
        if self.application is None or self._pension_var is None:
            return ""
        try:
            self.parse_inputs(*self._current_input_strings())
        except (ValueError, TypeError) as exc:
            return str(exc)
        return ""

    def _refresh_status(self) -> None:
        validation_message = self._pending_validation_message()
        pending = self.has_pending_changes
        self._workflow_state = ScenarioProjectionGuiState.from_controls(
            pending_changes=pending,
            pending_valid=not bool(validation_message),
            dirty=self.is_dirty,
            closed=self._closed,
        )
        if self._status_var is not None:
            self._status_var.set(self._workflow_state.status)
        if self._validation_var is not None:
            self._validation_var.set(
                "Input check: " + validation_message if validation_message else "Input check: ready"
            )
        if self._results_status_var is not None:
            self._results_status_var.set(
                "Results: current projection" if self.results_are_current else "Results: stale — run projection to refresh"
            )
        if self._selection_var is not None:
            names = self.pending_selected_scenarios
            self._selection_var.set(
                "Selected scenarios: " + ", ".join(name.title() for name in names)
                if names else "Selected scenarios: none (run will be rejected)"
            )
        self._refresh_action_states(pending)

    def _workflow_action_contract(self) -> tuple[WorkflowActionBinding, ...]:
        """Resolve the immutable action descriptors to validated live bindings."""
        actions = tuple(descriptor.action for descriptor in WORKFLOW_ACTION_PRESENTATION)
        if actions != WORKFLOW_ACTIONS:
            raise RuntimeError(
                "workflow action presentation contract is out of sync with canonical actions"
            )

        handler_names = tuple(descriptor.handler_name for descriptor in WORKFLOW_ACTION_PRESENTATION)
        button_names = tuple(descriptor.button_name for descriptor in WORKFLOW_ACTION_PRESENTATION)
        if len(handler_names) != len(set(handler_names)):
            raise RuntimeError("workflow action presentation contract has duplicate handler bindings")
        if len(button_names) != len(set(button_names)):
            raise RuntimeError("workflow action presentation contract has duplicate button bindings")

        contract = []
        for descriptor in WORKFLOW_ACTION_PRESENTATION:
            if not isinstance(descriptor.action, str) or not descriptor.action:
                raise RuntimeError("workflow action presentation contract has an invalid action name")
            if not isinstance(descriptor.handler_name, str) or not descriptor.handler_name:
                raise RuntimeError(
                    f"workflow action presentation contract has an invalid handler binding for {descriptor.action}"
                )
            if not isinstance(descriptor.button_name, str) or not descriptor.button_name:
                raise RuntimeError(
                    f"workflow action presentation contract has an invalid button binding for {descriptor.action}"
                )
            try:
                handler = getattr(self, descriptor.handler_name)
                button = getattr(self, descriptor.button_name)
            except AttributeError as exc:
                raise RuntimeError(
                    f"workflow action presentation contract references missing binding for {descriptor.action}"
                ) from exc
            if not callable(handler):
                raise RuntimeError(
                    f"workflow action presentation contract handler is not callable for {descriptor.action}"
                )
            if button is not None and not callable(getattr(button, "configure", None)):
                raise RuntimeError(
                    f"workflow action presentation contract button is not configurable for {descriptor.action}"
                )
            contract.append(WorkflowActionBinding(descriptor.action, handler, button))
        return tuple(contract)

    def _invalidate_workflow_action_bindings(self) -> None:
        """Clear the cached workflow action registry and all derived maps atomically."""
        self._workflow_action_binding_registry = None
        self._workflow_action_button_map = None
        self._workflow_action_handler_map = None
        self._workflow_action_button_map_source = None
        self._workflow_action_handler_map_source = None

    @staticmethod
    def _immutable_workflow_action_map(values: Mapping[str, Any]) -> Mapping[str, Any]:
        """Construct an immutable workflow-action mapping without publishing it."""
        return MappingProxyType(values)

    def _workflow_action_bindings(self) -> Mapping[str, WorkflowActionBinding]:
        """Return the single immutable resolved action-binding registry.

        Resolution is cached for the lifetime of the presentation wiring so
        rendering and dispatch consume the same resolved contract rather than
        independently reconstructing live handler/button bindings. Cached
        registries are also checked for canonical key and binding coherence so
        a privately replaced or mutated cache cannot become the source for
        derived presentation maps.
        """
        if self._closed:
            return EMPTY_WORKFLOW_ACTION_MAP
        registry = self._workflow_action_binding_registry
        if registry is None or not self._workflow_action_registry_is_coherent(registry):
            self._invalidate_workflow_action_bindings()
            contract = self._workflow_action_contract()
            # Construct the complete immutable registry before publishing it.
            # If contract resolution or immutable-map construction fails, all
            # dependent cache fields remain cleared rather than exposing a
            # partially rebuilt presentation contract.
            rebuilt_registry = self._immutable_workflow_action_map(
                {binding.action: binding for binding in contract}
            )
            self._workflow_action_binding_registry = rebuilt_registry
            registry = rebuilt_registry
        return registry

    def _workflow_action_registry_is_coherent(
        self,
        registry: Mapping[str, WorkflowActionBinding],
    ) -> bool:
        """Return whether a cached registry matches its canonical live bindings."""
        # The live registry is intentionally an immutable mapping proxy. A
        # mutable mapping may contain a coherent snapshot at one instant but
        # can be changed behind the cache boundary afterwards, so it is not a
        # valid cached registry.
        if not isinstance(registry, MappingProxyType):
            return False
        try:
            if tuple(registry) != WORKFLOW_ACTIONS:
                return False
            for descriptor in WORKFLOW_ACTION_PRESENTATION:
                binding = registry.get(descriptor.action)
                if not isinstance(binding, WorkflowActionBinding) or binding.action != descriptor.action:
                    return False
                try:
                    handler = getattr(self, descriptor.handler_name)
                    button = getattr(self, descriptor.button_name)
                except AttributeError:
                    return False
                if binding.handler != handler or binding.button is not button:
                    return False
            return True
        except (KeyError, TypeError, ValueError, RuntimeError):
            return False

    def _workflow_action_derived_map_is_coherent(
        self,
        cached_map: Any,
        source: Mapping[str, WorkflowActionBinding] | None,
        registry: Mapping[str, WorkflowActionBinding],
        expected: Mapping[str, Any],
    ) -> bool:
        """Return whether a derived action map is still tied to its exact source registry."""
        if source is not registry or not isinstance(cached_map, Mapping):
            return False
        try:
            if tuple(cached_map) != WORKFLOW_ACTIONS:
                return False
            for action in WORKFLOW_ACTIONS:
                if cached_map[action] is not expected[action]:
                    return False
            return True
        except (KeyError, TypeError, ValueError, RuntimeError):
            return False

    def _workflow_action_buttons(self) -> Mapping[str, Any]:
        """Return the cached immutable button map derived from the binding registry."""
        if self._closed:
            return EMPTY_WORKFLOW_ACTION_MAP
        registry = self._workflow_action_bindings()
        expected = {action: binding.button for action, binding in registry.items()}
        if not self._workflow_action_derived_map_is_coherent(
            self._workflow_action_button_map,
            self._workflow_action_button_map_source,
            registry,
            expected,
        ):
            # The derived map is valid only for the exact registry from which
            # it was built and for the exact entries supplied by that registry.
            # The entry check also protects the cache boundary if a private
            # attribute is replaced independently of the source reference.
            # Build the immutable map locally before publishing either the
            # map or its source reference. A failed reconstruction therefore
            # cannot leave a half-updated derived-cache pair behind.
            self._workflow_action_button_map = None
            self._workflow_action_button_map_source = None
            rebuilt_map = self._immutable_workflow_action_map(expected)
            self._workflow_action_button_map = rebuilt_map
            self._workflow_action_button_map_source = registry
        return self._workflow_action_button_map

    def _refresh_action_states(self, pending: bool | None = None) -> None:
        """Render action availability from the immutable workflow-state contract."""
        if pending is None:
            pending = self.has_pending_changes
        validation_message = self._pending_validation_message()
        self._workflow_state = ScenarioProjectionGuiState.from_controls(
            pending_changes=pending,
            pending_valid=not bool(validation_message),
            dirty=self.is_dirty,
            closed=self._closed,
        )
        # Once terminal close has released the live binding cache, later
        # callbacks must not rehydrate stale presentation bindings. The
        # terminal refresh still disables already-created controls directly.
        if self._closed:
            for button_name in ("_run_button", "_save_button", "_reset_button", "_reload_button", "_reports_button", "_report_pack_button"):
                button = getattr(self, button_name, None)
                if button is not None and callable(getattr(button, "configure", None)):
                    button.configure(state="disabled")
            return
        bindings = self._workflow_action_bindings()
        for action, enabled in self._workflow_state.action_states:
            button = bindings[action].button
            if button is not None:
                button.configure(state="normal" if enabled else "disabled")
        if self._reports_button is not None and callable(getattr(self._reports_button, "configure", None)):
            report_enabled = bool(self.application is not None and self.results_are_current and not validation_message)
            self._reports_button.configure(state="normal" if report_enabled else "disabled")
        if self._report_pack_button is not None and callable(getattr(self._report_pack_button, "configure", None)):
            pack_enabled = bool(self.application is not None and self.results_are_current and not validation_message)
            self._report_pack_button.configure(state="normal" if pack_enabled else "disabled")

    def _on_input_change(self, *_: Any) -> None:
        """Refresh state after keyboard edits to any editable control."""
        if self._closed:
            return
        self._refresh_status()

    def _keyboard_binding_contract(self) -> tuple[tuple[str, str, Any], ...]:
        """Resolve and validate the canonical keyboard workflow contract."""
        resolved = []
        seen_pairs: set[tuple[str, str]] = set()
        covered_actions: set[str] = set()
        for entry in WORKFLOW_KEYBOARD_BINDINGS:
            if not isinstance(entry, tuple) or len(entry) != 3:
                raise RuntimeError("keyboard binding contract contains an invalid entry")
            event, action, handler_name = entry
            if not isinstance(event, str) or not event:
                raise RuntimeError("keyboard binding contract contains an invalid event")
            if action not in WORKFLOW_ACTIONS:
                raise RuntimeError(
                    f"keyboard binding action is outside canonical workflow actions: {action}"
                )
            pair = (event, action)
            if pair in seen_pairs:
                raise RuntimeError(
                    f"keyboard binding contract contains duplicate event/action pair: {event} / {action}"
                )
            seen_pairs.add(pair)
            handler = getattr(self, handler_name, None)
            if not callable(handler):
                raise RuntimeError(
                    f"keyboard binding handler is not callable: {handler_name}"
                )
            covered_actions.add(action)
            resolved.append((event, action, handler))
        if covered_actions != set(WORKFLOW_ACTIONS):
            missing = tuple(action for action in WORKFLOW_ACTIONS if action not in covered_actions)
            raise RuntimeError(
                f"keyboard binding contract is missing workflow actions: {missing}"
            )
        return tuple(resolved)

    def _bind_keyboard_shortcuts(self) -> None:
        """Provide small, predictable keyboard shortcuts for the desktop workflow."""
        if self._closed or self._root is None or self.application is None:
            return
        service = self._event_service or TkEventService(self._root)
        self._event_service = service
        # Tk's bind API can accumulate callbacks when the same binding is
        # registered repeatedly. Treat shortcut wiring as idempotent for the
        # exact event-service instance, while still allowing an injected/new
        # service to be wired independently (useful for headless adapters).
        if self._keyboard_shortcuts_bound_service is service:
            return
        for event, _action, handler in self._keyboard_binding_contract():
            service.bind(event, handler)
        self._keyboard_shortcuts_bound_service = service

    def _workflow_action_handlers(self) -> Mapping[str, Any]:
        """Return the cached immutable handler map derived from the binding registry.

        Tests may still inject an explicit handler into ``_dispatch_workflow_action``
        for isolated boundary testing.
        """
        if self._closed:
            return EMPTY_WORKFLOW_ACTION_MAP
        registry = self._workflow_action_bindings()
        expected = {action: binding.handler for action, binding in registry.items()}
        if not self._workflow_action_derived_map_is_coherent(
            self._workflow_action_handler_map,
            self._workflow_action_handler_map_source,
            registry,
            expected,
        ):
            # The derived map is valid only for the exact registry from which
            # it was built and for the exact entries supplied by that registry.
            # The entry check also protects the cache boundary if a private
            # attribute is replaced independently of the source reference.
            # Build the immutable map locally before publishing either the
            # map or its source reference. A failed reconstruction therefore
            # cannot leave a half-updated derived-cache pair behind.
            self._workflow_action_handler_map = None
            self._workflow_action_handler_map_source = None
            rebuilt_map = self._immutable_workflow_action_map(expected)
            self._workflow_action_handler_map = rebuilt_map
            self._workflow_action_handler_map_source = registry
        return self._workflow_action_handler_map

    def _dispatch_workflow_action(self, action: str, handler: Any | None = None) -> bool:
        """Gate and dispatch one presentation action, then resynchronise state."""
        if not isinstance(action, str) or action not in WORKFLOW_ACTIONS:
            raise ValueError(f"unknown workflow action: {action}")
        if handler is not None and not callable(handler):
            raise TypeError(f"workflow action handler is not callable: {action}")

        # Closed presentation instances are terminal. Short-circuit before
        # refreshing state so callbacks arriving after teardown cannot inspect
        # controls or execute any presentation work at all.
        if self._closed:
            return False

        self._refresh_status()
        if not self._workflow_state.action_enabled(action):
            return False
        if handler is None:
            handler = self._workflow_action_handlers()[action]
        try:
            handler()
        finally:
            # Keep the presentation state synchronised even if an injected
            # handler raises. Real handlers normally absorb expected domain/UI
            # failures themselves; this finally block also protects the
            # presentation boundary from stale controls when a test double or
            # unexpected integration failure escapes. The original exception
            # is deliberately preserved.
            self._refresh_status()
        return True

    def _run_from_button(self) -> bool:
        """Dispatch the Run button through the workflow-state boundary."""
        return self._dispatch_workflow_action("run")

    def _save_from_button(self) -> bool:
        """Dispatch the Save button through the workflow-state boundary."""
        return self._dispatch_workflow_action("save")

    def _reset_from_button(self) -> bool:
        """Dispatch the Reset button through the workflow-state boundary."""
        return self._dispatch_workflow_action("reset")

    def _reload_from_button(self) -> bool:
        """Dispatch the Reload button through the workflow-state boundary."""
        return self._dispatch_workflow_action("reload")

    def _run_from_event(self, _event: Any | None = None) -> bool:
        """Dispatch keyboard Run through the workflow-state boundary."""
        return self._dispatch_workflow_action("run")

    def _save_from_event(self, _event: Any | None = None) -> bool:
        """Dispatch keyboard Save through the workflow-state boundary."""
        return self._dispatch_workflow_action("save")

    def _reset_from_event(self, _event: Any | None = None) -> bool:
        """Dispatch keyboard Reset through the workflow-state boundary."""
        return self._dispatch_workflow_action("reset")

    def _reload_from_event(self, _event: Any | None = None) -> bool:
        """Dispatch keyboard Reload through the workflow-state boundary."""
        return self._dispatch_workflow_action("reload")

    def _open_assumptions_editor(self) -> None:
        """Open a flexible editor for the complete assumptions.json document."""
        if self.application is None or self._closed:
            return
        import tkinter as tk
        from tkinter import ttk

        if self._assumptions_editor is not None:
            try:
                if self._assumptions_editor.winfo_exists():
                    self._assumptions_editor.deiconify()
                    self._assumptions_editor.lift()
                    return
            except Exception:
                pass

        editor = tk.Toplevel(self._root) if self._root is not None else tk.Toplevel()
        editor.title("Edit all assumptions")
        editor.geometry("820x680")
        editor.minsize(650, 500)
        def close_editor() -> None:
            """Close the editor without silently losing un-applied text edits."""
            try:
                pending = self.controller.assumptions_text_has_unapplied_changes(
                    text.get("1.0", "end-1c")
                )
            except (TypeError, ValueError):
                pending = True
            if not pending:
                editor.destroy()
                return
            messagebox = self._dialog or __import__(
                "tkinter.messagebox", fromlist=["messagebox"]
            )
            discard = messagebox.askyesno(
                "Discard assumptions edits?",
                "There are unapplied assumptions edits. Close without applying them?",
                parent=editor,
            )
            if discard:
                editor.destroy()

        editor.protocol("WM_DELETE_WINDOW", close_editor)

        frame = ttk.Frame(editor, padding=10)
        frame.pack(fill="both", expand=True)
        ttk.Label(
            frame,
            text="Edit the complete assumptions.json document. Apply validates the entire document in memory; Save writes it to disk.",
            wraplength=760,
        ).pack(fill="x", pady=(0, 8))

        text = tk.Text(frame, wrap="none", undo=True)
        text.pack(fill="both", expand=True)
        text.insert("1.0", self.controller.assumptions_json())
        text.edit_modified(False)

        status = tk.StringVar(value="Ready")
        ttk.Label(frame, textvariable=status, wraplength=760).pack(fill="x", pady=(8, 4))

        changes_var = tk.StringVar()
        ttk.Label(frame, textvariable=changes_var, wraplength=760, takefocus=True).pack(fill="x", pady=(0, 8))

        def refresh_changes() -> None:
            current_text = text.get("1.0", "end-1c")
            changes = self.controller.assumptions_changes()
            summary = self.controller.assumptions_editor_status(current_text)
            if changes:
                preview = ", ".join(changes[:6])
                suffix = " …" if len(changes) > 6 else ""
                changes_var.set(f"{summary} Changes: {preview}{suffix}")
            else:
                changes_var.set(summary)

        def on_text_modified(_event: Any | None = None) -> None:
            if text.edit_modified():
                refresh_changes()
                text.edit_modified(False)

        text.bind("<<Modified>>", on_text_modified, add="+")
        text.edit_modified(False)
        refresh_changes()

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x")

        def validate_document() -> None:
            try:
                self.controller.validate_assumptions_json(text.get("1.0", "end-1c"))
                status.set("Valid assumptions document. No changes applied.")
            except (ValueError, TypeError) as exc:
                status.set(f"Invalid assumptions: {exc}")

        def format_document() -> None:
            try:
                formatted = self.controller.format_assumptions_json(text.get("1.0", "end-1c"))
                text.delete("1.0", "end")
                text.insert("1.0", formatted)
                text.edit_modified(False)
                refresh_changes()
                status.set("Formatted and validated assumptions document; no changes applied.")
            except (ValueError, TypeError) as exc:
                status.set(f"Cannot format: {exc}")

        def apply_only() -> None:
            try:
                self.controller.apply_assumptions_json(text.get("1.0", "end-1c"))
                inputs = self.application.inputs()
                self._set_input_controls(inputs, self.selected_scenarios)
                self._refresh_status()
                refresh_changes()
                status.set("Applied and validated in memory. Use Save assumptions to persist the changes.")
            except (ValueError, TypeError) as exc:
                status.set(f"Not applied: {exc}")

        def apply_and_save() -> None:
            apply_only()
            if status.get().startswith("Applied and validated"):
                try:
                    self.controller.save()
                    self._refresh_status()
                    refresh_changes()
                    status.set("Applied, validated and saved to assumptions.json.")
                except (ValueError, OSError, TypeError) as exc:
                    status.set(f"Applied in memory, but not saved: {exc}")

        ttk.Button(buttons, text="Validate", command=validate_document).pack(side="left", padx=(0, 6))
        ttk.Button(buttons, text="Format", command=format_document).pack(side="left", padx=(0, 6))
        ttk.Button(buttons, text="Apply", command=apply_only).pack(side="left", padx=(0, 6))
        ttk.Button(buttons, text="Apply & Save", command=apply_and_save).pack(side="left", padx=(0, 6))
        def reload_document() -> None:
            text.delete("1.0", "end")
            text.insert("1.0", self.controller.assumptions_json())
            text.edit_modified(False)
            refresh_changes()
            status.set("Reloaded current in-memory assumptions.")

        def discard_changes() -> None:
            try:
                self.controller.discard_assumptions_changes()
                text.delete("1.0", "end")
                text.insert("1.0", self.controller.assumptions_json())
                text.edit_modified(False)
                self._set_input_controls(self.application.inputs(), self.selected_scenarios)
                self._refresh_status()
                refresh_changes()
                status.set("Discarded in-memory changes and restored the saved baseline.")
            except (ValueError, TypeError) as exc:
                status.set(f"Could not discard changes: {exc}")

        ttk.Button(buttons, text="Reload document", command=reload_document).pack(side="left")
        ttk.Button(buttons, text="Discard changes", command=discard_changes).pack(side="left", padx=(6, 0))
        ttk.Button(buttons, text="Close", command=close_editor).pack(side="right")

        self._assumptions_editor = editor
        self._assumptions_text = text

    def _run_projection(self) -> None:
        """Validate inputs, apply them in memory, rebuild the view model and refresh."""
        messagebox = self._dialog or __import__("tkinter.messagebox", fromlist=["messagebox"])

        if self.application is None or self._closed:
            return
        try:
            result = self.controller.run(*self._current_input_strings())
            self.view_model = result.view_model
            self._last_result_snapshot = result.workflow_result.snapshot
            self._last_workflow_result = result.workflow_result
            self._last_workflow_result = result.workflow_result
            self._last_projection_signature = (
                result.inputs,
                json.dumps(self.application.assumptions.data, sort_keys=True, ensure_ascii=False, allow_nan=False),
            )
            self._refresh_results()
            self._workflow_state = self._workflow_state.after_run(dirty=self.is_dirty)
            self._refresh_status()
        except (ValueError, TypeError) as exc:
            self._refresh_status()
            self._focus_validation_target()
            messagebox.showerror("Invalid projection inputs", str(exc), parent=self._root)


    def _export_pdf_reports(self) -> bool:
        """Export the complete professional PDF report suite from current GUI state."""
        messagebox = self._dialog or __import__("tkinter.messagebox", fromlist=["messagebox"])
        file_dialog = self._file_dialog or __import__("tkinter.filedialog", fromlist=["filedialog"])

        if self._closed or self.application is None:
            return False
        try:
            workflow_result = self._current_workflow_result()
        except (RuntimeError, ValueError, TypeError) as exc:
            messagebox.showerror("Reports unavailable", str(exc), parent=self._root)
            return False

        directory = file_dialog.askdirectory(
            title="Choose folder for Retirement Planner PDF reports",
            parent=self._root,
        )
        if not directory:
            return False

        from planner.reporting import export_report_suite

        exporter = self._report_suite_exporter or export_report_suite
        try:
            result = exporter(
                assumptions=self.application.assumptions,
                scenario_result=workflow_result,
                allocations=self.allocations,
                fund_returns=self.fund_returns,
                directory=directory,
            )
        except (ValueError, OSError, TypeError) as exc:
            messagebox.showerror("Could not export PDF reports", str(exc), parent=self._root)
            return False

        paths = getattr(result, "paths", result)
        message = "PDF reports exported to:\n" + "\n".join(str(path) for path in paths.values())
        messagebox.showinfo("PDF reports exported", message, parent=self._root)
        return True

    def _export_pdf_report_pack(self) -> bool:
        """Export the complete professional PDF report suite and consolidated pack."""
        messagebox = self._dialog or __import__("tkinter.messagebox", fromlist=["messagebox"])
        file_dialog = self._file_dialog or __import__("tkinter.filedialog", fromlist=["filedialog"])

        if self._closed or self.application is None:
            return False
        try:
            workflow_result = self._current_workflow_result()
        except (RuntimeError, ValueError, TypeError) as exc:
            messagebox.showerror("Reports unavailable", str(exc), parent=self._root)
            return False

        directory = file_dialog.askdirectory(
            title="Choose folder for Retirement Planner PDF report pack",
            parent=self._root,
        )
        if not directory:
            return False

        pack_path = Path(directory) / "RetirementPlanner_Report_Pack.pdf"
        if pack_path.exists():
            messagebox.showerror(
                "Could not export PDF report pack",
                f"Report pack already exists: {pack_path}",
                parent=self._root,
            )
            return False

        from planner.reporting import export_report_pack, export_report_suite

        suite_exporter = self._report_suite_exporter or export_report_suite
        pack_exporter = self._report_pack_exporter or export_report_pack
        try:
            suite_result = suite_exporter(
                assumptions=self.application.assumptions,
                scenario_result=workflow_result,
                allocations=self.allocations,
                fund_returns=self.fund_returns,
                directory=directory,
            )
            pack_result = pack_exporter(suite_result, pack_path)
        except (ValueError, FileExistsError, OSError, TypeError) as exc:
            messagebox.showerror("Could not export PDF report pack", str(exc), parent=self._root)
            return False

        suite_paths = getattr(suite_result, "paths", suite_result)
        generated = list(suite_paths.values()) if hasattr(suite_paths, "values") else list(suite_paths)
        generated.append(getattr(pack_result, "path", pack_result))
        message = "PDF report pack exported:\n" + "\n".join(str(path) for path in generated)
        messagebox.showinfo("PDF report pack exported", message, parent=self._root)
        return True

    def _save_assumptions(self) -> None:
        """Persist the current validated assumptions only after an explicit click."""
        messagebox = self._dialog or __import__("tkinter.messagebox", fromlist=["messagebox"])

        if self.application is None or self._closed:
            return
        try:
            self.controller.save()
        except (ValueError, OSError) as exc:
            messagebox.showerror("Could not save assumptions", str(exc), parent=self._root)
            return
        self._workflow_state = self._workflow_state.after_save()
        self._refresh_status()
        messagebox.showinfo("Assumptions saved", "Validated assumptions were saved.", parent=self._root)

    def _reset_inputs(self) -> None:
        """Restore controls and immediately resynchronise the workflow presentation state."""
        if self.application is None or self._closed:
            return
        self._set_input_controls(self.application.inputs(), self.selected_scenarios)
        self._workflow_state = self._workflow_state.after_reset()
        # Setting Tk variables may be suppressed or delayed by a headless/test
        # adapter, so explicitly refresh the derived state rather than relying
        # on variable-trace callbacks to update status and action controls.
        self._refresh_status()

    def _reload_saved_assumptions(self) -> None:
        """Reload the on-disk assumptions and refresh the projection view."""
        messagebox = self._dialog or __import__("tkinter.messagebox", fromlist=["messagebox"])

        if self.application is None or self._closed:
            return
        try:
            inputs = self.controller.reload_saved()
            result = self.controller.run(
                str(inputs.starting_pension),
                str(inputs.retirement_age),
                str(inputs.projection_end_age),
                inputs.scenarios,
            )
            self.view_model = result.view_model
            self._last_result_snapshot = result.workflow_result.snapshot
            self._last_projection_signature = (
                result.inputs,
                json.dumps(self.application.assumptions.data, sort_keys=True, ensure_ascii=False, allow_nan=False),
            )
            self._set_input_controls(result.inputs, result.inputs.scenarios)
            self._refresh_results()
            self._workflow_state = self._workflow_state.after_reload()
            self._refresh_status()
        except (ValueError, OSError, TypeError) as exc:
            messagebox.showerror("Could not reload assumptions", str(exc), parent=self._root)

    def build(self) -> Any:
        """Build and return the Tk root without entering the event loop.

        Building is idempotent so accidental refresh/rebuild calls cannot
        create duplicate control trees or duplicate keyboard bindings.
        """
        if self._closed:
            raise RuntimeError("cannot build a closed ScenarioProjectionWindow")
        if self._built and self._root is not None:
            return self._root
        import tkinter as tk
        from tkinter import ttk

        if self._root is None:
            self._root = tk.Tk()
        if self._event_service is None:
            self._event_service = TkEventService(self._root)
        self._root.title("Retirement Scenario Comparison")
        if hasattr(self._root, "protocol"):
            self._root.protocol("WM_DELETE_WINDOW", self.close)
        self._root.geometry("1080x780")
        self._root.minsize(900, 650)

        container = ttk.Frame(self._root, padding=16)
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container)
        header.pack(fill="x", pady=(0, 12))
        ttk.Label(
            header,
            text="Retirement scenario comparison",
            font=("TkDefaultFont", 16, "bold"),
        ).pack(side="left")
        if self.application is not None:
            self._status_var = tk.StringVar()
            ttk.Label(header, textvariable=self._status_var).pack(side="right")

        if self.application is not None:
            self._build_input_controls(container, ttk)

        self._content = ttk.Frame(container)
        self._content.pack(fill="both", expand=True)
        self._render_results(ttk)
        self._bind_keyboard_shortcuts()
        self._refresh_status()
        if self.application is not None and self._pension_var is not None:
            self._event_service.after_idle(lambda: self._focus_pension_entry())
        self._built = True
        return self._root

    def close(self) -> None:
        """Close the window safely and make subsequent UI callbacks no-ops."""
        if self._closed:
            return
        self._closed = True
        self._workflow_state = self._workflow_state.after_close()
        # A closed presentation must not retain the last published result
        # snapshot. Export consumers must re-establish a live presentation
        # context rather than reading data retained by a terminal instance.
        self._last_result_snapshot = None
        self._last_workflow_result = None
        # Closing is a terminal workflow transition. Refresh the presentation
        # state as well so any already-built/headless controls cannot retain
        # stale enabled actions or a pre-close status message.
        self._refresh_status()
        # Closing is terminal, so release the cached live presentation bindings
        # after the final state refresh. Subsequent callbacks cannot retain
        # references to widgets or handlers from the closed presentation.
        self._invalidate_workflow_action_bindings()
        if self._assumptions_editor is not None:
            try:
                if self._assumptions_editor.winfo_exists():
                    self._assumptions_editor.destroy()
            except Exception:
                pass
        self._assumptions_editor = None
        self._assumptions_text = None
        root = self._root
        if root is not None and hasattr(root, "destroy"):
            root.destroy()

    def _build_input_controls(self, container: Any, ttk: Any) -> None:
        import tkinter as tk

        inputs = self.application.inputs()
        controls = ttk.LabelFrame(container, text="Projection inputs", padding=10)
        controls.pack(fill="x", pady=(0, 12))
        controls.columnconfigure(0, weight=1)
        controls.columnconfigure(1, weight=0)
        controls.columnconfigure(2, weight=0)

        self._pension_var = tk.StringVar(value=f"{inputs.starting_pension:,.0f}")
        self._retirement_age_var = tk.StringVar(value=str(inputs.retirement_age))
        self._end_age_var = tk.StringVar(value=str(inputs.projection_end_age))
        for variable in (self._pension_var, self._retirement_age_var, self._end_age_var):
            variable.trace_add("write", self._on_input_change)

        fields = (
            ("Starting pension (£)", self._pension_var),
            ("Retirement age", self._retirement_age_var),
            ("Projection end age", self._end_age_var),
        )
        self._entry_widgets = []
        for column, (label, variable) in enumerate(fields):
            ttk.Label(controls, text=label).grid(row=0, column=column, padx=5, sticky="w")
            entry = ttk.Entry(controls, textvariable=variable, width=18, takefocus=True)
            entry.grid(row=1, column=column, padx=5, sticky="ew")
            self._entry_widgets.append(entry)

        scenario_frame = ttk.Frame(controls)
        scenario_frame.grid(row=2, column=0, columnspan=3, sticky="w", pady=(8, 0))
        ttk.Label(scenario_frame, text="Scenarios:").pack(side="left", padx=(0, 8))
        self._scenario_vars = {}
        for name in SUPPORTED_SCENARIOS:
            variable = tk.BooleanVar(value=name in inputs.scenarios)
            self._scenario_vars[name] = variable
            checkbutton = ttk.Checkbutton(
                scenario_frame, text=name.title(), variable=variable,
                command=self._refresh_status, takefocus=True,
            )
            checkbutton.pack(side="left", padx=4)
            self._scenario_checkbuttons[name] = checkbutton

        self._selection_var = tk.StringVar()
        ttk.Label(controls, textvariable=self._selection_var).grid(
            row=3, column=0, columnspan=3, sticky="w", padx=5, pady=(6, 0)
        )
        self._validation_var = tk.StringVar()
        self._validation_label = ttk.Label(controls, textvariable=self._validation_var, wraplength=760, takefocus=True)
        self._validation_label.grid(
            row=4, column=0, columnspan=3, sticky="w", padx=5, pady=(4, 0)
        )

        self._results_status_var = tk.StringVar()
        ttk.Label(controls, textvariable=self._results_status_var, wraplength=760, takefocus=True).grid(
            row=5, column=0, columnspan=3, sticky="w", padx=5, pady=(4, 0)
        )

        advanced = ttk.Frame(controls)
        advanced.grid(row=6, column=0, columnspan=3, sticky="w", pady=(10, 0))
        ttk.Button(advanced, text="Edit all assumptions…", command=self._open_assumptions_editor, takefocus=True).pack(side="left")
        self._reports_button = ttk.Button(advanced, text="Export PDF reports…", command=self._export_pdf_reports, takefocus=True)
        self._reports_button.pack(side="left", padx=(8, 0))
        self._report_pack_button = ttk.Button(advanced, text="Export PDF report pack…", command=self._export_pdf_report_pack, takefocus=True)
        self._report_pack_button.pack(side="left", padx=(8, 0))

        buttons = ttk.Frame(controls)
        buttons.grid(row=7, column=0, columnspan=3, sticky="w", pady=(8, 0))
        self._run_button = ttk.Button(buttons, text="Run projection", command=self._run_from_button, takefocus=True)
        self._run_button.pack(side="left", padx=(0, 6))
        self._save_button = ttk.Button(buttons, text="Save assumptions", command=self._save_from_button, takefocus=True)
        self._save_button.pack(side="left", padx=(0, 6))
        self._reset_button = ttk.Button(buttons, text="Reset inputs", command=self._reset_from_button, takefocus=True)
        self._reset_button.pack(side="left", padx=(0, 6))
        self._reload_button = ttk.Button(buttons, text="Reload saved", command=self._reload_from_button, takefocus=True)
        self._invalidate_workflow_action_bindings()
        self._reload_button.pack(side="left")

    def _focus_validation_target(self) -> None:
        """Move keyboard focus to the first control that needs attention."""
        if self._pension_var is None:
            return
        pension, retirement, end_age, scenarios = self._current_input_strings()
        try:
            self.parse_inputs(pension, retirement, end_age, scenarios)
        except (ValueError, TypeError):
            pension_text = str(pension).replace(",", "").replace("£", "").strip()
            try:
                pension_value = float(pension_text)
            except (ValueError, TypeError):
                if self._entry_widgets:
                    self._entry_widgets[0].focus_set()
                elif self._validation_label is not None:
                    self._validation_label.focus_set()
                return
            if not isfinite(pension_value):
                if self._entry_widgets:
                    self._entry_widgets[0].focus_set()
                elif self._validation_label is not None:
                    self._validation_label.focus_set()
                return
            try:
                retirement_value = int(str(retirement).strip())
            except (ValueError, TypeError):
                if len(self._entry_widgets) > 1:
                    self._entry_widgets[1].focus_set()
                elif self._validation_label is not None:
                    self._validation_label.focus_set()
                return
            try:
                end_value = int(str(end_age).strip())
            except (ValueError, TypeError):
                if len(self._entry_widgets) > 2:
                    self._entry_widgets[2].focus_set()
                elif self._validation_label is not None:
                    self._validation_label.focus_set()
                return
            if end_value < retirement_value:
                if len(self._entry_widgets) > 2:
                    self._entry_widgets[2].focus_set()
                elif self._validation_label is not None:
                    self._validation_label.focus_set()
                return
            if not scenarios:
                for name in SUPPORTED_SCENARIOS:
                    if name in self._scenario_checkbuttons:
                        self._scenario_checkbuttons[name].focus_set()
                        return
                if self._validation_label is not None:
                    self._validation_label.focus_set()
                return
            if self._validation_label is not None:
                self._validation_label.focus_set()

    def _focus_pension_entry(self) -> None:
        """Focus the primary editable field when the window first becomes interactive."""
        entries = getattr(self, "_entry_widgets", ())
        if entries and not self._closed:
            entries[0].focus_set()
            entries[0].selection_range(0, "end")

    def _render_results(self, ttk: Any) -> None:
        for child in self._content.winfo_children():
            child.destroy()
        self._cards_frame = None
        self._table = None
        self._chart_canvas = None
        self._chart_accessibility_var = None
        self._chart_focus_index = 0

        self._cards_frame = ttk.Frame(self._content)
        self._cards_frame.pack(fill="x", pady=(0, 16))
        for card in self.view_model.scenario_cards:
            card_frame = ttk.LabelFrame(self._cards_frame, text=card.name, padding=10)
            card_frame.pack(side="left", fill="both", expand=True, padx=4)
            ttk.Label(card_frame, text=f"Return: {format_percent(card.annual_return)}").pack(anchor="w")
            ttk.Label(card_frame, text=f"Ending pension: {format_currency(card.ending_balance)}").pack(anchor="w")
            ttk.Label(card_frame, text=f"Investment growth: {format_currency(card.total_investment_growth)}").pack(anchor="w")
            ttk.Label(card_frame, text=f"Withdrawals: {format_currency(card.total_withdrawals)}").pack(anchor="w")
            ttk.Label(card_frame, text=f"Source: {card.source}").pack(anchor="w")

        summary = ttk.Frame(self._content)
        summary.pack(fill="x", pady=(0, 12))
        ttk.Label(summary, text=f"Lowest: {format_currency(self.view_model.lowest_ending_balance)}").pack(side="left", padx=4)
        ttk.Label(summary, text=f"Highest: {format_currency(self.view_model.highest_ending_balance)}").pack(side="left", padx=12)
        ttk.Label(summary, text=f"Spread: {format_currency(self.view_model.ending_balance_spread)}").pack(side="left", padx=12)
        ttk.Label(summary, text=f"Scenarios: {len(self.view_model.scenario_cards)}").pack(side="right", padx=4)

        self._render_ending_balance_chart(ttk)

        table_frame = ttk.Frame(self._content)
        table_frame.pack(fill="both", expand=True)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        columns = ("scenario", "year", "starting", "growth", "withdrawals", "ending")
        self._table = ttk.Treeview(table_frame, columns=columns, show="headings", height=18)
        headings = {
            "scenario": "Scenario",
            "year": "Year",
            "starting": "Starting pension",
            "growth": "Investment growth",
            "withdrawals": "Withdrawals",
            "ending": "Ending pension",
        }
        widths = {"scenario": 130, "year": 65, "starting": 140, "growth": 140, "withdrawals": 120, "ending": 140}
        for column in columns:
            self._table.heading(column, text=headings[column])
            self._table.column(
                column,
                width=widths[column],
                minwidth=65 if column == "year" else 100,
                stretch=column in {"scenario", "ending"},
                anchor="e" if column not in {"scenario", "year"} else "w",
            )
        for row in self.view_model.year_rows:
            self._table.insert(
                "",
                "end",
                values=(
                    row.scenario,
                    row.year,
                    format_currency(row.starting_balance),
                    format_currency(row.investment_growth),
                    format_currency(row.withdrawals),
                    format_currency(row.ending_balance),
                ),
            )
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self._table.yview)
        horizontal = ttk.Scrollbar(table_frame, orient="horizontal", command=self._table.xview)
        self._table.configure(yscrollcommand=scrollbar.set, xscrollcommand=horizontal.set)
        self._table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")

    def _render_ending_balance_chart(self, ttk: Any) -> None:
        """Render a compact, calculation-free ending-balance comparison chart."""
        import tkinter as tk

        chart_frame = ttk.LabelFrame(
            self._content,
            text="Ending pension comparison",
            padding=8,
        )
        chart_frame.pack(fill="x", pady=(0, 12))
        chart_frame.columnconfigure(0, weight=1)

        series = self.view_model.ending_balance_series()
        self._chart_canvas = tk.Canvas(
            chart_frame,
            height=180,
            highlightthickness=0,
            takefocus=True,
        )
        self._chart_canvas.grid(row=0, column=0, sticky="ew")
        self._chart_canvas.bind("<Configure>", self._draw_ending_balance_chart)
        self._chart_canvas.bind("<Motion>", self._on_chart_motion)
        self._chart_canvas.bind("<FocusIn>", self._on_chart_focus)
        self._chart_canvas.bind("<Key>", self._on_chart_key)
        self._chart_canvas._scenario_series = series
        self._chart_focus_index = 0
        self._chart_accessibility_var = tk.StringVar()
        ttk.Label(
            chart_frame,
            textvariable=self._chart_accessibility_var,
            wraplength=760,
            takefocus=True,
        ).grid(row=1, column=0, sticky="w", pady=(6, 0))
        self._draw_ending_balance_chart()
        self._refresh_chart_accessibility()

    def _refresh_chart_accessibility(self, index: int | None = None) -> None:
        """Expose chart data as keyboard-readable text without recalculation."""
        canvas = self._chart_canvas
        if canvas is None:
            return
        series = tuple(getattr(canvas, "_scenario_series", ()))
        if not series:
            self._chart_focus_index = 0
            if self._chart_accessibility_var is not None:
                self._chart_accessibility_var.set("Chart: no scenarios selected.")
            return
        if index is not None:
            self._chart_focus_index = max(0, min(index, len(series) - 1))
        name, value = series[self._chart_focus_index]
        summary = ", ".join(f"{scenario.title()} {format_currency(amount)}" for scenario, amount in series)
        if self._chart_accessibility_var is not None:
            self._chart_accessibility_var.set(
                f"Chart focus: {name.title()}, ending pension {format_currency(value)}. "
                f"Scenarios: {summary}. Use Left/Right arrows to move between scenarios."
            )

    def _on_chart_focus(self, _event: Any | None = None) -> None:
        self._refresh_chart_accessibility()
        self._draw_ending_balance_chart()

    def _on_chart_key(self, event: Any) -> str | None:
        """Navigate scenario bars from the keyboard when the chart has focus."""
        canvas = self._chart_canvas
        if canvas is None:
            return None
        series = tuple(getattr(canvas, "_scenario_series", ()))
        if not series:
            return None
        key = getattr(event, "keysym", "")
        if key in ("Left", "Up", "Home"):
            index = 0 if key == "Home" else self._chart_focus_index - 1
        elif key in ("Right", "Down", "End"):
            index = len(series) - 1 if key == "End" else self._chart_focus_index + 1
        else:
            return None
        self._refresh_chart_accessibility(index)
        self._draw_ending_balance_chart()
        return "break"

    def _on_chart_motion(self, event: Any) -> None:
        """Expose the bar under the pointer as accessible text."""
        canvas = self._chart_canvas
        if canvas is None:
            return
        series = tuple(getattr(canvas, "_scenario_series", ()))
        if not series:
            return
        width = max(canvas.winfo_width(), 420)
        height = max(canvas.winfo_height(), 180)
        margin_left, margin_right, margin_top, margin_bottom = 120, 24, 18, 34
        plot_width = max(width - margin_left - margin_right, 1)
        plot_height = max(height - margin_top - margin_bottom, 1)
        maximum = max(value for _, value in series)
        maximum = maximum if maximum > 0 else 1.0
        bar_gap = 10
        bar_height = max((plot_height - bar_gap * (len(series) - 1)) / len(series), 18)
        if not (margin_left <= event.x <= width - margin_right):
            return
        for index, (name, value) in enumerate(series):
            y = margin_top + index * (bar_height + bar_gap)
            bar_width = max(value / maximum * plot_width, 0)
            if y <= event.y <= y + bar_height and margin_left <= event.x <= margin_left + bar_width:
                self._refresh_chart_accessibility(index)
                return

    def _draw_ending_balance_chart(self, _event: Any | None = None) -> None:
        """Draw scenario bars from immutable view-model values only."""
        canvas = self._chart_canvas
        if canvas is None:
            return
        series = tuple(getattr(canvas, "_scenario_series", ()))
        canvas.delete("all")
        if not series:
            canvas.create_text(12, 30, anchor="w", text="No scenarios selected.")
            self._refresh_chart_accessibility()
            return

        width = max(canvas.winfo_width(), 420)
        height = max(canvas.winfo_height(), 180)
        margin_left, margin_right, margin_top, margin_bottom = 120, 24, 18, 34
        plot_width = max(width - margin_left - margin_right, 1)
        plot_height = max(height - margin_top - margin_bottom, 1)
        maximum = max(value for _, value in series)
        maximum = maximum if maximum > 0 else 1.0
        bar_gap = 10
        bar_height = max((plot_height - bar_gap * (len(series) - 1)) / len(series), 18)

        for index, (name, value) in enumerate(series):
            y = margin_top + index * (bar_height + bar_gap)
            bar_width = max(value / maximum * plot_width, 0)
            canvas.create_text(
                margin_left - 10, y + bar_height / 2,
                anchor="e", text=name.title(),
            )
            canvas.create_rectangle(
                margin_left, y, margin_left + bar_width, y + bar_height,
                outline="" if index != self._chart_focus_index else "black",
                width=2 if index == self._chart_focus_index else 1,
            )
            canvas.create_text(
                min(margin_left + bar_width + 8, width - 8),
                y + bar_height / 2,
                anchor="w" if margin_left + bar_width + 8 < width - 8 else "e",
                text=format_currency(value),
            )

        canvas.create_line(
            margin_left, height - margin_bottom,
            width - margin_right, height - margin_bottom,
        )
        canvas.create_text(
            margin_left, height - 10, anchor="w", text="£0"
        )
        canvas.create_text(
            width - margin_right, height - 10, anchor="e",
            text=format_currency(maximum),
        )

    def _refresh_results(self) -> None:
        import tkinter.ttk as ttk

        if self._closed:
            return
        if self._content is not None:
            self._render_results(ttk)

    def run(self) -> None:
        """Build the window and, when owned, enter the Tk event loop."""
        root = self.build()
        if self._owns_root:
            root.mainloop()
