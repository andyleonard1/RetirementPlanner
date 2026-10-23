"""Build projection inputs from the actual internal investment profile."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .investment_profile import InvestmentProfile


@dataclass(frozen=True)
class ProjectionInput:
    fund_identifier: str
    provider: str
    fund_name: str
    projection_eligible: bool
    historical_return_available: bool
    volatility_available: bool
    charges_available: bool
    asset_allocation_available: bool
    glide_path: bool
    target_retirement_year: int | None
    confidence: str
    limitations: tuple[str, ...]


class ProjectionInputBuilder:
    """Derive projection readiness from stored internal fund-profile data.

    No synthetic availability flags are stored on InvestmentProfile. Availability
    is derived only from information actually present in the profile.
    """

    def build(self, profile: InvestmentProfile) -> ProjectionInput:
        limitations: list[str] = []

        # The current Sprint 84 profile stores a data-quality classification
        # rather than a separate historical-data flag.
        historical = profile.data_quality in {
            "limited_history",
            "historical_snapshot",
            "complete_history",
        }

        # Volatility requires an actual return series/volatility metric. The
        # profile currently does not store one, so do not infer it.
        volatility = False

        charges = profile.annual_charge is not None

        # An asset allocation is available only where explicit weights are
        # stored. Merely having underlying-investment names is not sufficient.
        allocation = bool(profile.asset_allocation)

        if not historical:
            limitations.append("Historical return data is unavailable.")
        if not volatility:
            limitations.append("Volatility data is unavailable.")
        if not charges:
            limitations.append("Fund charge data is unavailable.")
        if not allocation:
            limitations.append("Asset allocation data is unavailable.")

        # A fund can be used for a fund-informed projection when some
        # historical evidence exists. Missing secondary characteristics reduce
        # confidence rather than creating invented values.
        eligible = historical

        if not eligible:
            confidence = "ineligible"
        elif limitations:
            confidence = "limited"
        else:
            confidence = "high"

        return ProjectionInput(
            fund_identifier=profile.identifier,
            provider=profile.provider,
            fund_name=profile.name,
            projection_eligible=eligible,
            historical_return_available=historical,
            volatility_available=volatility,
            charges_available=charges,
            asset_allocation_available=allocation,
            glide_path=profile.glide_path,
            target_retirement_year=profile.target_retirement_year,
            confidence=confidence,
            limitations=tuple(limitations),
        )

    def build_many(
        self, profiles: Iterable[InvestmentProfile]
    ) -> tuple[ProjectionInput, ...]:
        return tuple(self.build(profile) for profile in profiles)
