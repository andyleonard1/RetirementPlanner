import json
from pathlib import Path


class Assumptions:

    def __init__(self):
        self.data = self.load()

    def load(self):

        file_path = Path("data") / "assumptions.json"

        with open(file_path, "r") as file:
            return json.load(file)

    def get(self, name, default=None):
        return self.data.get(name, default)