"""
Tax Optimizer Engine

Compatibility wrapper around the shared OptimisationEngine.

This preserves the historical basic-rate-band behaviour while avoiding a
second implementation of the optimisation traversal.
"""

from planner.optimisation_engine import OptimisationEngine


class TaxOptimizerEngine(OptimisationEngine):

    def __init__(self, assumptions):
        super().__init__(
            assumptions,
            policy="basic_rate_band",
        )
