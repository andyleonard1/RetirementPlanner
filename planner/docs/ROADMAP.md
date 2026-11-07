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

## Sprint 286 - RC4 Release Candidate Verification

- Completed full-suite validation: 1,560 passed, 2 skipped.
- Verified compilation and protected assumptions/golden-baseline JSON digests.
- Generated and reconciled a 476-file Sprint 286 release manifest.
- Passed package audit and release-evidence reconciliation.
- Recovery investigation reproduced the earlier recorded ZIP hash (`d6d26...`) in two separate build invocations from the reconstructed source, confirming repeatability in the current build environment.
- The later recorded hash (`76bb...`) remains unreproduced. Its origin and equivalence to the recovered archive are unconfirmed.
- The investigation is closed as an unresolved historical evidence discrepancy. Formal GitHub Release publication remains a separately authorised step.

## Sprint 287 - RC4 Release Evidence Reconciliation and Publication Readiness

- Reconcile the Sprint 286 release verification record with the merged GitHub history.
- Update the README and project status to identify Sprint 287 as the current checkpoint.
- Confirm the availability and integrity of the locally generated RC4 candidate artefacts.
- Review outstanding formal publication requirements.
- Produce a clear release-readiness recommendation.
- Keep GitHub Release publication and release tagging subject to separate explicit approval.
- No production financial calculation, assumptions or golden-baseline changes are in scope.
- Starting test baseline: 1,560 passed, 2 skipped.

## Sprint 288 - RC4 Hash Investigation Closure

- Trace the historical Sprint 286 archive hash discrepancy through Git history.
- Compare source and verification revisions, manifest contents and archive-building tools.
- Reconstruct the candidate archive and perform a second build invocation.
- Confirm repeatability of the recovered archive in the current build environment.
- Record the unresolved historical hash discrepancy and retain the recovered evidence.
- Keep formal release publication on hold pending a fresh, explicitly authorised release candidate.
