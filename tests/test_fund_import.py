import csv
import tempfile
import unittest
from pathlib import Path

from planner.funds.fund_import import FundDataImporter


class FundDataImporterTests(unittest.TestCase):
    def setUp(self):
        self.importer = FundDataImporter()

    def test_imports_records(self):
        result = self.importer.import_records([
            {"fund_identifier": "FUND-A", "year": "2023", "return_rate": "0.08"}
        ])
        self.assertEqual(result[0].fund_identifier, "FUND-A")
        self.assertEqual(result[0].year, 2023)
        self.assertAlmostEqual(result[0].return_rate, 0.08)

    def test_imports_multiple_records(self):
        result = self.importer.import_records([
            {"fund_identifier": "A", "year": 2022, "return_rate": 0.10},
            {"fund_identifier": "A", "year": 2023, "return_rate": -0.05},
            {"fund_identifier": "B", "year": 2023, "return_rate": 0.12},
        ])
        self.assertEqual(len(result), 3)

    def test_missing_field_is_rejected(self):
        with self.assertRaises(ValueError):
            self.importer.import_records([{"fund_identifier": "A", "year": 2023}])

    def test_invalid_return_is_rejected(self):
        with self.assertRaises(ValueError):
            self.importer.import_records([{"fund_identifier": "A", "year": 2023, "return_rate": "bad"}])

    def test_blank_identifier_is_rejected(self):
        with self.assertRaises(ValueError):
            self.importer.import_records([{"fund_identifier": " ", "year": 2023, "return_rate": 0.1}])

    def test_invalid_year_is_rejected(self):
        with self.assertRaises(ValueError):
            self.importer.import_records([{"fund_identifier": "A", "year": 1899, "return_rate": 0.1}])

    def test_csv_import(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "returns.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["fund_identifier", "year", "return_rate"])
                writer.writeheader()
                writer.writerow({"fund_identifier": "A", "year": "2024", "return_rate": "0.11"})
            result = self.importer.import_csv(path)
        self.assertEqual(result[0].fund_identifier, "A")
        self.assertAlmostEqual(result[0].return_rate, 0.11)


if __name__ == "__main__":
    unittest.main()
