# Issue #10 Implementation Plan — route-1bd C3-C4 +1V8 closure

## Base
- Branch: `agent/phase1-mainboard-schematic`
- Base SHA: `7058994e3c5b8dea1296e413ee13ab90f646897b`
- Accepted authority: route-1bc = 0 violations / 120 unconnected / 268 PASS

## Objective
Validate exactly one additional same-net copper connection on the far-right edge:

`C3.1/+1V8 (41.005,13.475)` → direct vertical `0.30 mm` F.Cu segment → `C4.1/+1V8 (41.005,14.975)`.

Expected result if valid: 0 violations / 119 unconnected / 268 PASS.

## Architecture
1. Reproduce accepted route-1bc.
2. Load the generated route-1bc board with pcbnew.
3. Validate exact C3/C4 references, values, pad nets, and coordinates.
4. Add exactly one 0.30 mm F.Cu segment on +1V8 from C3.1 to C4.1.
5. Refill zones/build connectivity and save route-1bd.
6. Run KiCad 9.0.9 DRC and the 268-node physical pin/net audit.
7. Assert exact routing scope, placement invariants, accepted-baseline preservation, and frozen-interface preservation.
8. Upload evidence.
9. Formally accept only after independent Artifact inspection.

## Candidate selection
### Option A — C3.1 ↔ C4.1 +1V8
Selected. Straight 1.500 mm segment, no via, identical geometry class to accepted C2↔C3 route-1bc, non-RF, non-PMIC.

### Option B — C4.1 ↔ C302.1
Deferred because it is longer and non-collinear.

### Option C — J7 / RF / PMIC / I2C constrained items
Deferred due tighter signal geometry or existing explicit gates.

## Geometry preflight
- C3.1 center: (41.005,13.475), pad size 0.46 x 0.40 mm.
- C4.1 center: (41.005,14.975), pad size 0.46 x 0.40 mm.
- Adjacent C3.2/C4.2 GND centers: x=41.645 mm.
- Proposed track width: 0.30 mm.
- Conservative lateral copper gap: about 0.260 mm.
- Current minimum clearance: 0.100 mm.
- Executed KiCad DRC remains authoritative.

## Invariants
- C3/C4 remain 100nF.
- C3.1/C4.1 remain +1V8.
- C3.2/C4.2 remain GND.
- C3/C4 placement unchanged.
- Exactly one new F.Cu segment, zero vias.
- No component moves/rotations.
- Accepted route-1bc geometry otherwise unchanged.
- No RF or supplier-gated changes.
- No design-rule waiver, via-in-pad, or manufacturing-release claim.

## Verification
- Dedicated GitHub Actions workflow.
- KiCad exactly 9.0.9.
- DRC: 0 violations / 119 unconnected.
- pin/net audit: PASS / 268.
- exact C3/C4 identity, nets, coordinates.
- exact 1 segment / 0 via scope.
- Artifact hashes independently checked.

## Rollback
Any failed hard gate rejects route-1bd. Accepted authority remains route-1bc.
