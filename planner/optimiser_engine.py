"""
British-spelling compatibility entry point.

The canonical implementation is OptimisationEngine in
planner.optimisation_engine.
"""

from planner.optimisation_engine import OptimisationEngine


OptimiserEngine = OptimisationEngine

__all__ = ["OptimiserEngine"]
