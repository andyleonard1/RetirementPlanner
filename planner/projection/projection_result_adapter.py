"""Reporting adapter for structured portfolio projection results."""
from __future__ import annotations

from .scenario_projection_comparison import ScenarioProjectionComparison


class ProjectionResultReportAdapter:
    """Convert projection domain results into a stable report payload.

    This adapter deliberately performs no financial calculations. It only
    reshapes already-calculated values for report/UI consumers.
    """

    def build(self, comparison: ScenarioProjectionComparison) -> dict:
        if not isinstance(comparison, ScenarioProjectionComparison):
            raise TypeError("comparison must be ScenarioProjectionComparison")

        scenarios = []
        for projection in comparison.projections:
            scenarios.append(
                {
                    "name": projection.scenario_name,
                    "source": projection.source,
                    "starting_pension": projection.starting_pension,
                    "annual_return": projection.annual_return,
                    "ending_balance": projection.ending_balance,
                    "total_investment_growth": projection.total_investment_growth,
                    "total_withdrawals": projection.total_withdrawals,
                    "years": [
                        {
                            "year": row.year,
                            "starting_balance": row.starting_balance,
                            "investment_growth": row.investment_growth,
                            "withdrawals": row.withdrawals,
                            "ending_balance": row.ending_balance,
                        }
                        for row in projection.years
                    ],
                }
            )

        return {
            "scenario_names": list(comparison.scenario_names),
            "scenarios": scenarios,
            "ending_balances": dict(comparison.ending_balances),
            "highest_ending_balance": comparison.highest_ending_balance,
            "lowest_ending_balance": comparison.lowest_ending_balance,
            "ending_balance_spread": comparison.ending_balance_spread,
        }
