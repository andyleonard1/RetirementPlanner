"""Pure workflow state model for the scenario projection desktop GUI."""
from __future__ import annotations

from dataclasses import dataclass, replace


WORKFLOW_ACTIONS = ("run", "save", "reset", "reload")


@dataclass(frozen=True)
class ScenarioProjectionGuiState:
    """Immutable presentation state for Run/Save/Reset/Reload actions.

    The model contains no Tk dependencies and no financial logic.  It records
    the relationship between the last applied state, pending edits and the
    persistence baseline so the desktop adapter can render the same rules
    consistently and headless tests can exercise the workflow directly.
    """

    pending_changes: bool = False
    pending_valid: bool = True
    dirty: bool = False
    closed: bool = False

    @property
    def run_enabled(self) -> bool:
        return not self.closed and self.pending_changes and self.pending_valid

    @property
    def save_enabled(self) -> bool:
        return not self.closed and self.dirty and not self.pending_changes

    @property
    def reset_enabled(self) -> bool:
        return not self.closed and self.pending_changes

    @property
    def reload_enabled(self) -> bool:
        return not self.closed

    @property
    def available_actions(self) -> tuple[str, ...]:
        """Return the canonical workflow action vocabulary in stable order."""
        return WORKFLOW_ACTIONS

    @property
    def action_states(self) -> tuple[tuple[str, bool], ...]:
        """Return the canonical action/permission snapshot in stable order."""
        return tuple(
            zip(
                WORKFLOW_ACTIONS,
                (
                    self.run_enabled,
                    self.save_enabled,
                    self.reset_enabled,
                    self.reload_enabled,
                ),
            )
        )

    def action_enabled(self, action: str) -> bool:
        """Return whether a named workflow action is currently permitted."""
        if action not in WORKFLOW_ACTIONS:
            raise ValueError(f"unknown workflow action: {action}")
        return dict(self.action_states)[action]

    @property
    def status(self) -> str:
        if self.closed:
            return "Closed"
        if self.pending_changes:
            return "Changes ready to run" if self.pending_valid else "Input needs attention"
        if self.dirty:
            return "Unsaved changes"
        return "Saved assumptions"

    @classmethod
    def from_controls(
        cls,
        *,
        pending_changes: bool,
        pending_valid: bool,
        dirty: bool,
        closed: bool = False,
    ) -> "ScenarioProjectionGuiState":
        """Create state from the observable GUI/application conditions."""
        return cls(
            pending_changes=bool(pending_changes),
            pending_valid=bool(pending_valid),
            dirty=bool(dirty),
            closed=bool(closed),
        )

    def edited(self, *, valid: bool) -> "ScenarioProjectionGuiState":
        """Represent an editable-control change awaiting Run."""
        if self.closed:
            return self
        return replace(self, pending_changes=True, pending_valid=bool(valid))

    def after_run(self, *, dirty: bool) -> "ScenarioProjectionGuiState":
        """Represent a successful Run that makes controls the applied state."""
        if self.closed:
            return self
        return replace(self, pending_changes=False, pending_valid=True, dirty=bool(dirty))

    def after_save(self) -> "ScenarioProjectionGuiState":
        """Represent a successful explicit Save."""
        if self.closed:
            return self
        return replace(self, pending_changes=False, pending_valid=True, dirty=False)

    def after_reset(self) -> "ScenarioProjectionGuiState":
        """Represent Reset restoring controls to the applied state."""
        if self.closed:
            return self
        return replace(self, pending_changes=False, pending_valid=True)

    def after_reload(self) -> "ScenarioProjectionGuiState":
        """Represent Reload restoring the saved on-disk baseline."""
        if self.closed:
            return self
        return replace(self, pending_changes=False, pending_valid=True, dirty=False)

    def after_close(self) -> "ScenarioProjectionGuiState":
        """Represent terminal window closure."""
        return replace(self, closed=True, pending_changes=False, pending_valid=False)
