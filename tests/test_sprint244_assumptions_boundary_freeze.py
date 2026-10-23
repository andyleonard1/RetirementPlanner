import ast
import unittest
from pathlib import Path

from planner.assumption_resolver import AssumptionResolver


class Sprint244AssumptionsBoundaryFreezeTests(unittest.TestCase):
    ROOT = Path(__file__).resolve().parents[1]
    RESOLVER = ROOT / "planner" / "assumption_resolver.py"
    LEGACY = ("inflation", "savings_interest", "pension_growth")
    CANONICAL = ("inflation_rate", "savings_interest_rate", "expected_investment_return")

    def test_legacy_aliases_are_resolver_only(self):
        offenders = []
        for path in (self.ROOT / "planner").rglob("*.py"):
            if path == self.RESOLVER or "__pycache__" in path.parts:
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            source = path.read_text(encoding="utf-8")
            for key in self.LEGACY:
                if f'get("{key}")' in source or f"get('{key}')" in source:
                    offenders.append(f"{path}: {key}")
                if f'["{key}"]' in source or f"['{key}']" in source:
                    offenders.append(f"{path}: {key} index")
        self.assertEqual([], offenders)

    def test_canonical_alias_contract_is_complete(self):
        self.assertEqual(
            dict(zip(self.CANONICAL, self.LEGACY)),
            AssumptionResolver._ALIASES,
        )

    def test_resolver_preserves_canonical_precedence_at_freeze_boundary(self):
        resolver = AssumptionResolver({
            "inflation_rate": 0.025, "inflation": 0.09,
            "savings_interest_rate": 0.03, "savings_interest": 0.08,
            "expected_investment_return": 0.0475, "pension_growth": 0.12,
        })
        self.assertEqual(0.025, resolver.inflation_rate())
        self.assertEqual(0.03, resolver.savings_interest_rate())
        self.assertEqual(0.0475, resolver.expected_investment_return())

    def test_monte_carlo_precedence_remains_distinct(self):
        resolver = AssumptionResolver({
            "expected_return": 0.04,
            "expected_investment_return": 0.0475,
            "pension_growth": 0.12,
        })
        self.assertEqual(0.04, resolver.monte_carlo_expected_return())


if __name__ == "__main__":
    unittest.main()
