# Sprint 291 — GUI Assumptions Editor Interaction & Usability

## Objective

Close the Sprint 278 verification gap by exercising the assumptions editor through real Tkinter widgets and user-facing button actions. This sprint is test-led and does not change financial calculation rules, shipped assumptions defaults or golden fixtures.

## Implementation

- Added native Tkinter integration coverage in `tests/test_sprint291_tk_assumptions_editor.py`.
- The tests create a real Tk root, open the actual assumptions-editor `Toplevel`, locate its `Text` and `ttk.Button` widgets, and invoke the visible actions.
- Covered editor opening and control labels, keyboard-focus eligibility, Validate, Format, Apply, Apply & Save, invalid-document rejection, Reload document, Discard changes, and close confirmation.
- Made the editor text control and all editor action buttons explicitly keyboard-focusable.
- Native GUI tests skip with a clear reason when Tkinter or a display server is unavailable. The target Windows desktop run is the primary GUI acceptance environment; a headless skip is not evidence that the GUI interactions passed.
- Advanced the release-manifest builder default sprint and its regression expectation to Sprint 291.

## Safety boundaries

- Validate and Format must not mutate active assumptions or the saved file.
- Apply changes only the in-memory assumptions document.
- Apply & Save persists only after successful validation.
- Invalid documents must not partially mutate active state or saved bytes.
- Reload document restores editor text from the current in-memory document.
- Discard changes restores the last persisted baseline without writing to disk.
- Closing with unapplied text asks for confirmation and honours the user's choice.

## Validation

Run the focused GUI tests on Windows:

```powershell
python -m pytest -ra tests/test_sprint291_tk_assumptions_editor.py
```

Then run the existing assumptions GUI regressions and the full suite:

```powershell
python -m pytest -ra tests/test_sprint278_gui_assumptions_coverage.py tests/test_sprint278_gui_assumptions_workflow_matrix.py tests/test_scenario_projection_gui.py
python -m pytest -ra
```

A headless environment may skip native Tk tests. Record the Windows GUI test result separately from headless CI results. Sprint acceptance remains pending the user's local Windows execution.

No production financial calculations, shipped assumptions defaults or golden baseline values are changed by Sprint 291.
