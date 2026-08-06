from dataclasses import dataclass

@dataclass
class RetirementAgeResult:

    age: int

    success: bool

    ending_assets: float

    ending_pension: float

    total_tax: float

    planner_result: object