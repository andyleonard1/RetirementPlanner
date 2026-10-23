# Coding Standards

## Formatting

Use **Black-compatible** formatting.

## Linting

Use **Ruff** for static checks where configured.

## Typing

- All new public methods must include type hints.
- Prefer concrete result types at public boundaries.
- Use `Protocol` for structural contracts where inheritance would create unnecessary coupling.
- Avoid `Any` in new public APIs unless the value is intentionally unconstrained.

## Logging

Use the Python `logging` module for diagnostics.

Engines should not use diagnostic `print()` calls. Reports and application entry points may print user-facing output.

## Design

- One responsibility per class.
- Keep public interfaces stable.
- Keep business rules in the appropriate engine.
- Prefer composition over inheritance for engine orchestration.
- Prefer incremental improvement over rewrites.
- Maintain compatibility shims temporarily when they materially reduce migration risk.

## Testing

- Add regression coverage when changing a public interface.
- Preserve golden-scenario behaviour unless a calculation change is intentional.
- Run the complete test suite before closing a sprint.
- Treat a passing-test checkpoint as the protected baseline for the next sprint.
