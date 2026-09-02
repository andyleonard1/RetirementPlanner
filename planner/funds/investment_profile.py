"""Provider-neutral internal investment profiles for RC4 Sprint 84."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping


@dataclass(frozen=True)
class InvestmentProfile:
    identifier: str
    provider: str
    name: str
    currency: str = "GBP"
    investment_type: str = "fund"
    annual_charge: float | None = None
    target_retirement_year: int | None = None
    glide_path: bool = False
    underlying_investments: tuple[str, ...] = ()
    asset_allocation: tuple[tuple[str, float], ...] = ()
    data_source: str | None = None
    data_quality: str = "unknown"

    def validate(self) -> None:
        if not self.identifier.strip():
            raise ValueError("identifier is required")
        if not self.provider.strip():
            raise ValueError("provider is required")
        if not self.name.strip():
            raise ValueError("name is required")
        if not self.currency.strip():
            raise ValueError("currency is required")
        if self.annual_charge is not None and self.annual_charge < 0:
            raise ValueError("annual_charge cannot be negative")
        if any(weight < 0 for _, weight in self.asset_allocation):
            raise ValueError("asset allocation cannot contain negative weights")
        if self.asset_allocation:
            total = sum(weight for _, weight in self.asset_allocation)
            if abs(total - 1.0) > 1e-6:
                raise ValueError("asset allocation must total 100 percent")


class InvestmentProfileRegistry:
    """Store internal fund metadata separately from user assumptions."""

    def __init__(self, profiles: Iterable[InvestmentProfile] = ()):
        self._profiles: dict[str, InvestmentProfile] = {}
        for profile in profiles:
            self.add(profile)

    def add(self, profile: InvestmentProfile) -> None:
        profile.validate()
        if profile.identifier in self._profiles:
            raise ValueError(f"duplicate investment profile: {profile.identifier}")
        self._profiles[profile.identifier] = profile

    def get(self, identifier: str) -> InvestmentProfile:
        try:
            return self._profiles[identifier]
        except KeyError as exc:
            raise KeyError(f"investment profile not found: {identifier}") from exc

    def __len__(self) -> int:
        return len(self._profiles)


AVIVA_UNIVERSAL_2027 = InvestmentProfile(
    identifier="GB00BRDCMN86:GBP",
    provider="Aviva",
    name="Aviva Insured Funds Universal 2027 Retirement S14",
    currency="GBP",
    investment_type="target_retirement_fund",
    annual_charge=0.0035,
    target_retirement_year=2027,
    glide_path=True,
    data_source="Financial Times / Aviva",
    data_quality="limited_history",
)

SKY_NEW_DRAWDOWN_LIFESTYLE = InvestmentProfile(
    identifier="SKY_NEW_DRAWDOWN_LIFESTYLE",
    provider="Sky Pension Plan",
    name="New Drawdown Lifestyle",
    currency="GBP",
    investment_type="lifestyle_strategy",
    glide_path=True,
    underlying_investments=(
        "BlackRock Aquila Life (30:70) Currency Hedged Global Equity Fund",
        "Schroders Diversified Growth Fund",
        "BlackRock Aquila Life Cash Fund",
    ),
    data_source="Sky Pension Plan fund performance",
    data_quality="historical_snapshot",
)
