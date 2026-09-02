"""Integration adapter for Sprint 63 tax-free cash strategy.

Keeps the strategy layer separate from the existing tax and withdrawal
engines while providing a stable contract for future planner integration.
"""
from __future__ import annotations

from dataclasses import dataclass

from .tax_free_cash import TaxFreeCashStrategy, WithdrawalPlan


@dataclass(frozen=True)
class TaxFreeCashIntegrationResult:
    plan: WithdrawalPlan
    taxable_income_before_tax_free_cash: float


class TaxFreeCashIntegration:
    def __init__(self, strategy: TaxFreeCashStrategy):
        self.strategy = strategy

    def apply(
        self,
        target_net_income: float,
        taxable_pension_required: float,
        tax_paid: float,
        *,
        use_tax_free_cash: bool = True,
    ) -> TaxFreeCashIntegrationResult:
        plan = self.strategy.plan_year(
            target_net_income=target_net_income,
            taxable_pension_required=taxable_pension_required,
            tax_paid=tax_paid,
            use_tax_free_cash=use_tax_free_cash,
        )
        return TaxFreeCashIntegrationResult(
            plan=plan,
            taxable_income_before_tax_free_cash=taxable_pension_required,
        )
