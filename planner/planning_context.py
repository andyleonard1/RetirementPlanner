"""
Planning Context

Shared objects used by every engine.
"""

from dataclasses import dataclass

from planner.market.market_data import MarketData
from planner.market.portfolio import Portfolio


@dataclass(slots=True)
class PlanningContext:

    assumptions: object
    market_data: MarketData
    portfolio: Portfolio