"""Sprint 284: versioned golden outputs for representative retirement scenarios.

Golden values are reviewable fixtures, not generated during test execution. If a
financial result intentionally changes, review the diff and update the fixture
only with an explicit rationale.
"""
from __future__ import annotations

import json
import math
import unittest
from pathlib import Path

from planner.assumptions import Assumptions
from planner.planner import RetirementPlanner

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = Path(__file__).resolve().parent / "golden" / "sprint284_scenarios.json"
FIELDS = (
    "calendar_year", "age", "target_spending", "gross_pension_income",
    "income_tax", "your_state_pension", "closing_pension", "isa_closing", "savings_closing",
    "income_shortfall", "total_assets",
)
BASE = {
    "current_age": 65, "retirement_age": 65, "projection_end_age": 72,
    "spouse_current_age": 62, "current_calendar_year": 2026,
    "starting_pension": 240000.0, "starting_savings": 30000.0,
    "starting_isa": 60000.0, "expected_investment_return": 0.03,
    "platform_charge": 0.0, "fund_charge": 0.0,
    "savings_interest_rate": 0.02, "isa_growth_rate": 0.03,
    "inflation": 0.025, "inflation_link_spending": True,
    "inflation_link_tax": True, "inflation_link_isa": False,
    "state_pension_full": 12548.0, "state_pension_growth": 0.025,
    "state_pension_earnings_growth": 0.03,
    "state_pension_triple_lock_enabled": True, "property_sale": 0.0,
    "property_sale_age": 67, "annual_isa_allowance": 20000.0,
    "withdrawal_strategy": "PENSION_FIRST", "max_pension_income": 30000.0,
    "spending_phase_1": 38000.0, "spending_phase_2": 34000.0,
    "spending_phase_3": 30000.0, "phase_1_end_age": 67,
    "phase_2_end_age": 69,
}
SCENARIOS = {
    "balanced_pension_first": {},
    "isa_first": {"withdrawal_strategy": "ISA_FIRST"},
    "higher_inflation_triple_lock_off": {
        "inflation": 0.04, "state_pension_triple_lock_enabled": False,
        "inflation_link_isa": True,
    },
}


def project(name: str) -> dict:
    assumptions = Assumptions()
    values = dict(BASE)
    values.update(SCENARIOS[name])
    for key, value in values.items():
        assumptions.set(key, value)
    result = RetirementPlanner(assumptions, audit_context="sprint284_golden").run()
    rows = []
    for year in result.timeline:
        row = {}
        for field in FIELDS:
            value = getattr(year, field)
            if isinstance(value, (int, float)):
                row[field] = int(value) if field in ("calendar_year", "age") else round(float(value), 2)
            else:
                raise AssertionError(f"Unexpected non-numeric golden field: {field}")
        rows.append(row)
    return {"timeline": rows, "summary": {
        "ending_pension": round(float(result.summary["ending_pension"]), 2),
        "ending_assets": round(float(result.summary["ending_assets"]), 2),
        "total_tax": round(float(result.summary["total_tax"]), 2),
        "gross_pension": round(float(result.summary["gross_pension"]), 2),
    }}


class Sprint284GoldenScenarioRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture_bytes = FIXTURE.read_bytes()
        cls.fixture = json.loads(cls.fixture_bytes)

    def test_fixture_schema_and_scenario_inventory_are_explicit(self):
        self.assertEqual(self.fixture["format"], "retirement-planner-golden-scenarios")
        self.assertEqual(self.fixture["version"], 1)
        self.assertEqual(set(self.fixture["scenarios"]), set(SCENARIOS))
        for scenario in self.fixture["scenarios"].values():
            self.assertEqual(scenario["fields"], list(FIELDS))
            self.assertTrue(scenario["timeline"])
            for row in scenario["timeline"]:
                self.assertEqual(set(row), set(FIELDS))

    def test_representative_scenarios_match_reviewed_golden_outputs(self):
        for name, expected in self.fixture["scenarios"].items():
            with self.subTest(scenario=name):
                actual = project(name)
                self.assertEqual(len(actual["timeline"]), len(expected["timeline"]))
                for index, (actual_row, expected_row) in enumerate(zip(actual["timeline"], expected["timeline"])):
                    for field in FIELDS:
                        self.assertAlmostEqual(actual_row[field], expected_row[field], delta=0.011,
                                               msg=f"{name}: row {index}, {field}")
                self.assertEqual(set(actual["summary"]), set(expected["summary"]))
                for field, value in expected["summary"].items():
                    self.assertAlmostEqual(actual["summary"][field], value, delta=0.011,
                                           msg=f"{name}: summary {field}")

    def test_scenarios_are_distinct_and_cover_tax_withdrawal_and_policy_variants(self):
        base = self.fixture["scenarios"]["balanced_pension_first"]["timeline"]
        isa = self.fixture["scenarios"]["isa_first"]["timeline"]
        policy = self.fixture["scenarios"]["higher_inflation_triple_lock_off"]["timeline"]
        self.assertTrue(any(a["closing_pension"] != b["closing_pension"] for a, b in zip(base, isa)))
        self.assertTrue(any(a["your_state_pension"] != b["your_state_pension"] for a, b in zip(base, policy)))
        self.assertTrue(any(a["gross_pension_income"] != b["gross_pension_income"] for a, b in zip(base, isa)))

    def test_golden_values_are_finite_and_years_contiguous(self):
        for name, scenario in self.fixture["scenarios"].items():
            years = [row["calendar_year"] for row in scenario["timeline"]]
            self.assertEqual(years, list(range(years[0], years[0] + len(years))), name)
            for row in scenario["timeline"]:
                for field in FIELDS:
                    self.assertTrue(math.isfinite(float(row[field])), f"{name}: {field}")
            for value in scenario["summary"].values():
                self.assertTrue(math.isfinite(float(value)), name)

    def test_running_scenarios_never_rewrites_golden_fixture(self):
        before = self.fixture_bytes
        for name in SCENARIOS:
            project(name)
        self.assertEqual(FIXTURE.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
