# Issue #11 Implementation Plan — route-1be C4-C302 +1V8

## Base
- Branch: `agent/phase1-mainboard-schematic`
- Base SHA: `8fb9fe94b36f3a2f0ebdafbff2252b860913cde6`
- Accepted authority: route-1bd = 0 violations / 119 unconnected / 268 PASS

## Objective
Determine and validate the safest standard-rule +1V8 connection between C4.1 and C302.1.

This is intentionally split into two phases because the path is longer and non-collinear.

## Phase A — Read-only geometry probe
1. Reproduce accepted route-1bd.
2. Gate source at 0 / 119 / 268 PASS.
3. Load the route-1bd PCB with pcbnew without saving/modifying it.
4. Record:
   - C4 and C302 values, footprint bbox, rotation;
   - all pad numbers/nets/positions/sizes/bboxes;
   - pads, tracks and vias intersecting a conservative right-edge corridor `x=39.5..42.3, y=14.0..20.3`.
5. Emit JSON evidence and upload it.
6. Select routing Option A/B/C from executed geometry.

## Phase B — Candidate routing
Only after Phase A:
- Option A: minimal F.Cu edge-corridor route if clean.
- Option B: standard through-via layer transition only if materially cleaner.
- Option C: defer/reject if neither is clean.

Candidate acceptance requires executed KiCad 9.0.9:
- 0 rule violations;
- deterministic expected unconnected count (nominally 118);
- 268-node pin/net audit PASS;
- exact copper scope;
- no placement/RF/supplier-gated change.

## Invariants
- C4 remains 100nF; C302 remains 1uF.
- C4.1/C302.1 remain +1V8.
- C4.2/C302.2 remain GND.
- route-1bd geometry is immutable except explicit candidate copper.
- C302 accepted GND escape remains unchanged.
- no rule reduction, via-in-pad, component move/rotation or manufacturing claim.

## Rollback
If the probe shows a constrained corridor, or candidate DRC/audit fails, route-1be is rejected/deferred and route-1bd remains authoritative.
