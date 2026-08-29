# Issue #18 Implementation Plan — route-1bl from route-1bk

## Base
- Branch: `agent/phase1-mainboard-schematic`
- Base accepted/archive SHA: `038bb5c349d0e8a823c152539094e74827705768`
- Accepted electrical authority: route-1bk = 0 violations / 113 unconnected / 268 PASS
- Accepted Artifact: 9715915878
- Accepted PCB SHA-256: `283217e6a0ff89355999c0bc2fa5330d5348811caaea97deff6c8b27295a9ed8`

## Phase A
1. Reproduce route-1bk with `tools/reproduce-route1bk-accepted.sh`.
2. Assert source DRC = 0 / 113 and physical audit = 268 PASS.
3. Parse the current 113-item DRC output.
4. Exclude U1/J7/RF/nRF-internal/supplier-gated/PMIC-switch/CHG_5V/LDO2_IN/SYS_I2C_SCL/BIO_SW/DISP_SW/DOCK_5V_RAW/duplicate-terminal items.
5. Search ordinary endpoint pairs <= 12 mm using L-HV / L-VH / HVH / VHV with:
   - 0.05 mm lane grid;
   - ±3.0 mm lane margin;
   - provisional 0.30 mm F.Cu width.
6. Require conservative different-net/unnetted copper clearance >= 0.100 mm.
7. Rank by endpoint semantics, segment count, path length, clearance, then functional risk.
8. Prefer C301.1/+1V8 → accepted +1V8 rail if legal.
9. For any pad↔track winner, prove the exact target track segment and landing point before materialization.

## Phase B
For one selected candidate:
1. Create exact read-only identity/net/coordinate/path probe.
2. Materialize only the documented route.
3. Run KiCad 9.0.9 DRC.
4. Require exact 113 → 112 unconnected decrement.
5. Run 268-node physical pin/net audit.
6. Verify exact scope, no placement changes, no frozen-interface changes.
7. Upload evidence Artifact.
8. Download Artifact in a second job and re-verify SHA256SUMS and JSON gates.
9. Independently download/re-verify before formal acceptance.
10. Commit acceptance/rejection evidence and reproducer.
11. Archive/retire temporary workflows.

## Invariants
- route-1bk remains authority unless all Phase B gates pass.
- No rule reduction.
- No via-in-pad.
- No component move/rotation.
- No RF/nRF-internal/supplier-gated changes.
- C301.2/GND must remain untouched if C301 is selected.
- Accepted R404/R302 +1V8 route geometry must remain unchanged except for the intentional same-net landing.
- CHG_5V, LDO2_IN and SYS_I2C_SCL geometry-gated routing remain untouched.
- Release remains NOT_FOR_GERBER.
