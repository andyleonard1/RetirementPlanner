"""
Decision Engine

Runs all available strategies and recommends the best one.
"""

from planner.scenario_engine import ScenarioEngine
from planner.risk_engine import RiskEngine

class DecisionEngine:

    def __init__(self):
        self.engine = ScenarioEngine()

    def run(self):

        scenarios = self.engine.compare_strategies()

        #
        # Rank by ending assets
        #
        scenarios.sort(
            key=lambda s: s["summary"]["ending_assets"],
            reverse=True,
        )

        best = scenarios[0]
        risk = RiskEngine().analyse(best["timeline"])
        runner_up = scenarios[1] if len(scenarios) > 1 else None

        return {

        "recommended": best["name"],

        "summary": best["summary"],

        "runner_up": runner_up,

        "all": scenarios,

        "risk": risk,

}
        