# Engine Catalogue

This document is the quick reference for the main engine responsibilities.

| Component | Responsibility | Typical input | Output |
|---|---|---|---|
| `RetirementPlanner` | Orchestrates a complete plan | Assumptions | `PlannerResult` |
| `TimelineEngine` | Builds the retirement-year timeline | Assumptions | Timeline |
| `PensionEngine` | Projects pension withdrawals and growth | Timeline | Timeline |
| `StatePensionEngine` | Projects State Pension income | Timeline | Timeline |
| `SavingsEngine` | Projects cash savings | Timeline | Timeline |
| `ISAEngine` | Projects ISA contributions/growth | Timeline | Timeline |
| `TaxEngine` | Calculates income tax | Timeline/year data | Tax values/timeline updates |
| `WithdrawalEngine` | Applies withdrawal rules | Timeline | Timeline |
| `CashflowEngine` | Evaluates income and spending cash flow | Timeline | Timeline |
| `InflationEngine` | Applies inflation assumptions | Assumptions/timeline | Timeline values |
| `StrategyEngine` | Applies withdrawal strategy logic | Timeline/assumptions | Strategy/timeline |
| `SummaryEngine` | Produces end-of-plan statistics | Completed timeline | Summary |
| `ScenarioManager` | Builds and compares scenarios | Scenarios | Comparisons/decisions |
| `RetirementAgeScoringEngine` | Scores retirement-age options | Scenario comparisons | Scores |
| `RecommendationEngine` | Produces recommendation data | Comparisons/trade-offs | Recommendations |
| `DecisionEngine` | Produces decision analysis | Planner/scenario data | Decision result |
| `RiskEngine` | Assesses plan risk | Plan/summary data | Risk result |
| `GoalEngine` | Evaluates planning goals | Plan data | Goal result |
| `OptimisationEngine` | Shared optimisation traversal | Optimisation inputs | Optimisation result |
| `MonteCarloEngine` | Runs probabilistic simulations | Assumptions/plan | Simulation results |
| `SensitivityRunner` | Runs assumption variations | Sensitivity grid | Sensitivity results |
| `ChartEngine` | Creates report charts | Timeline | Chart files |

## Contract guidance

Where a component crosses a stable architectural boundary, prefer the contracts in `planner/contracts.py` rather than coupling consumers to a concrete implementation.

## Reporting guidance

Reports should consume summaries, decision objects, recommendation objects and prepared chart files. They should not reproduce calculation logic.
