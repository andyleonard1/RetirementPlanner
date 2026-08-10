from dataclasses import dataclass

from planner.assumptions import Assumptions


@dataclass
class Scenario:

    name: str

    assumptions: Assumptions