"""Calculation-free export boundary for scenario projection report snapshots."""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Mapping

from .scenario_projection_report import ScenarioProjectionReport


def _mutable_value(value: Any) -> Any:
    """Recreate ordinary containers from an immutable report snapshot."""
    if isinstance(value, Mapping):
        return {key: _mutable_value(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_mutable_value(item) for item in value]
    return value


def _atomic_write_bundle(files: Mapping[Path, str], *, overwrite: bool = False) -> None:
    """Publish a small multi-file bundle with rollback on publication failure."""
    paths = tuple(files)
    if not paths:
        return
    parents = {path.parent.resolve() for path in paths}
    if len(parents) != 1:
        raise ValueError("bundle files must share one destination directory")
    parent = next(iter(parents))
    parent.mkdir(parents=True, exist_ok=True)
    if not overwrite:
        conflicts = [path for path in paths if path.exists()]
        if conflicts:
            raise FileExistsError(f"export destination already exists: {conflicts[0]}")

    temporary: dict[Path, Path] = {}
    backups: dict[Path, Path] = {}
    published: list[Path] = []
    try:
        for destination, text in files.items():
            with NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=parent,
                prefix=f".{destination.name}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                handle.write(text)
                handle.flush()
                temporary[destination] = Path(handle.name)

        if overwrite:
            for destination in paths:
                if destination.exists():
                    with NamedTemporaryFile(
                        dir=parent,
                        prefix=f".{destination.name}.",
                        suffix=".bak",
                        delete=False,
                    ) as handle:
                        backup = Path(handle.name)
                    backup.unlink(missing_ok=True)
                    destination.replace(backup)
                    backups[destination] = backup

        for destination in paths:
            temporary[destination].replace(destination)
            published.append(destination)
    except Exception:
        for destination in published:
            destination.unlink(missing_ok=True)
        for destination, backup in backups.items():
            if backup.exists():
                backup.replace(destination)
        raise
    finally:
        for temporary_path in temporary.values():
            temporary_path.unlink(missing_ok=True)
        for backup in backups.values():
            backup.unlink(missing_ok=True)


def export_snapshot_bundle(
    snapshot: Mapping[str, Any],
    directory: str | Any,
    stem: str = "retirement_projection",
    *,
    overwrite: bool = False,
) -> dict[str, Path]:
    """Export one validated immutable report snapshot as JSON/text companions."""
    ScenarioProjectionReport().build_from_snapshot(snapshot)
    ScenarioProjectionReport.render_text_from_snapshot(snapshot)
    if not isinstance(stem, str) or not stem.strip():
        raise ValueError("export bundle stem must be a non-empty string")
    safe_stem = stem.strip()
    if Path(safe_stem).name != safe_stem:
        raise ValueError("export bundle stem must be a filename stem, not a path")

    destination = Path(directory)
    json_path = destination / f"{safe_stem}.json"
    text_path = destination / f"{safe_stem}.txt"
    payload = _mutable_value(snapshot["payload"])
    files = {
        json_path: json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        text_path: str(snapshot["text"]) + "\n",
    }
    _atomic_write_bundle(files, overwrite=overwrite)
    return {"json": json_path, "text": text_path}
