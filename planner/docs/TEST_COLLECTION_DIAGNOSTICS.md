# Pytest collection diagnostics

Use this diagnostic when two environments report different pytest totals. It captures
Python and pytest versions, collection node IDs, per-file counts, and SHA-256 hashes
for test files and common pytest configuration files. It does not run tests or change
financial data.

From the repository root:

```bash
python scripts/test_collection_report.py --output collection-local.json
```

Run the same command in the second environment and compare the two JSON reports:

```bash
python scripts/test_collection_report.py --compare collection-other.json
```

The comparison returns the exact node IDs present only on either side, changed test
file hashes, configuration differences, and runtime versions. A non-zero comparison
exit code means the collected node-ID sets differ. Reports may contain internal test
names; review before sharing outside the project.

This tool is diagnostic only. It does not edit `data/assumptions.json`, regenerate the
golden scenario pack, invoke historical market data, or alter financial calculations.
