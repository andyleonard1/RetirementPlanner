# Roadmap

## RC2 — Architecture Stabilisation

Current release track.

Completed areas include:

- engine-driven planner architecture
- scenario comparison
- standard result objects
- optimisation framework consolidation
- logging consistency
- typed engine contracts
- reporting migration

Remaining RC2 focus:

- documentation consolidation
- integration coverage
- removal of obsolete compatibility paths where safe

## RC3 — Optimisation Suite

- expand optimisation beyond the current prototype
- **compare optimisation strategies — Sprint 51 complete**
- improve explanation of optimisation outcomes
- **integrate optimisation decision support into recommendation/report pipeline — Sprint 54 complete**

## RC4 — Historical Replay

- historical market scenarios
- deterministic replay of market sequences
- comparison of historical outcomes

## RC5 — Professional Reporting

- richer adviser reporting
- clearer assumptions and methodology sections
- expanded scenario and sensitivity presentation

## RC6 — User Interface

- interactive planning workflow
- scenario controls
- visual comparison of outcomes

## Version 2.0 — Production Release

Production hardening, documentation, integration coverage and release validation.

## Version 3.0 — Advanced Financial Planning Platform

Longer-term expansion into a broader financial-planning platform.

## RC3 — Sprint 53

- Added read-only optimisation decision support.
- Decision support interprets policy capacity differences and materiality without changing financial calculations.

## RC4 — Sprint 62

- Added isolated sequence-of-returns risk analysis.
- Compare identical annual return sets in different orders while modelling withdrawals.
- Keep deterministic retirement engines unchanged.
- Protected Sprint 61 baseline: 241 tests passing.
