# Issue #22 — route-1bp Phase A implementation plan

## Objective

Start from the formally accepted route-1bo authority and identify at most one next ordinary, non-frozen routing family without modifying the PCB.

Accepted source: **route-1bo = 0 KiCad 9.0.9 DRC violations / 109 unconnected / 268-node audit PASS**.

## Source of truth

- `docs/pcb-route-r13-1bo-validation.json`
- `tools/reproduce-route1bo-accepted.sh`
- `.ai/intelligence/mainboard-routing-safety-invariants.md`
- `.ai/decisions/pcb-routing-acceptance-authority.md`
- `.ai/rules/validated.md`
- Issue #22
- PR #2

## Phase A1

1. Reproduce route-1bo using the accepted reproducer.
2. Fail closed unless the source is exactly 0 / 109 / 268 PASS.
3. Record the actual 109-item ratsnest.
4. Reuse `tools/probe-pcb-r13-route1bn-max4-coarse.py` as the parameterized read-only screen engine.
5. Supply the route-1bo PCB/report paths and `--expected-unconnected 109`.
6. Keep the established frozen/deferred reference/net exclusions.
7. Search L, HVH/VHV, HVHV/VHVH families at 0.30 mm provisional F.Cu width and 0.25 mm coarse grid.
8. Require conservative unrelated/unnetted copper clearance >= 0.100 mm.
9. Record every passing candidate and exclusion summary in an Artifact.
10. Assert `board_modified == false` and independently verify the downloaded Artifact.

## Semantic review

Geometry is only a filter. Review all numerical passes against frozen scope, electrical semantics, target identity, and whether the endpoint is an actual electrical pad/track rather than a mechanical or ambiguous element.

Select at most one family. If no safe ordinary candidate survives, stop Phase A without materializing copper.

## Phase A2

Only after semantic selection, create a candidate-specific 0.05 mm read-only refine. Do not generalize or materialize multiple candidates.

## Phase B

Only one selected/refined family may proceed to exact identity probe and materialization. Acceptance remains:
- KiCad 9.0.9 DRC = 0
- exact 109 -> 108 ratsnest decrement
- 268-node audit PASS
- exact intended physical delta only
- zero footprint moves/rotations
- no rule waiver or via-in-pad
- frozen/supplier-gated scope preserved
- Artifact verification plus independent verification

route-1bo remains authority until every Phase B gate passes. Release remains **NOT_FOR_GERBER**.

## Pre-Implementation Review

- Requirements coverage: PASS
- Architecture/duplication: PASS — reuse accepted reproducer and parameterized screen engine.
- Risk/regression/security: PASS WITH HARD GATES — no PCB mutation in Phase A; numerical geometry cannot release frozen scope.
