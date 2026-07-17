"""
Timeline Engine

Creates one RetirementYear object for every year in the retirement projection.

This engine does not perform any financial calculations.
Its sole responsibility is to build the timeline that all other
engines will populate.
"""
from planner.models import RetirementYear


class TimelineEngine:
    """
    Creates one RetirementYear object for each year in the projection.
    """

    def __init__(self, assumptions):

        self.assumptions = assumptions

    def build(self):

        timeline = []

        start_age = self.assumptions.get("retirement_age")
        end_age = self.assumptions.get("projection_end_age")

        current_age = self.assumptions.get("current_age")
        spouse_current_age = self.assumptions.get("spouse_current_age")
        current_year = self.assumptions.get("current_calendar_year")

        for age in range(start_age, end_age + 1):

            years_elapsed = age - current_age

            calendar_year = current_year + years_elapsed

            spouse_age = spouse_current_age + years_elapsed

            year = RetirementYear(
                age=age,
                calendar_year=calendar_year,
                spouse_age=spouse_age,
            )

            timeline.append(year)

        return timeline