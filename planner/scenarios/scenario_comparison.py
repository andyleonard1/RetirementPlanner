from dataclasses import dataclass


@dataclass(slots=True)
class ScenarioComparison:

    name: str

    success: bool

    ending_assets: float

    ending_pension: float

    ending_isa: float

    ending_savings: float

    total_tax: float

    retirement_age: int