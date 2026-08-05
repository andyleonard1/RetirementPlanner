"""
Portfolio

Represents an investment portfolio and calculates
its annual return from market data.
"""

from dataclasses import dataclass

from planner.market.models import MarketYear


@dataclass(slots=True)
class Portfolio:

    equity_weight: float
    bond_weight: float

    @property
    def total_weight(self):

        return (
            self.equity_weight
            + self.bond_weight
        )

    def validate(self):

        if abs(self.total_weight - 1.0) > 0.0001:

            raise ValueError(
                "Portfolio weights must total 1.0"
            )

    def annual_return(
        self,
        market_year: MarketYear,
    ):

        self.validate()

        return (

            self.equity_weight
            * market_year.equity

            +

            self.bond_weight
            * market_year.bonds

        ) / 100.0