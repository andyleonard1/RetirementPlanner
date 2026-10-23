import unittest
from pathlib import Path

from planner.assumption_resolver import AssumptionResolver
from planner.investment_return import InvestmentReturnResolver


class Sprint239AssumptionConsumerBoundaryTests(unittest.TestCase):
    def test_canonical_operational_accessors_are_available(self):
        assumptions = {
            "investment_volatility": 0.11,
            "inflation_volatility": 0.012,
            "isa_growth_rate": 0.041,
            "state_pension_full": 12548,
            "state_pension_growth": 0.035,
            "state_pension_earnings_growth": 0.03,
            "state_pension_triple_lock_enabled": True,
            "state_pension_earnings_growth_schedule_enabled": False,
        }
        resolver = AssumptionResolver(assumptions)
        self.assertEqual(resolver.investment_volatility(), 0.11)
        self.assertEqual(resolver.inflation_volatility(), 0.012)
        self.assertEqual(resolver.isa_growth_rate(), 0.041)
        self.assertEqual(resolver.state_pension_full(), 12548.0)
        self.assertEqual(resolver.state_pension_growth(), 0.035)
        self.assertEqual(resolver.state_pension_earnings_growth(), 0.03)
        self.assertTrue(resolver.state_pension_triple_lock_enabled())

    def test_scheduled_isa_return_uses_canonical_resolver_boundary(self):
        assumptions = {
            "isa_growth_rate": 0.04,
            "isa_return_schedule_enabled": False,
        }
        self.assertEqual(
            InvestmentReturnResolver.scheduled_isa_return(assumptions, 2026),
            0.04,
        )

    def test_calculation_modules_do_not_directly_read_selected_canonical_assumptions(self):
        keys = (
            "investment_volatility",
            "inflation_volatility",
            "isa_growth_rate",
            "state_pension_full",
            "state_pension_growth",
            "state_pension_earnings_growth",
            "state_pension_triple_lock_enabled",
            "state_pension_earnings_growth_schedule_enabled",
            "state_pension_earnings_growth_schedule",
        )
        offenders = []
        for path in Path("planner").rglob("*.py"):
            if "__pycache__" in path.parts or path.name == "assumption_resolver.py":
                continue
            source = path.read_text(encoding="utf-8")
            for key in keys:
                if f'assumptions.get("{key}"' in source or f"assumptions.get('{key}'" in source:
                    offenders.append(f"{path}: {key}")
                if f'self.assumptions.get("{key}"' in source or f"self.assumptions.get('{key}'" in source:
                    offenders.append(f"{path}: self.{key}")
        self.assertEqual([], offenders)

    def test_legacy_alias_boundary_remains_unchanged(self):
        assumptions = {
            "inflation_rate": 0.025,
            "inflation": 0.04,
            "savings_interest_rate": 0.03,
            "savings_interest": 0.05,
            "expected_investment_return": 0.0475,
            "pension_growth": 0.08,
        }
        resolver = AssumptionResolver(assumptions)
        self.assertEqual(resolver.inflation_rate(), 0.025)
        self.assertEqual(resolver.savings_interest_rate(), 0.03)
        self.assertEqual(resolver.expected_investment_return(), 0.0475)


if __name__ == "__main__":
    unittest.main()
