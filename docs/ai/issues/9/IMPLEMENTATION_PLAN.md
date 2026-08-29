# Issue #9 Implementation Plan — route-1bc C2-C3 +1V8 closure

## Base
- Branch: `agent/phase1-mainboard-schematic`
- Base SHA: `c6345ee0420ce5b5417c16f204ff4d2378f3df69`
- Accepted authority: route-1bb = 0 violations / 121 unconnected / 268 PASS

## Objective
Validate exactly one additional same-net copper connection on the far-right edge:

`C2.1/+1V8 (41.005,11.975)` → direct vertical `0.30 mm` F.Cu segment → `C3.1/+1V8 (41.005,13.475)`.

Expected result if valid: 0 violations / 120 unconnected / 268 PASS.

## Architecture
1. Reproduce accepted route-1bb.
2. Load the generated route-1bb board with pcbnew.
3. Validate exact C2/C3 references, values, pad nets, and pad coordinates.
4. Add exactly one 0.30 mm F.Cu segment on +1V8 from C2.1 to C3.1.
5. Refill zones/build connectivity and save route-1bc.
6. Run KiCad 9.0.9 DRC and the 268-node physical pin/net audit.
7. Assert exact scope, placement invariants, source geometry preservation, and frozen-interface preservation.
8. Upload evidence.
9. Formally accept only after independent Artifact inspection.

## Candidate selection
### Option A — C2.1 ↔ C3.1 +1V8
Selected. Straight 1.500 mm segment, no via, non-RF, non-PMIC, far board edge.

### Option B — J7 GND chain
Rejected for this increment due 0.5 mm-pitch signal-row geometry.

### Option C — RF/PMIC/I2C constrained items
Rejected because they are already frozen or geometry-gated.

## Geometry preflight
- C2.1 center: (41.005,11.975), pad size 0.46 x 0.40 mm.
- C3.1 center: (41.005,13.475), pad size 0.46 x 0.40 mm.
- Adjacent C2.2/C3.2 GND centers: x=41.645 mm.
- Proposed track width: 0.30 mm.
- Conservative lateral copper gap:
  - track right edge = 41.005 + 0.150 = 41.155
  - GND pad left edge = 41.645 - 0.230 = 41.415
  - gap ≈ 0.260 mm
- Current minimum clearance rule: 0.100 mm.
- This is preflight only; KiCad DRC is authoritative.

## Invariants
- C2/C3 remain 100nF.
- C2.1/C3.1 remain +1V8.
- C2.2/C3.2 remain GND.
- C2/C3 placement unchanged.
- Exactly one new F.Cu segment, zero vias.
- No component moves/rotations.
- All accepted route-1bb geometry otherwise unchanged.
- No RF or supplier-gated changes.
- No design-rule waiver, via-in-pad, or manufacturing-release claim.

## Verification
- Dedicated GitHub Actions workflow.
- KiCad version exactly 9.0.9.
- DRC: 0 violations / 120 unconnected.
- pin/net audit: PASS / 268.
- exact C2/C3 identity, nets, coordinates.
- exact 1 segment / 0 via scope.
- Artifact hashes independently checked.

## Rollback
Any failed hard gate rejects route-1bc. Accepted authority remains route-1bb.
