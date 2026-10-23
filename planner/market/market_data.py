"""
Market Data

Loads historical annual market returns from CSV.
"""

import csv

from planner.market.models import MarketYear


class MarketData:

    def __init__(self, filename="data/market_returns.csv"):

        self.filename = filename
        self.years = []

    # -----------------------------------------------------

    def load(self):

        self.years.clear()

        with open(
            self.filename,
            newline="",
            encoding="utf-8",
        ) as csvfile:

            reader = csv.DictReader(csvfile)

            for row in reader:

                self.years.append(

                    MarketYear(

                        year=int(row["Year"]),

                        equity=float(row["Equity"]),

                        bonds=float(row["Bonds"]),

                        inflation=float(row["Inflation"]),

                    )

                )

    # -----------------------------------------------------

    def get_year(self, index):

        return self.years[index]

    # -----------------------------------------------------

    def get_by_calendar_year(self, calendar_year):

        for year in self.years:

            if year.year == calendar_year:

                return year

        return None

    # -----------------------------------------------------

    def __len__(self):

        return len(self.years)

    # -----------------------------------------------------

    def __iter__(self):

        return iter(self.years)