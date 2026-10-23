"""
State Pension Engine

Calculates State Pension for both spouses and updates the
RetirementYear objects created by the TimelineEngine.
"""
import logging

from planner.contracts import AssumptionsProvider, Timeline
from planner.assumption_resolver import AssumptionResolver

logger = logging.getLogger(__name__)

class StatePensionEngine:

    def __init__(self, assumptions: AssumptionsProvider):

        self.assumptions = assumptions
        resolver = AssumptionResolver(assumptions)

        self.full_pension = resolver.state_pension_full()
        self.growth = resolver.state_pension_growth()
        self.earnings_growth = resolver.state_pension_earnings_growth()
        self.triple_lock_enabled = resolver.state_pension_triple_lock_enabled()
        self.cpi_growth = resolver.inflation_rate()
        self.earnings_schedule_enabled = resolver.state_pension_earnings_growth_schedule_enabled()
        self.earnings_schedule = resolver.state_pension_earnings_growth_schedule()

    def _earnings_growth_for_year(self, calendar_year: int | None) -> float:
        if not self.earnings_schedule_enabled or calendar_year is None:
            return float(self.earnings_growth)
        scheduled = self.earnings_schedule.get(str(calendar_year))
        if scheduled is None:
            return float(self.earnings_growth)
        return float(scheduled)

    def _annual_growth(
        self,
        inflation_rate: float | None = None,
        calendar_year: int | None = None,
    ) -> float:
        """Resolve the annual State Pension increase.

        When triple lock is enabled, the annual CPI input comes from the
        projected year when available. This lets Monte Carlo inflation paths
        flow consistently into State Pension as well as spending, tax and ISA
        calculations.
        """
        if not self.triple_lock_enabled:
            return self.growth

        cpi_growth = (
            self.cpi_growth
            if inflation_rate is None
            else inflation_rate
        )

        return max(
            self._earnings_growth_for_year(calendar_year),
            float(cpi_growth),
            0.025,
        )

    def apply(self, timeline: Timeline) -> Timeline:
        logger.info("Running State Pension Engine")

        # Build an age-indexed annual growth map. A normal planner timeline
        # supplies every year, while direct engine callers may supply a single
        # year (for example age 68); in that case the current configured rate
        # is used for any earlier missing State Pension increases.
        rates_by_age = {}
        for year in timeline:
            year_inflation = getattr(year, "inflation_rate", None)
            if year_inflation is None:
                year_inflation = self.cpi_growth
            rates_by_age[year.age] = self._annual_growth(
                year_inflation,
                getattr(year, "calendar_year", None),
            )

        def accumulated_factor(target_age: int) -> float:
            factor = 1.0
            for age in range(68, target_age + 1):
                source_year = next(
                    (item for item in timeline if item.age == age),
                    None,
                )
                if source_year is not None:
                    rate = rates_by_age[age]
                else:
                    rate = self._annual_growth(self.cpi_growth)
                factor *= 1 + rate
            return factor

        for year in timeline:
            age = year.age

            your_pension = (
                self.full_pension * accumulated_factor(age)
                if age >= 67
                else 0
            )
            spouse_pension = (
                self.full_pension * accumulated_factor(age)
                if age >= 69
                else 0
            )

            year.your_state_pension = round(your_pension, 2)
            year.spouse_state_pension = round(spouse_pension, 2)

        return timeline