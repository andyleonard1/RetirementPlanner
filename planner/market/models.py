from dataclasses import dataclass


@dataclass(slots=True)
class MarketYear:

    year: int

    equity: float

    bonds: float

    inflation: float