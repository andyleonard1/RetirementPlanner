import unittest

from planner.market.models import MarketYear
from planner.market.portfolio import Portfolio


class TestPortfolio(unittest.TestCase):

    def test_equal_weights(self):

        portfolio = Portfolio(

            equity_weight=0.5,

            bond_weight=0.5,

        )

        year = MarketYear(

            year=2024,

            equity=10.0,

            bonds=2.0,

            inflation=2.5,

        )

        result = portfolio.annual_return(year)

        self.assertAlmostEqual(
            result,
            0.06,
            places=6,
        )

    def test_sixty_forty(self):

        portfolio = Portfolio(

            equity_weight=0.6,

            bond_weight=0.4,

        )

        year = MarketYear(

            year=2024,

            equity=12.0,

            bonds=4.0,

            inflation=2.0,

        )

        result = portfolio.annual_return(year)

        self.assertAlmostEqual(
            result,
            0.088,
            places=6,
        )

    def test_invalid_weights(self):

        portfolio = Portfolio(

            equity_weight=0.8,

            bond_weight=0.5,

        )

        year = MarketYear(

            year=2024,

            equity=10,

            bonds=5,

            inflation=2,

        )

        with self.assertRaises(ValueError):

            portfolio.annual_return(year)


if __name__ == "__main__":
    unittest.main()