from dataclasses import dataclass


@dataclass(slots=True)
class Recommendation:

    priority: int

    title: str

    message: str

    impact: str