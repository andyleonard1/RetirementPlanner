import unittest
from pathlib import Path

from planner.assumption_resolver import AssumptionResolver
from planner.savings_engine import SavingsEngine


class Sprint237CanonicalSavingsInterestBoundaryTests(unittest.TestCase):
    def test_savings_engine_uses_canonical_savings_interest_rate(self):
        engine = SavingsEngine(
            {
                "starting_savings": 1000.0,
                "savings_interest_rate": 0.03,
                "savings_interest": 0.07,
            }
        )
        self.assertAlmostEqual(engine.interest_rate, 0.03)

    def test_savings_engine_preserves_legacy_fallback(self):
        engine = SavingsEngine(
            {
                "starting_savings": 1000.0,
                "savings_interest": 0.07,
            }
        )
        self.assertAlmostEqual(engine.interest_rate, 0.07)

    def test_savings_interest_direct_reads_are_confined_to_resolver(self):
        offenders = []
        for path in Path("planner").rglob("*.py"):
            if "__pycache__" in path.parts or path.name == "assumption_resolver.py":
                continue
            source = path.read_text(encoding="utf-8")
            for fragment in (
                'assumptions.get("savings_interest_rate")',
                "assumptions.get('savings_interest_rate')",
                'assumptions["savings_interest_rate"]',
                "assumptions['savings_interest_rate']",
                'assumptions.get("savings_interest")',
                "assumptions.get('savings_interest')",
                'assumptions["savings_interest"]',
                "assumptions['savings_interest']",
            ):
                if fragment in source:
                    offenders.append(f"{path}: {fragment}")
        self.assertEqual([], offenders)

    def test_savings_engine_declares_resolver_boundary(self):
        source = Path("planner/savings_engine.py").read_text(encoding="utf-8")
        self.assertIn("from planner.assumption_resolver import AssumptionResolver", source)
        self.assertIn(
            "AssumptionResolver(assumptions).savings_interest_rate()",
            source,
        )


if __name__ == "__main__":
    unittest.main()
