"""Bridge validated portfolio scenarios into projection inputs."""
from dataclasses import dataclass
from typing import Iterable
from .portfolio_risk_return_scenarios import PortfolioRiskReturnScenario

@dataclass(frozen=True)
class FundInformedProjectionInput:
    starting_pension: float
    expected_return: float
    volatility: float | None
    scenario_name: str
    source: str
    fund_allocation: tuple[tuple[str, float], ...]
    enabled: bool = True

class FundInformedProjectionInputBuilder:
    def build(self, starting_pension: float,
              scenario: PortfolioRiskReturnScenario,
              fund_allocation: Iterable[tuple[str, float]]
              ) -> FundInformedProjectionInput:
        if starting_pension < 0:
            raise ValueError("starting_pension cannot be negative")
        allocation = tuple((str(i), float(w)) for i, w in fund_allocation)
        if not allocation:
            raise ValueError("fund allocation is required")
        if any(not i.strip() for i, _ in allocation):
            raise ValueError("fund identifiers cannot be blank")
        if any(w < 0 for _, w in allocation):
            raise ValueError("fund allocation weights cannot be negative")
        if abs(sum(w for _, w in allocation) - 1.0) > 1e-9:
            raise ValueError("fund allocation must total 1.0")
        if scenario.volatility is not None and scenario.volatility < 0:
            raise ValueError("scenario volatility cannot be negative")
        return FundInformedProjectionInput(
            float(starting_pension), float(scenario.expected_return),
            scenario.volatility, scenario.name, scenario.source, allocation)

    def build_disabled(self, starting_pension: float) -> FundInformedProjectionInput:
        if starting_pension < 0:
            raise ValueError("starting_pension cannot be negative")
        return FundInformedProjectionInput(
            float(starting_pension), 0.0, None, "disabled",
            "fund-informed projection disabled", (), False)
