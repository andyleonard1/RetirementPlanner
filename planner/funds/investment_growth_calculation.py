"""Apply a selected projection return to investment growth."""
from dataclasses import dataclass
from .projection_engine_integration import ProjectionReturnDecision

@dataclass(frozen=True)
class InvestmentGrowthResult:
    starting_balance: float
    expected_return: float
    ending_balance: float
    source: str
    fund_informed: bool

class InvestmentGrowthCalculator:
    def calculate(self, starting_balance: float, decision: ProjectionReturnDecision) -> InvestmentGrowthResult:
        if starting_balance < 0:
            raise ValueError("starting_balance cannot be negative")
        return InvestmentGrowthResult(
            float(starting_balance),
            float(decision.expected_return),
            float(starting_balance) * (1.0 + float(decision.expected_return)),
            decision.source,
            decision.fund_informed,
        )
