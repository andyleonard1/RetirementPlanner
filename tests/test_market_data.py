import unittest

from planner.market.market_data import MarketData


class TestMarketData(unittest.TestCase):

    def test_load(self):

        data = MarketData()

        data.load()

        self.assertGreater(len(data), 0)

    def test_first_record(self):

        data = MarketData()

        data.load()

        year = data.get_year(0)

        self.assertEqual(year.year, 2020)
        self.assertEqual(year.equity, 16.2)
        self.assertEqual(year.bonds, 7.5)
        self.assertEqual(year.inflation, 0.9)


if __name__ == "__main__":
    unittest.main()