import unittest
from pathlib import Path

from planner.assumption_resolver import AssumptionResolver
from planner.monte_carlo_engine import MonteCarloEngine
from planner.state_pension import StatePensionEngine


class Sprint235CanonicalAssumptionBoundaryTests(unittest.TestCase):
    def test_state_pension_uses_canonical_inflation_with_legacy_fallback(self):
        canonical = StatePensionEngine(
            {"inflation_rate": 0.031, "inflation": 0.021}
        )
        legacy = StatePensionEngine({"inflation": 0.021})
        self.assertAlmostEqual(canonical.cpi_growth, 0.031)
        self.assertAlmostEqual(legacy.cpi_growth, 0.021)

    def test_monte_carlo_inflation_mean_uses_resolver_boundary(self):
        assumptions = {
            "expected_return": 0.04,
            "expected_investment_return": 0.0475,
            "pension_growth": 0.04,
            "inflation_rate": 0.031,
            "inflation": 0.021,
            "investment_volatility": 0.0,
            "inflation_volatility": 0.0,
            "platform_charge": 0.0,
            "fund_charge": 0.0,
            "current_age": 62,
            "projection_end_age": 62,
        }
        # The resolver boundary is independently asserted here; the engine's
        # zero-volatility path must therefore retain the canonical mean.
        self.assertAlmostEqual(
            AssumptionResolver(assumptions).inflation_rate(), 0.031
        )
        self.assertAlmostEqual(
            AssumptionResolver({"inflation": 0.021}).inflation_rate(), 0.021
        )

    def test_canonical_inflation_direct_reads_are_confined_to_resolver(self):
        offenders = []
        for path in Path("planner").rglob("*.py"):
            if "__pycache__" in path.parts or path.name == "assumption_resolver.py":
                continue
            source = path.read_text(encoding="utf-8")
            for fragment in (
                'assumptions.get("inflation_rate")',
                "assumptions.get('inflation_rate')",
                'assumptions["inflation_rate"]',
                "assumptions['inflation_rate']",
            ):
                if fragment in source:
                    offenders.append(f"{path}: {fragment}")
        self.assertEqual([], offenders)

    def test_state_pension_and_monte_carlo_import_resolver_boundary(self):
        state_source = Path("planner/state_pension.py").read_text(encoding="utf-8")
        monte_source = Path("planner/monte_carlo_engine.py").read_text(encoding="utf-8")
        self.assertIn("AssumptionResolver", state_source)
        self.assertIn("AssumptionResolver", monte_source)


if __name__ == "__main__":
    unittest.main()
