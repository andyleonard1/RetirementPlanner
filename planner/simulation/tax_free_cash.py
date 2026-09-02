"""Tax-free pension cash strategy infrastructure for RC4 Sprint 63.

This module models how a defined tax-free cash allowance can be used
alongside taxable pension withdrawals to meet a target net income.
It is deliberately isolated from the existing pension/tax engines.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TaxFreeCashConfig:
    allowance: float
    annual_tax_free_cash: float = 0.0

    def validate(self) -> None:
        if self.allowance < 0:
            raise ValueError("allowance cannot be negative")
        if self.annual_tax_free_cash < 0:
            raise ValueError("annual_tax_free_cash cannot be negative")


@dataclass(frozen=True)
class WithdrawalPlan:
    tax_free_cash: float
    taxable_pension: float
    tax_paid: float
    net_income: float
    remaining_allowance: float


class TaxFreeCashStrategy:
    """Apply tax-free cash before taxable pension where requested."""

    def __init__(self, config: TaxFreeCashConfig):
        config.validate()
        self.config = config

    def plan_year(
        self,
        target_net_income: float,
        taxable_pension_required: float,
        tax_paid: float,
        *,
        use_tax_free_cash: bool = True,
    ) -> WithdrawalPlan:
        if target_net_income < 0:
            raise ValueError("target_net_income cannot be negative")
        if taxable_pension_required < 0:
            raise ValueError("taxable_pension_required cannot be negative")
        if tax_paid < 0:
            raise ValueError("tax_paid cannot be negative")

        if not use_tax_free_cash or self.config.allowance <= 0:
            tax_free = 0.0
        else:
            tax_free = min(
                self.config.allowance,
                self.config.annual_tax_free_cash or self.config.allowance,
            )

        taxable_net = max(0.0, taxable_pension_required - tax_paid)
        net_income = tax_free + taxable_net

        return WithdrawalPlan(
            tax_free_cash=tax_free,
            taxable_pension=taxable_pension_required,
            tax_paid=tax_paid,
            net_income=net_income,
            remaining_allowance=self.config.allowance - tax_free,
        )
