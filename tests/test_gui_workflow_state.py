import unittest

from planner.gui.workflow_state import WORKFLOW_ACTIONS, ScenarioProjectionGuiState


class ScenarioProjectionGuiStateTests(unittest.TestCase):
    def test_saved_state_disables_run_and_save(self):
        state = ScenarioProjectionGuiState()
        self.assertFalse(state.run_enabled)
        self.assertFalse(state.save_enabled)
        self.assertFalse(state.reset_enabled)
        self.assertTrue(state.reload_enabled)
        self.assertEqual(state.status, "Saved assumptions")

    def test_valid_pending_edit_enables_only_run(self):
        state = ScenarioProjectionGuiState().edited(valid=True)
        self.assertTrue(state.run_enabled)
        self.assertFalse(state.save_enabled)
        self.assertTrue(state.reset_enabled)
        self.assertEqual(state.status, "Changes ready to run")

    def test_invalid_pending_edit_reports_attention_required(self):
        state = ScenarioProjectionGuiState().edited(valid=False)
        self.assertFalse(state.run_enabled)
        self.assertFalse(state.save_enabled)
        self.assertTrue(state.reset_enabled)
        self.assertEqual(state.status, "Input needs attention")

    def test_successful_run_clears_pending_and_preserves_dirty_baseline(self):
        state = ScenarioProjectionGuiState().edited(valid=True).after_run(dirty=True)
        self.assertFalse(state.run_enabled)
        self.assertTrue(state.save_enabled)
        self.assertFalse(state.reset_enabled)
        self.assertEqual(state.status, "Unsaved changes")

    def test_save_returns_to_clean_saved_state(self):
        state = ScenarioProjectionGuiState().edited(valid=True).after_run(dirty=True).after_save()
        self.assertFalse(state.run_enabled)
        self.assertFalse(state.save_enabled)
        self.assertEqual(state.status, "Saved assumptions")

    def test_reset_clears_pending_without_discarding_applied_dirty_state(self):
        state = ScenarioProjectionGuiState(dirty=True).edited(valid=True).after_reset()
        self.assertFalse(state.pending_changes)
        self.assertTrue(state.dirty)
        self.assertTrue(state.save_enabled)
        self.assertEqual(state.status, "Unsaved changes")

    def test_reload_clears_pending_and_dirty_state(self):
        state = ScenarioProjectionGuiState(dirty=True).edited(valid=False).after_reload()
        self.assertFalse(state.pending_changes)
        self.assertFalse(state.dirty)
        self.assertFalse(state.save_enabled)
        self.assertEqual(state.status, "Saved assumptions")

    def test_invalid_edit_followed_by_valid_edit_recovers_run_action(self):
        state = ScenarioProjectionGuiState().edited(valid=False)
        recovered = state.edited(valid=True)
        self.assertTrue(recovered.run_enabled)
        self.assertEqual(recovered.status, "Changes ready to run")

    def test_invalid_pending_state_is_preserved_by_reset(self):
        state = ScenarioProjectionGuiState(dirty=True).edited(valid=False).after_reset()
        self.assertFalse(state.pending_changes)
        self.assertTrue(state.pending_valid)
        self.assertTrue(state.save_enabled)
        self.assertEqual(state.status, "Unsaved changes")

    def test_action_states_exposes_canonical_permission_snapshot(self):
        clean = ScenarioProjectionGuiState()
        pending = clean.edited(valid=True)
        dirty = clean.after_run(dirty=True)
        closed = dirty.after_close()
        self.assertEqual(clean.action_states, (("run", False), ("save", False), ("reset", False), ("reload", True)))
        self.assertEqual(pending.action_states, (("run", True), ("save", False), ("reset", True), ("reload", True)))
        self.assertEqual(dirty.action_states, (("run", False), ("save", True), ("reset", False), ("reload", True)))
        self.assertEqual(closed.action_states, (("run", False), ("save", False), ("reset", False), ("reload", False)))
        self.assertEqual(tuple(action for action, _ in clean.action_states), WORKFLOW_ACTIONS)

    def test_action_enabled_reads_from_canonical_action_snapshot(self):
        state = ScenarioProjectionGuiState(dirty=True).edited(valid=True)
        snapshot = dict(state.action_states)
        self.assertEqual(
            {action: state.action_enabled(action) for action in WORKFLOW_ACTIONS},
            snapshot,
        )

    def test_action_state_snapshot_is_immutable(self):
        state = ScenarioProjectionGuiState().edited(valid=True)
        snapshot = state.action_states
        with self.assertRaises(TypeError):
            snapshot[0] = ("run", False)
        self.assertEqual(snapshot, state.action_states)

    def test_action_enabled_matches_all_named_action_properties(self):
        clean = ScenarioProjectionGuiState()
        pending = clean.edited(valid=True)
        dirty = clean.after_run(dirty=True)
        closed = dirty.after_close()
        self.assertEqual(
            [clean.action_enabled(name) for name in ("run", "save", "reset", "reload")],
            [False, False, False, True],
        )
        self.assertEqual(
            [pending.action_enabled(name) for name in ("run", "save", "reset", "reload")],
            [True, False, True, True],
        )
        self.assertEqual(
            [dirty.action_enabled(name) for name in ("run", "save", "reset", "reload")],
            [False, True, False, True],
        )
        self.assertEqual(
            [closed.action_enabled(name) for name in ("run", "save", "reset", "reload")],
            [False, False, False, False],
        )

    def test_available_actions_exposes_canonical_workflow_vocabulary(self):
        state = ScenarioProjectionGuiState()
        self.assertEqual(WORKFLOW_ACTIONS, ("run", "save", "reset", "reload"))
        self.assertEqual(state.available_actions, WORKFLOW_ACTIONS)
        self.assertEqual(len(state.available_actions), len(set(state.available_actions)))

    def test_unknown_action_is_rejected_without_mutating_state(self):
        state = ScenarioProjectionGuiState(dirty=True).edited(valid=True)
        before = state
        with self.assertRaises(ValueError):
            state.action_enabled("export")
        self.assertIs(state, before)

    def test_action_enabled_rejects_unknown_action(self):
        with self.assertRaises(ValueError):
            ScenarioProjectionGuiState().action_enabled("export")

    def test_close_is_terminal_for_all_actions(self):
        state = ScenarioProjectionGuiState(dirty=True).edited(valid=True).after_close()
        self.assertTrue(state.closed)
        self.assertFalse(state.run_enabled)
        self.assertFalse(state.save_enabled)
        self.assertFalse(state.reset_enabled)
        self.assertFalse(state.reload_enabled)
        self.assertEqual(state.status, "Closed")
        self.assertIs(state.after_run(dirty=True), state)
        self.assertIs(state.after_save(), state)
        self.assertIs(state.after_reset(), state)
        self.assertIs(state.after_reload(), state)


if __name__ == "__main__":
    unittest.main()
