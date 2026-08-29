# Issue #16 Implementation Plan — route-1bj from route-1bi

## Base
- Branch: `agent/phase1-mainboard-schematic`
- Base accepted/archive SHA: `df35a6cf0b82c6234024afa0f5de4764971bd733`
- Accepted electrical authority: route-1bi = 0 violations / 115 unconnected / 268 PASS
- Accepted Artifact: 9712848520
- Accepted PCB SHA-256: `9e513dc10b0cf16006bebcf60bf925e78740bbdd124811852b2703e45f1fd1ca`

## Phase A
1. Reproduce route-1bi with `tools/reproduce-route1bi-accepted.sh`.
2. Assert source DRC = 0 / 115 and physical audit = 268 PASS.
3. Parse the **current** 115-item DRC output rather than reusing route-1bg candidate ordering.
4. Exclude U1/J7/RF/supplier-gated/PMIC-switch/CHG_5V/LDO2_IN/SYS_I2C_SCL/duplicate-terminal items.
5. Search ordinary endpoint pairs <= 12 mm with:
   - L-HV / L-VH,
   - HVH,
   - VHV,
   - 0.25 mm lane grid,
   - ±3.0 mm local search margin,
   - 0.30 mm F.Cu provisional width.
6. Require conservative different-net/unnetted copper clearance >= 0.100 mm.
7. Rank passing routes by endpoint semantics, segment count, total path length, then clearance.
8. Review functional meaning before selecting the winner.

## Phase B
For one selected candidate:
1. Create exact read-only identity/net/coordinate/path probe.
2. Materialize only the documented route.
3. Run KiCad 9.0.9 DRC.
4. Require exact 115 → 114 unconnected decrement.
5. Run 268-node physical pin/net audit.
6. Verify exact scope, no placement changes, no frozen-interface changes.
7. Upload evidence Artifact.
8. Download Artifact in a second job and re-verify SHA256SUMS and JSON gates.
9. Independently download/re-verify before formal acceptance.
10. Commit acceptance/rejection evidence and reproducer.
11. Archive/retire temporary workflows.

## Invariants
- route-1bi remains authority unless all Phase B gates pass.
- No rule reduction.
- No via-in-pad.
- No component move/rotation.
- No RF/supplier-gated changes.
- Release remains NOT_FOR_GERBER.
