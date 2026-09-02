import unittest

from planner.funds.historical_fund_returns import (
    HistoricalFundReturn,
    HistoricalFundReturnImporter,
    HistoricalFundReturnStore,
)


class HistoricalFundReturnTests(unittest.TestCase):
    def setUp(self):
        self.aviva = "GB00BRDCMN86:GBP"
        self.sky = "SKY_NEW_DRAWDOWN_LIFESTYLE"

    def test_actual_return_is_valid(self):
        item = HistoricalFundReturn(
            self.aviva, 2024, 0.08, "Financial Times / Aviva"
        )
        item.validate()

    def test_estimated_return_is_valid(self):
        item = HistoricalFundReturn(
            self.aviva, 2025, 0.06, "internal estimate", "estimated"
        )
        item.validate()

    def test_missing_identifier_is_rejected(self):
        with self.assertRaises(ValueError):
            HistoricalFundReturn("", 2024, 0.08, "source").validate()

    def test_invalid_year_is_rejected(self):
        with self.assertRaises(ValueError):
            HistoricalFundReturn(self.aviva, 1899, 0.08, "source").validate()

    def test_missing_source_is_rejected(self):
        with self.assertRaises(ValueError):
            HistoricalFundReturn(self.aviva, 2024, 0.08, "").validate()

    def test_invalid_data_type_is_rejected(self):
        with self.assertRaises(ValueError):
            HistoricalFundReturn(
                self.aviva, 2024, 0.08, "source", "forecast"
            ).validate()

    def test_store_rejects_duplicate_fund_year(self):
        store = HistoricalFundReturnStore()
        store.add(HistoricalFundReturn(self.aviva, 2024, 0.08, "source"))
        with self.assertRaises(ValueError):
            store.add(HistoricalFundReturn(self.aviva, 2024, 0.09, "other source"))

    def test_store_returns_fund_history_in_year_order(self):
        store = HistoricalFundReturnStore([
            HistoricalFundReturn(self.aviva, 2024, 0.08, "source"),
            HistoricalFundReturn(self.aviva, 2022, -0.04, "source"),
            HistoricalFundReturn(self.aviva, 2023, 0.05, "source"),
        ])
        self.assertEqual(
            [x.year for x in store.for_fund(self.aviva)],
            [2022, 2023, 2024],
        )

    def test_actual_and_estimated_records_are_separated(self):
        store = HistoricalFundReturnStore([
            HistoricalFundReturn(self.aviva, 2024, 0.08, "source", "actual"),
            HistoricalFundReturn(self.aviva, 2025, 0.06, "source", "estimated"),
        ])
        self.assertEqual([x.year for x in store.actual_for_fund(self.aviva)], [2024])
        self.assertEqual(
            [x.year for x in store.estimated_for_fund(self.aviva)], [2025]
        )

    def test_all_returns_are_sorted_by_fund_and_year(self):
        store = HistoricalFundReturnStore([
            HistoricalFundReturn(self.sky, 2024, 0.07, "Sky"),
            HistoricalFundReturn(self.aviva, 2023, 0.05, "Aviva"),
            HistoricalFundReturn(self.aviva, 2022, -0.03, "Aviva"),
        ])
        result = store.all()
        self.assertEqual(
            [(x.fund_identifier, x.year) for x in result],
            [
                (self.aviva, 2022),
                (self.aviva, 2023),
                (self.sky, 2024),
            ],
        )

    def test_importer_uses_actual_as_default(self):
        importer = HistoricalFundReturnImporter()
        result = importer.import_records([{
            "fund_identifier": self.aviva,
            "year": "2024",
            "return_rate": "0.08",
            "source": "Financial Times / Aviva",
        }])
        self.assertEqual(result[0].data_type, "actual")

    def test_importer_accepts_estimated_records(self):
        importer = HistoricalFundReturnImporter()
        result = importer.import_records([{
            "fund_identifier": self.aviva,
            "year": "2025",
            "return_rate": "0.06",
            "source": "internal estimate",
            "data_type": "estimated",
        }])
        self.assertEqual(result[0].data_type, "estimated")

    def test_importer_rejects_missing_required_fields(self):
        importer = HistoricalFundReturnImporter()
        with self.assertRaises(ValueError):
            importer.import_records([{
                "fund_identifier": self.aviva,
                "year": 2024,
                "return_rate": 0.08,
            }])

    def test_provenance_is_preserved(self):
        importer = HistoricalFundReturnImporter()
        result = importer.import_records([{
            "fund_identifier": self.sky,
            "year": 2021,
            "return_rate": -0.02,
            "source": "Sky Pension Plan fund performance",
        }])
        self.assertEqual(
            result[0].source,
            "Sky Pension Plan fund performance",
        )


if __name__ == "__main__":
    unittest.main()
