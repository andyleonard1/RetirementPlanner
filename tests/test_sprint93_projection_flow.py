import unittest

from planner.assumptions import Assumptions
from planner.models import RetirementYear
from planner.pension_engine import PensionEngine
from planner.planner import RetirementPlanner
from planner.funds.projection_engine_integration import ProjectionReturnDecision


class Sprint93ProjectionFlowTests(unittest.TestCase):
    def setUp(self):
        self.assumptions = Assumptions()
        self.assumptions["starting_pension"] = 100000
        self.assumptions["pension_growth"] = 0.04

    def year(self):
        y = RetirementYear(age=65, calendar_year=2030, spouse_age=63)
        y.pension_withdrawal = 0
        return y

    def test_pension_engine_without_decision_uses_legacy_rate(self):
        y = self.year()
        PensionEngine(self.assumptions).apply([y])
        self.assertEqual(y.pension_growth, 4000.00)
        self.assertEqual(y.closing_pension, 104000.00)

    def test_pension_engine_with_disabled_decision_uses_legacy_rate(self):
        y = self.year()
        decision = ProjectionReturnDecision(0.06, "disabled", False)
        PensionEngine(self.assumptions, decision).apply([y])
        self.assertEqual(y.pension_growth, 4000.00)
        self.assertEqual(y.closing_pension, 104000.00)

    def test_pension_engine_with_fund_decision_uses_fund_rate(self):
        y = self.year()
        decision = ProjectionReturnDecision(0.06, "fund-informed scenario: central", True)
        PensionEngine(self.assumptions, decision).apply([y])
        self.assertEqual(y.pension_growth, 6000.00)
        self.assertEqual(y.closing_pension, 106000.00)

    def test_fund_return_overrides_timeline_market_return(self):
        y = self.year()
        y.pension_growth_rate = 0.02
        decision = ProjectionReturnDecision(0.06, "fund-informed scenario: central", True)
        PensionEngine(self.assumptions, decision).apply([y])
        self.assertEqual(y.pension_growth, 6000.00)

    def test_legacy_timeline_market_return_remains_supported(self):
        y = self.year()
        y.pension_growth_rate = 0.02
        PensionEngine(self.assumptions).apply([y])
        self.assertEqual(y.pension_growth, 2000.00)

    def test_withdrawal_is_still_applied_after_fund_growth(self):
        y = self.year()
        y.pension_withdrawal = 10000
        decision = ProjectionReturnDecision(0.06, "fund-informed scenario: central", True)
        PensionEngine(self.assumptions, decision).apply([y])
        self.assertEqual(y.pension_growth, 6000.00)
        self.assertEqual(y.closing_pension, 96000.00)

    def test_zero_fund_return_preserves_balance_before_withdrawal(self):
        y = self.year()
        decision = ProjectionReturnDecision(0.0, "fund-informed scenario: central", True)
        PensionEngine(self.assumptions, decision).apply([y])
        self.assertEqual(y.closing_pension, 100000.00)

    def test_negative_fund_return_reduces_balance(self):
        y = self.year()
        decision = ProjectionReturnDecision(-0.10, "fund-informed scenario: conservative", True)
        PensionEngine(self.assumptions, decision).apply([y])
        self.assertEqual(y.closing_pension, 90000.00)

    def test_fund_return_is_applied_across_multiple_years(self):
        timeline = [self.year(), self.year(), self.year()]
        for i, y in enumerate(timeline):
            y.age += i
            y.calendar_year += i
        decision = ProjectionReturnDecision(0.06, "fund-informed scenario: central", True)
        PensionEngine(self.assumptions, decision).apply(timeline)
        self.assertEqual([y.closing_pension for y in timeline], [106000.00, 112360.00, 119101.60])

    def test_legacy_path_is_numerically_unchanged(self):
        timeline = [self.year(), self.year()]
        for i, y in enumerate(timeline):
            y.age += i
            y.calendar_year += i
        PensionEngine(self.assumptions).apply(timeline)
        self.assertEqual([y.closing_pension for y in timeline], [104000.00, 108160.00])

    def test_planner_accepts_optional_projection_decision(self):
        decision = ProjectionReturnDecision(0.06, "fund-informed scenario: central", True)
        planner = RetirementPlanner(self.assumptions, projection_return_decision=decision)
        self.assertIs(planner.projection_return_decision, decision)

    def test_planner_default_decision_is_none(self):
        planner = RetirementPlanner(self.assumptions)
        self.assertIsNone(planner.projection_return_decision)

    def test_planner_passes_decision_to_pension_engine(self):
        decision = ProjectionReturnDecision(0.06, "fund-informed scenario: central", True)
        planner = RetirementPlanner(self.assumptions, projection_return_decision=decision)
        timeline = [self.year()]
        planner.run_engines = planner.run_engines  # public method remains available
        engine = PensionEngine(self.assumptions, planner.projection_return_decision)
        engine.apply(timeline)
        self.assertEqual(timeline[0].pension_growth, 6000.00)

    def test_planner_without_decision_does_not_force_fund_return(self):
        planner = RetirementPlanner(self.assumptions)
        timeline = [self.year()]
        PensionEngine(self.assumptions, planner.projection_return_decision).apply(timeline)
        self.assertEqual(timeline[0].pension_growth, 4000.00)

    def test_fund_return_does_not_change_tax_free_cash_calculation(self):
        y = self.year()
        y.pension_withdrawal = 10000
        decision = ProjectionReturnDecision(0.06, "fund-informed scenario: central", True)
        PensionEngine(self.assumptions, decision).apply([y])
        self.assertEqual(y.tax_free_cash_used, 2500.00)
        self.assertEqual(y.taxable_pension_withdrawal, 7500.00)

    def test_fund_return_does_not_change_starting_pension(self):
        y = self.year()
        decision = ProjectionReturnDecision(0.06, "fund-informed scenario: central", True)
        PensionEngine(self.assumptions, decision).apply([y])
        self.assertEqual(y.opening_pension, 100000.00)

    def test_high_return_is_not_compounded_twice(self):
        y = self.year()
        decision = ProjectionReturnDecision(0.20, "fund-informed scenario: optimistic", True)
        PensionEngine(self.assumptions, decision).apply([y])
        self.assertEqual(y.pension_growth, 20000.00)
        self.assertEqual(y.closing_pension, 120000.00)

    def test_fund_decision_source_does_not_affect_growth_math(self):
        a = self.year()
        b = self.year()
        PensionEngine(self.assumptions, ProjectionReturnDecision(.06, "A", True)).apply([a])
        PensionEngine(self.assumptions, ProjectionReturnDecision(.06, "B", True)).apply([b])
        self.assertEqual(a.closing_pension, b.closing_pension)

    def test_disabled_decision_return_value_is_ignored(self):
        y = self.year()
        decision = ProjectionReturnDecision(0.25, "disabled", False)
        PensionEngine(self.assumptions, decision).apply([y])
        self.assertEqual(y.pension_growth, 4000.00)


if __name__ == "__main__":
    unittest.main()
