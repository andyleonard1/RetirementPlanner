"""
Tests for the typed engine contracts.
"""

import unittest

from planner.assumptions import Assumptions
from planner.cashflow_engine import CashFlowEngine
from planner.contracts import (
    AssumptionsProvider,
    SummaryEngineProtocol,
    TimelineBuilderProtocol,
    TimelineTransformerProtocol,
    ValidatorProtocol,
)
from planner.isa_engine import ISAEngine
from planner.savings_engine import SavingsEngine
from planner.state_pension import StatePensionEngine
from planner.summary_engine import SummaryEngine
from planner.tax_engine import TaxEngine
from planner.timeline import TimelineEngine
from planner.validation_engine import ValidationEngine
from planner.withdrawal_engine import WithdrawalEngine


class TestEngineContracts(unittest.TestCase):

    def setUp(self):
        self.assumptions = Assumptions()

    def test_assumptions_provider_contract(self):
        self.assertIsInstance(
            self.assumptions,
            AssumptionsProvider,
        )

    def test_timeline_builder_contract(self):
        self.assertIsInstance(
            TimelineEngine(self.assumptions),
            TimelineBuilderProtocol,
        )

    def test_timeline_transformer_contract(self):
        engines = [
            CashFlowEngine(self.assumptions),
            StatePensionEngine(self.assumptions),
            SavingsEngine(self.assumptions),
            ISAEngine(self.assumptions),
            WithdrawalEngine(self.assumptions),
            TaxEngine(self.assumptions),
        ]

        for engine in engines:
            with self.subTest(engine=type(engine).__name__):
                self.assertIsInstance(
                    engine,
                    TimelineTransformerProtocol,
                )

    def test_summary_and_validation_contracts(self):
        self.assertIsInstance(
            SummaryEngine(self.assumptions),
            SummaryEngineProtocol,
        )

        self.assertIsInstance(
            ValidationEngine(self.assumptions),
            ValidatorProtocol,
        )


if __name__ == "__main__":
    unittest.main()
