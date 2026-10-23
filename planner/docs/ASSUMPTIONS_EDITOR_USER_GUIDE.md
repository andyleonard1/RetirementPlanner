# Assumptions Editor User Guide

The scenario projection GUI provides two levels of assumptions editing. The primary screen exposes the common projection inputs. **Edit all assumptions…** opens the advanced editor for the complete `assumptions.json` document.

## Editing the complete document

The advanced editor accepts the complete JSON object used by the assumptions model, including nested values such as `goals`. This keeps the GUI flexible as the assumptions document evolves instead of requiring a dedicated widget for every field.

## Safe workflow

**Validate** checks the complete document without applying changes.

**Format** validates the document and then replaces the editor text with canonical, readable JSON. Formatting does not apply or save the document.

**Apply** validates and applies the complete document in memory. It does not write the file.

**Apply & Save** validates, applies and persists the document through the existing assumptions save mechanism.

**Reload document** replaces editor text with the current in-memory document.

**Discard changes** restores the last persisted validated baseline in memory and refreshes the main GUI inputs.

Closing the editor while text differs from the active document prompts before the text is discarded. Invalid JSON is treated as pending work so it cannot be silently lost.

## Dirty-state meaning

The editor status distinguishes two different conditions:

- **Unapplied text changes** — the text in the editor differs from the active in-memory assumptions.
- **Applied assumption changes are unsaved** — the active assumptions differ from the last persisted baseline.

Both states can exist at the same time. Saving clears the persisted-change state; formatting, reloading and discarding programmatically replace editor text and leave the text widget clean.
