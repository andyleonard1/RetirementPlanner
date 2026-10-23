"""Property sale and ISA-sheltering event engine."""
from __future__ import annotations

import logging

from planner.contracts import AssumptionsProvider, Timeline

logger = logging.getLogger(__name__)


class PropertySaleEngine:
    """Materialise the configured property sale before asset roll-forwards."""

    def __init__(self, assumptions: AssumptionsProvider):
        self.assumptions = assumptions
        self.property_sale = float(assumptions.get("property_sale", 0.0))
        self.property_sale_age = int(assumptions.get("property_sale_age"))
        self.annual_isa_allowance = float(
            assumptions.get("annual_isa_allowance", 0.0)
        )
        self.inflation_link_isa = bool(
            assumptions.get("inflation_link_isa", False)
        )
        self.isa_allowance_schedule_enabled = bool(
            assumptions.get("isa_allowance_schedule_enabled", False)
        )
        self.isa_allowance_schedule = dict(
            assumptions.get("isa_allowance_schedule", {}) or {}
        )

    @staticmethod
    def _tax_year(calendar_year: int) -> str:
        return f"{calendar_year}/{str(calendar_year + 1)[-2:]}"

    def _scheduled_allowance(self, calendar_year: int) -> float:
        """Resolve the latest configured statutory allowance at this year."""
        if not self.isa_allowance_schedule_enabled or not self.isa_allowance_schedule:
            return self.annual_isa_allowance

        current = calendar_year
        candidates = []
        for label, allowance in self.isa_allowance_schedule.items():
            start_year = int(str(label).split("/")[0])
            if start_year <= current:
                candidates.append((start_year, float(allowance)))

        if not candidates:
            return self.annual_isa_allowance

        return max(candidates, key=lambda item: item[0])[1]

    def apply(self, timeline: Timeline) -> Timeline:
        logger.info("Running Property Sale Engine")

        for year in timeline:
            if year.age != self.property_sale_age or self.property_sale <= 0:
                continue

            proceeds = round(self.property_sale, 2)
            isa_allowance = self._scheduled_allowance(year.calendar_year)
            if self.inflation_link_isa:
                isa_allowance *= float(getattr(year, "inflation_factor", 1.0))
            to_isa = round(min(proceeds, isa_allowance), 2)
            to_savings = round(max(0.0, proceeds - to_isa), 2)

            year.property_sale_proceeds = proceeds
            year.property_sale_to_isa = to_isa
            year.property_sale_to_savings = to_savings
            year.isa_contribution = round(year.isa_contribution + to_isa, 2)
            year.savings_money_in = round(year.savings_money_in + to_savings, 2)

        return timeline
