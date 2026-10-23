# GUI Assumptions Workflow Coverage

Sprint 278 verifies the advanced assumptions editor as a three-state workflow rather than treating JSON editing as a single operation.

## State boundaries

- **Editor text** is the candidate document currently displayed to the user.
- **Active assumptions** are the validated in-memory values used by the application.
- **Persisted baseline** is the last saved document on disk and the reference used by dirty-state/discard behavior.

These states intentionally differ during an edit. Validate and Format must not change active assumptions or the file. Apply changes only the active in-memory document. Save persists the applied document and clears applied-change tracking. Reload reads the saved document from disk. Discard restores the last saved baseline without writing to disk.

## Regression matrix

`tests/test_sprint278_gui_assumptions_workflow_matrix.py` exercises:

- validation and formatting without mutation of active state, saved baseline or file bytes;
- Apply versus explicit Save, including nested assumption edits;
- reload of the saved document after an in-memory change;
- discard of nested changes back to the persisted baseline;
- clean, unapplied-text, applied-unsaved and combined editor status states;
- malformed editor text treated as pending work and rejected on Apply;
- invalid-document rejection without partial mutation or persistence.

Run the focused matrix with:

```bash
python -m pytest -q tests/test_sprint278_gui_assumptions_workflow_matrix.py
```

## Scope and limitations

The tests target the controller/application boundary and persistence contract. They do not automate mouse/keyboard interaction with a native GUI toolkit and do not establish that financial calculations are correct. The existing assumptions audit, schema validation and engine integration tests remain separate evidence layers. No financial calculations, assumptions defaults or golden baseline were changed for this sprint.
