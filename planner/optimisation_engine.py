"""
Optimisation Engine

Shared optimisation framework for retirement-income calculations.

The live planner uses the Personal Allowance policy implemented by this
engine. Alternative tax-limit policies can reuse the same framework without
duplicating the timeline traversal and result storage.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class OptimisationEngine:
    """Calculate tax-efficient pension limits under named policies.

    The live planner continues to use ``apply()`` exactly as before.  The
    comparison API is deliberately read-only: it calculates policy outcomes
    without changing timeline objects, making it safe for analysis and
    reporting layers.
    """

    _POLICY_DESCRIPTIONS = {
        "personal_allowance": "Personal Allowance less State Pension income.",
        "basic_rate_band": "Basic-rate limit less State Pension income.",
    }

    def __init__(self, assumptions, policy="personal_allowance"):
        self.assumptions = assumptions
        self.policy = policy
        self._validate_policy(policy)

    @classmethod
    def supported_policies(cls):
        """Return the supported optimisation policy names in stable order."""
        return tuple(cls._POLICY_DESCRIPTIONS)

    @classmethod
    def policy_descriptions(cls):
        """Return human-readable descriptions of supported policies."""
        return dict(cls._POLICY_DESCRIPTIONS)

    @classmethod
    def _validate_policy(cls, policy):
        if policy not in cls._POLICY_DESCRIPTIONS:
            raise ValueError(
                f"Unknown optimisation policy: {policy!r}. "
                f"Supported policies: {', '.join(cls.supported_policies())}"
            )

    def _calculate_limit(self, year, policy=None):
        """Return the maximum pension income for the selected policy."""

        selected_policy = self.policy if policy is None else policy
        self._validate_policy(selected_policy)

        state_pension = (
            year.your_state_pension
            + year.spouse_state_pension
        )

        if selected_policy == "basic_rate_band":
            basic_limit = self.assumptions.get("basic_rate_limit")
            return max(0.0, basic_limit - state_pension)

        allowance = self.assumptions.get("personal_allowance")
        return max(0.0, allowance - state_pension)

    def calculate(self, timeline):
        """Return limits for this engine's policy without mutating the timeline."""
        return [
            (year.age, round(self._calculate_limit(year), 2))
            for year in timeline
        ]

    def compare_policies(self, timeline, policies=None):
        """Compare supported policies without mutating timeline objects.

        Returns a mapping of policy name to ``[(age, limit), ...]`` rows.
        """
        selected = (
            self.supported_policies()
            if policies is None
            else tuple(policies)
        )

        for policy in selected:
            self._validate_policy(policy)

        return {
            policy: [
                (year.age, round(self._calculate_limit(year, policy), 2))
                for year in timeline
            ]
            for policy in selected
        }

    def apply(self, timeline):
        """Calculate and store the tax-efficient pension limit for each year."""

        logger.info(
            "Running OptimisationEngine (policy=%s)",
            self.policy,
        )

        for year, (_, remaining_allowance) in zip(
            timeline,
            self.calculate(timeline),
        ):
            year.maximum_tax_efficient_pension = remaining_allowance

            logger.debug(
                "Age %s: tax-efficient pension=%s",
                year.age,
                remaining_allowance,
            )

        return timeline
