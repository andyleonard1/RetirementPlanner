"""
Assumptions

Loads and validates the retirement planner assumptions
from assumptions.json.
"""

import json
import os
import tempfile
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from planner.assumptions_schema import AssumptionsSchema
from planner.validation_engine import ValidationEngine


@dataclass(frozen=True)
class AssumptionChange:
    """A single configuration change since the last load/save baseline."""

    path: str
    before: Any
    after: Any


class Assumptions:

    def __init__(self, filename="data/assumptions.json"):

        self.filename = filename
        self.data = {}
        self._baseline_data = {}

        self.load()
        self.validate()

    # -----------------------------------------------------

    def load(self):

        if not os.path.exists(self.filename):

            raise FileNotFoundError(
                f"Cannot find assumptions file:\n{self.filename}"
            )

        try:

            with open(
                self.filename,
                "r",
                encoding="utf-8",
            ) as f:

                self.data = json.load(f)
                self._baseline_data = deepcopy(self.data)

        except json.JSONDecodeError as ex:

            raise ValueError(
                f"Invalid JSON in {self.filename}\n{ex}"
            ) from ex

    # -----------------------------------------------------

    def validate(self):
        """Validate the current in-memory configuration.

        Structural schema validation runs before domain/business validation so
        callers receive a clear configuration error at the boundary.
        """

        AssumptionsSchema.validate(self.data)
        ValidationEngine(self).validate()

    # -----------------------------------------------------

    def save(self):
        """Validate and atomically persist the current configuration.

        Invalid in-memory changes are rejected before the existing file is
        touched. A temporary file plus ``os.replace`` prevents a failed write
        from leaving a partially written assumptions file.
        """

        self.validate()

        directory = os.path.dirname(os.path.abspath(self.filename))
        os.makedirs(directory, exist_ok=True)

        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=directory,
                prefix=".assumptions-",
                suffix=".tmp",
                delete=False,
            ) as f:
                temp_path = f.name
                json.dump(
                    self.data,
                    f,
                    indent=4,
                    ensure_ascii=False,
                    allow_nan=False,
                )
                f.write("\n")
                f.flush()
                os.fsync(f.fileno())

            os.replace(temp_path, self.filename)
            temp_path = None
            self._baseline_data = deepcopy(self.data)

        finally:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)

    # -----------------------------------------------------

    def changes(self):
        """Return configuration changes since the last load/save baseline.

        Changes are calculated from the complete configuration snapshot, so
        nested edits such as changes to a goal target are included even when
        the caller mutates the underlying dictionary directly.
        """

        changes = []
        self._collect_changes(
            self._baseline_data,
            self.data,
            path="",
            changes=changes,
        )
        return tuple(changes)

    def has_changes(self):
        """Return True when the in-memory configuration differs from its baseline."""

        return bool(self.changes())

    def reset_change_tracking(self):
        """Accept the current in-memory configuration as the audit baseline."""

        self._baseline_data = deepcopy(self.data)

    @classmethod
    def _collect_changes(cls, before, after, path, changes):
        if isinstance(before, dict) and isinstance(after, dict):
            for key in sorted(set(before) | set(after)):
                child_path = f"{path}.{key}" if path else str(key)
                if key not in before:
                    changes.append(
                        AssumptionChange(child_path, None, deepcopy(after[key]))
                    )
                elif key not in after:
                    changes.append(
                        AssumptionChange(child_path, deepcopy(before[key]), None)
                    )
                else:
                    cls._collect_changes(
                        before[key], after[key], child_path, changes
                    )
            return

        if isinstance(before, list) and isinstance(after, list):
            max_length = max(len(before), len(after))
            for index in range(max_length):
                child_path = f"{path}[{index}]"
                if index >= len(before):
                    changes.append(
                        AssumptionChange(child_path, None, deepcopy(after[index]))
                    )
                elif index >= len(after):
                    changes.append(
                        AssumptionChange(child_path, deepcopy(before[index]), None)
                    )
                else:
                    cls._collect_changes(
                        before[index], after[index], child_path, changes
                    )
            return

        if before != after:
            changes.append(
                AssumptionChange(path, deepcopy(before), deepcopy(after))
            )

    # -----------------------------------------------------

    def get(self, key, default=None):

        return self.data.get(
            key,
            default,
        )

    # -----------------------------------------------------

    def set(self, key, value):

        self.data[key] = value

    # -----------------------------------------------------

    def contains(self, key):

        return key in self.data

    # -----------------------------------------------------

    def keys(self):

        return self.data.keys()

    # -----------------------------------------------------

    def values(self):

        return self.data.values()

    # -----------------------------------------------------

    def items(self):

        return self.data.items()

    # -----------------------------------------------------

    def __getitem__(self, key):

        return self.data[key]

    # -----------------------------------------------------

    def __setitem__(self, key, value):

        self.data[key] = value

    # -----------------------------------------------------

    def __contains__(self, key):

        return key in self.data

    # -----------------------------------------------------

    def __len__(self):

        return len(self.data)

    # -----------------------------------------------------

    def __str__(self):

        return (
            f"Assumptions("
            f"{len(self.data)} settings)"
        )