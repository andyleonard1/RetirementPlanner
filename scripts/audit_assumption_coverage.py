"""Audit the assumptions contract across schema, defaults, metadata and consumers.

Run from the project root: python scripts/audit_assumption_coverage.py [--output PATH]
This is a static/configuration audit; it does not prove that financial outputs are
correct. Runtime integration tests remain the evidence for calculation behavior.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def build_report(root: Path = ROOT) -> dict[str, Any]:
    sys.path.insert(0, str(root))
    from planner.assumption_consumer_catalog import CONSUMERS, consumer_modules
    from planner.assumption_usage_catalog import ROLES, schema_paths, unclassified_schema_paths
    from planner.assumptions_schema import AssumptionsSchema
    from planner.audit_catalog import DESCRIPTIONS

    defaults_path = root / "data" / "assumptions.json"
    defaults = json.loads(defaults_path.read_text(encoding="utf-8"))
    schema = set(schema_paths())
    default_keys = set(defaults)
    roles = set(ROLES)
    described = set(DESCRIPTIONS)
    unknown_default_keys = sorted(default_keys - schema)
    schema_missing_defaults = sorted(schema - default_keys)
    schema_missing_roles = sorted(schema - roles)
    role_without_consumer = sorted(role for role in set(ROLES.values()) if role not in CONSUMERS)
    schema_missing_descriptions = sorted(schema - described)
    consumer_sources = {}
    consumer_missing_modules = []
    for path in sorted(schema):
        modules = consumer_modules(path)
        consumer_sources[path] = list(modules)
        for module_name in modules:
            module_path = root.joinpath(*module_name.split("." )).with_suffix(".py")
            if not module_path.is_file():
                consumer_missing_modules.append({"assumption": path, "module": module_name})
    # The GUI's JSON editor is the supported complete-document editing boundary;
    # its preservation behavior is separately tested by the regression suite.
    gui_controller = root / "planner" / "gui" / "scenario_projection_controller.py"
    gui_editor = gui_controller.is_file() and "apply_assumptions_json" in gui_controller.read_text(encoding="utf-8") and "assumptions_json" in gui_controller.read_text(encoding="utf-8")
    issues = []
    for label, values in (
        ("default keys absent from schema", unknown_default_keys),
        ("schema keys absent from defaults", schema_missing_defaults),
        ("schema keys without operational roles", schema_missing_roles),
        ("roles without consumer boundaries", role_without_consumer),
        ("schema keys without audit descriptions", schema_missing_descriptions),
        ("consumer modules missing from source tree", consumer_missing_modules),
    ):
        if values:
            issues.append({"check": label, "items": values})
    if not gui_editor:
        issues.append({"check": "GUI complete JSON editor boundary", "items": [str(gui_controller.relative_to(root))]})
    return {
        "report_format": "retirement-planner-assumption-coverage-audit",
        "report_version": 1,
        "scope": "schema/defaults/role/consumer/description/GUI-boundary consistency; not financial correctness",
        "status": "PASS" if not issues else "FAIL",
        "counts": {
            "schema_paths": len(schema),
            "default_top_level_keys": len(default_keys),
            "classified_roles": len(set(ROLES.values())),
            "consumer_boundaries": len(CONSUMERS),
            "audit_descriptions": len(described),
        },
        "gui_complete_json_editor_boundary": bool(gui_editor),
        "consumer_modules_by_assumption": consumer_sources,
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = build_report(args.root.resolve())
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        destination = args.output if args.output.is_absolute() else args.root / args.output
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
