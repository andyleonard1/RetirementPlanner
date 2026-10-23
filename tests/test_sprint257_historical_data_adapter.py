import json
import shutil
import tempfile
import unittest
from pathlib import Path

from planner.market.historical_data_adapter import (
    FIXTURE_FORMAT,
    HistoricalDataSourceAdapter,
    HistoricalFixtureError,
    HistoricalSeriesDataset,
    load_historical_fixture,
    validate_dataset,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "historical_returns_v1.json"


class Sprint257HistoricalDataAdapterTests(unittest.TestCase):
    def test_versioned_fixture_loads_and_preserves_observations(self):
        dataset = load_historical_fixture(FIXTURE)
        self.assertEqual(dataset.format_version, 1)
        self.assertEqual(dataset.contract.series_id, "sample-gbp-annual-returns")
        self.assertEqual([item.year for item in dataset.observations], [2020, 2021, 2022])

    def test_fixture_preserves_actual_estimated_status_and_provenance(self):
        dataset = load_historical_fixture(FIXTURE)
        self.assertEqual([item.status for item in dataset.observations], ["actual", "estimated", "actual"])
        self.assertEqual(dataset.observations[1].source_url, "https://example.invalid/synthetic-fixture")

    def test_fixture_is_explicitly_synthetic(self):
        dataset = load_historical_fixture(FIXTURE)
        self.assertIn("Synthetic", dataset.contract.description)
        self.assertEqual(dataset.observations[0].source_name, "Synthetic test fixture")

    def test_unknown_format_version_is_rejected(self):
        payload = json.loads(FIXTURE.read_text())
        payload["format_version"] = 2
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.json"
            path.write_text(json.dumps(payload))
            with self.assertRaisesRegex(HistoricalFixtureError, "unsupported format_version"):
                load_historical_fixture(path)

    def test_non_integer_format_version_is_rejected(self):
        payload = json.loads(FIXTURE.read_text())
        payload["format_version"] = 1.0
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.json"
            path.write_text(json.dumps(payload))
            with self.assertRaisesRegex(HistoricalFixtureError, "unsupported format_version"):
                load_historical_fixture(path)

    def test_wrong_format_identifier_is_rejected(self):
        payload = json.loads(FIXTURE.read_text())
        payload["format"] = "other-format"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.json"
            path.write_text(json.dumps(payload))
            with self.assertRaisesRegex(HistoricalFixtureError, "format must be"):
                load_historical_fixture(path)

    def test_unknown_root_key_is_rejected(self):
        payload = json.loads(FIXTURE.read_text())
        payload["provider_magic"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.json"
            path.write_text(json.dumps(payload))
            with self.assertRaisesRegex(HistoricalFixtureError, "unknown keys"):
                load_historical_fixture(path)

    def test_gap_is_not_interpolated_or_fabricated(self):
        payload = json.loads(FIXTURE.read_text())
        payload["observations"] = [payload["observations"][0], payload["observations"][2]]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.json"
            path.write_text(json.dumps(payload))
            with self.assertRaisesRegex(HistoricalFixtureError, "missing calendar years: 2021"):
                load_historical_fixture(path)

    def test_numeric_rate_is_preserved_without_percent_coercion(self):
        payload = json.loads(FIXTURE.read_text())
        payload["observations"][0]["equity_return"] = 5.2
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.json"
            path.write_text(json.dumps(payload))
            dataset = load_historical_fixture(path)
            self.assertEqual(dataset.observations[0].equity_return, 5.2)

    def test_malformed_json_has_domain_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.json"
            path.write_text("{")
            with self.assertRaisesRegex(HistoricalFixtureError, "cannot read historical fixture"):
                load_historical_fixture(path)

    def test_protocol_is_runtime_checkable(self):
        class StubAdapter:
            def load_series(self, series_id: str) -> HistoricalSeriesDataset:
                return load_historical_fixture(FIXTURE)
        self.assertIsInstance(StubAdapter(), HistoricalDataSourceAdapter)

    def test_dataset_validator_checks_contract_again(self):
        dataset = load_historical_fixture(FIXTURE)
        validate_dataset(dataset)
        invalid = HistoricalSeriesDataset(dataset.contract, dataset.observations, format_version=2)
        with self.assertRaisesRegex(HistoricalFixtureError, "unsupported format_version"):
            validate_dataset(invalid)

    def test_fixture_format_identifier_is_stable(self):
        self.assertEqual(FIXTURE_FORMAT, "retirement-planner-historical-series")

    def test_fixture_path_is_versioned(self):
        self.assertTrue(FIXTURE.name.endswith("_v1.json"))


if __name__ == "__main__":
    unittest.main()
