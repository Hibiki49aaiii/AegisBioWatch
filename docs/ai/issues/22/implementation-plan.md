# Issue #22 — route-1bp implementation plan

Status: active  
Base Commit SHA: `e7b9d1dc8dfe5d37f4367392291d9e3e2c49310f`  
Accepted source: **route-1bo = 0 / 109 / 268 PASS**  
Release: **NOT_FOR_GERBER**

## Goal

Find at most one next ordinary, non-frozen isolated routing closure from the accepted route-1bo state without changing copper during Phase A.

## Architecture

- Reproduce `route-1bo` using `tools/reproduce-route1bo-accepted.sh`.
- Reuse the parameterized `tools/probe-pcb-r13-route1bn-max4-coarse.py` engine with explicit route-1bo source PCB/report paths and expected unconnected count 109.
- Keep Phase A1 and A2 read-only.
- If a candidate survives semantic review, create a candidate-specific 0.05 mm refine probe.
- Only then create a candidate-specific Phase B materializer and validation workflow.

## Scope

In scope:
- 109-item executed ratsnest inventory.
- Existing frozen/deferred semantic exclusions.
- L, HVH/VHV, HVHV/VHVH F.Cu coarse screening at 0.30 mm width.
- Conservative clearance gate >= 0.100 mm.
- One candidate maximum.

Out of scope:
- U1 high-density and listed frozen/supplier/RF regions.
- rule reduction, via-in-pad, footprint moves/rotations.
- production/Gerber/manufacturing release.

## Risks

- A geometrically good candidate may be semantically frozen.
- Unnetted/mechanical copper may appear as the nearest obstacle and requires identity review.
- A lower ratsnest count is not acceptance without exact 0 DRC / 268-node / physical-delta gates.

## Human Understanding

Phase A is only a measurement pass. It does not create route-1bp copper. route-1bo remains authority until one Phase B candidate executes every acceptance gate.

## Verification Plan

1. KiCad 9.0.9 installed and pinned.
2. Accepted route-1bo reproduces at 0 / 109 / 268 PASS.
3. Inventory contains exactly 109 unconnected items.
4. Screen output reports `board_modified=false`.
5. Downloaded Artifact SHA256SUMS and JSON gates pass.
6. Inspect passing candidates semantically before any refine/materialization.

## Implementation Checklist

- [x] Issue #22 created with base authority.
- [x] Phase A1 workflow designed from accepted-source pattern.
- [ ] Execute Phase A1 workflow.
- [ ] Inspect Artifact and candidate exclusions.
- [ ] Select at most one candidate after semantic review.
- [ ] Run 0.05 mm refine only if justified.
