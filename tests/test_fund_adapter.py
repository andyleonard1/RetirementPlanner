import unittest

from planner.funds.fund_adapter import (
    FundDataAdapter,
    FundSourceMetadata,
    InMemoryFundDataAdapter,
)
from planner.funds.fund_import import ImportedFundReturn


class FundDataAdapterTests(unittest.TestCase):
    def test_in_memory_adapter_exposes_records(self):
        records = (
            ImportedFundReturn("A", 2023, 0.10),
            ImportedFundReturn("A", 2024, -0.05),
        )
        adapter = InMemoryFundDataAdapter(records)

        self.assertIsInstance(adapter, FundDataAdapter)
        self.assertEqual(adapter.returns(), records)

    def test_metadata_is_preserved(self):
        adapter = InMemoryFundDataAdapter(
            [],
            source_name="manual",
            source_version="1",
        )

        self.assertEqual(
            adapter.metadata,
            FundSourceMetadata("manual", "1"),
        )

    def test_default_metadata_is_supported(self):
        adapter = InMemoryFundDataAdapter([])

        self.assertEqual(adapter.metadata.source_name, "manual")
        self.assertIsNone(adapter.metadata.source_version)

    def test_adapter_returns_are_immutable(self):
        records = [ImportedFundReturn("A", 2024, 0.10)]
        adapter = InMemoryFundDataAdapter(records)
        records.append(ImportedFundReturn("A", 2025, 0.20))

        self.assertEqual(len(adapter.returns()), 1)

    def test_adapter_can_be_reused(self):
        adapter = InMemoryFundDataAdapter([
            ImportedFundReturn("A", 2024, 0.10),
        ])

        self.assertEqual(adapter.returns(), adapter.returns())


if __name__ == "__main__":
    unittest.main()
