# Retirement Planner Architecture

## Design Philosophy

Retirement Planner is an engine-driven financial planning system.

The application follows a layered architecture.

Applications

↓

Planner

↓

Calculation Engines

↓

Analysis Engines

↓

Reports

---

## Principles

Planner orchestrates.

Engines calculate.

Reports present.

Configuration comes from Assumptions.

Business rules exist only once.

No engine writes reports.

No report performs calculations.