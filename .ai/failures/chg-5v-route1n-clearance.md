# CHG_5V route-1n clearance below rule

Confidence: medium  
Recorded: 2026-08-20

## Context

The historical route-1n attempt tried to advance the `CHG_5V` connection during the Phase 1 Main Board routing series.

## Attempt

Use the tested route-1n geometry to close `CHG_5V`.

## Why it seemed plausible

It reduced routing incompleteness and was a direct candidate for advancing the ratsnest.

## Why it failed

PR #2 records an actual clearance of **0.0669 mm** where **0.1000 mm** was required. No rule waiver was accepted, so the route was rejected rather than weakening the design rule.

## Evidence

- PR #2, `Historical exception remains`: route-1n `REJECTED`, `CHG_5V` clearance 0.0669 mm vs 0.1000 mm required, no waiver.
- PR #2 current frozen/geometry-gated section keeps `CHG_5V` rejected/deferred pending coordinated PMIC-side refinement.

The original raw route-1n DRC Artifact was not re-opened during this bootstrap, so confidence is medium rather than high.

## Better approach

Keep `CHG_5V` deferred until a coordinated PMIC-side geometry refinement satisfies normal rules. Do not lower clearance requirements merely to reduce the unconnected count.

## Applicability

Any future attempt to revisit `CHG_5V` on the current routing lineage. Re-run current KiCad DRC against any new geometry rather than assuming the historical failure dimensions still apply.
