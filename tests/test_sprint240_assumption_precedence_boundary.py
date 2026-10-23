import unittest

from planner.assumption_resolver import AssumptionResolver
from planner.investment_return import InvestmentReturnResolver


class Sprint240AssumptionPrecedenceBoundaryTests(unittest.TestCase):
    def test_canonical_alias_precedence_is_stable(self):
        resolver = AssumptionResolver({
            "inflation_rate": 0.025, "inflation": 0.05,
            "savings_interest_rate": 0.03, "savings_interest": 0.06,
            "expected_investment_return": 0.0475, "pension_growth": 0.08,
        })
        self.assertEqual(resolver.inflation_rate(), 0.025)
        self.assertEqual(resolver.savings_interest_rate(), 0.03)
        self.assertEqual(resolver.expected_investment_return(), 0.0475)

    def test_monte_carlo_precedence_is_explicit_and_independent(self):
        resolver = AssumptionResolver({
            "expected_return": 0.04,
            "expected_investment_return": 0.0475,
            "pension_growth": 0.08,
        })
        self.assertEqual(resolver.monte_carlo_expected_return(), 0.04)
        resolver = AssumptionResolver({
            "expected_investment_return": 0.0475,
            "pension_growth": 0.08,
        })
        self.assertEqual(resolver.monte_carlo_expected_return(), 0.0475)

    def test_investment_return_boundary_uses_resolver_for_charges_and_schedules(self):
        assumptions = {
            "expected_investment_return": 0.0475,
            "expected_return": 0.04,
            "platform_charge": 0.0025,
            "fund_charge": 0.0025,
            "investment_return_schedule_enabled": True,
            "investment_return_schedule": {"2030": 0.06},
            "isa_growth_rate": 0.04,
            "isa_return_schedule_enabled": True,
            "isa_return_schedule": {"2030": 0.05},
        }
        config = InvestmentReturnResolver.resolve(assumptions)
        self.assertEqual(config.total_charge, 0.005)
        self.assertEqual(InvestmentReturnResolver.scheduled_gross_projection_return(assumptions, 2030), 0.06)
        self.assertEqual(InvestmentReturnResolver.scheduled_isa_return(assumptions, 2030), 0.05)

    def test_resolver_precedence_fallbacks_remain_defined(self):
        self.assertEqual(AssumptionResolver({"pension_growth": 0.08}).monte_carlo_expected_return(), 0.08)
        self.assertEqual(AssumptionResolver({}).platform_charge(), 0.0)
        self.assertEqual(AssumptionResolver({}).fund_charge(), 0.0)


if __name__ == "__main__":
    unittest.main()
