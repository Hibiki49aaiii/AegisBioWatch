# Issue #17 Implementation Plan — route-1bk from route-1bj

## Base
- Branch: `agent/phase1-mainboard-schematic`
- Base accepted/archive SHA: `5e2cc80c83d63e10bf76c78eb7f7956ccc627e14`
- Accepted electrical authority: route-1bj = 0 violations / 114 unconnected / 268 PASS
- Accepted Artifact: 9713740190
- Accepted PCB SHA-256: `64b3f16ad984c45fb995c2694c3714d7200db9fb07f21be7fcb391aa9e04b6d8`

## Phase A
1. Reproduce route-1bj with `tools/reproduce-route1bj-accepted.sh`.
2. Assert source DRC = 0 / 114 and physical audit = 268 PASS.
3. Parse the current 114-item DRC output.
4. Exclude U1/J7/RF/nRF-internal/supplier-gated/PMIC-switch/CHG_5V/LDO2_IN/SYS_I2C_SCL/duplicate-terminal items.
5. Search ordinary endpoint pairs <= 12 mm using L-HV / L-VH / HVH / VHV with:
   - 0.05 mm lane grid;
   - ±3.0 mm lane margin;
   - provisional 0.30 mm F.Cu width.
6. Require conservative different-net/unnetted copper clearance >= 0.100 mm.
7. Rank by endpoint semantics, segment count, path length, clearance, then functional risk.
8. For pad↔track candidates, prove the exact target segment/intersection before materialization.
9. Review power-path/current implications before selecting VSYS or DOCK_5V_RAW.

## Phase B
For one selected candidate:
1. Create exact read-only identity/net/coordinate/path probe.
2. Materialize only the documented route.
3. Run KiCad 9.0.9 DRC.
4. Require exact 114 → 113 unconnected decrement.
5. Run 268-node physical pin/net audit.
6. Verify exact scope, no placement changes, no frozen-interface changes.
7. Upload evidence Artifact.
8. Download Artifact in a second job and re-verify SHA256SUMS and JSON gates.
9. Independently download/re-verify before formal acceptance.
10. Commit acceptance/rejection evidence and reproducer.
11. Archive/retire temporary workflows.

## Invariants
- route-1bj remains authority unless all Phase B gates pass.
- No rule reduction.
- No via-in-pad.
- No component move/rotation.
- No RF/nRF-internal/supplier-gated changes.
- CHG_5V and SYS_I2C_SCL geometry-gated routing remain untouched.
- Release remains NOT_FOR_GERBER.
