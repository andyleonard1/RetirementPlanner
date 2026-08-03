"""
Assumptions

Loads and validates the retirement planner assumptions
from assumptions.json.
"""

import json
import os

from planner.validation_engine import ValidationEngine


class Assumptions:

    def __init__(self, filename="data/assumptions.json"):

        self.filename = filename
        self.data = {}

        self.load()

        ValidationEngine(
            self
        ).validate()

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

        except json.JSONDecodeError as ex:

            raise ValueError(
                f"Invalid JSON in {self.filename}\n{ex}"
            ) from ex

    # -----------------------------------------------------

    def save(self):

        with open(
            self.filename,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                self.data,
                f,
                indent=4,
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