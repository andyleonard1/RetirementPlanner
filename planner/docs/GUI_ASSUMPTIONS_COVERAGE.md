# GUI Assumptions Editor Coverage — Sprint 278

## Scope

Sprint 278 strengthens regression coverage at the GUI assumptions-editor boundary. It checks that the editor exposes the documented actions (Validate, Format, Apply, Apply & Save, Reload document, Discard changes and Close), wires those actions to the controller boundary, reports unsaved/unapplied state, and preserves the complete JSON document through validation, formatting, application, saving and reload.

The tests also exercise atomic rejection of an invalid nested schedule and ensure validation/formatting do not mutate active assumptions. Unicode and nested schedule data are included to guard against accidental lossy formatting.

## Limits

The button-wiring test inspects the GUI method's Python syntax tree; it does not launch a visible Tk window or claim end-user visual/accessibility testing. Controller lifecycle tests exercise the underlying behavior headlessly. These tests do not establish financial calculation correctness, which remains covered by calculation, integration and golden-scenario tests.

## Run

```bash
python -m pytest -ra tests/test_sprint278_gui_assumptions_coverage.py
```

The complete release acceptance command remains `python -m pytest -ra`.
