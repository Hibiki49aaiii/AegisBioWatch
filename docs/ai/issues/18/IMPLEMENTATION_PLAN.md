# Issue #18 Implementation Plan — route-1bl from route-1bk

## Base
- Branch: `agent/phase1-mainboard-schematic`
- Base accepted/archive SHA: `038bb5c349d0e8a823c152539094e74827705768`
- Accepted electrical authority: route-1bk = 0 violations / 113 unconnected / 268 PASS
- Accepted Artifact: 9715915878
- Accepted PCB SHA-256: `283217e6a0ff89355999c0bc2fa5330d5348811caaea97deff6c8b27295a9ed8`

## Phase A — completed
1. Reproduced route-1bk at 0 / 113 / 268 PASS.
2. Screened the actual current 113-item ratsnest.
3. Rejected C301.1/+1V8 after 2,884 max-four-segment paths produced 0 legal routes; best modeled clearance was 0.074999 mm.
4. Rejected +1V8→R403 because modeled clearance was 0.099999 mm.
5. Rejected NRF_RESET_N candidate because its route approached frozen C11/RF_B context.
6. Evaluated VSYS→R106.1 with R106.2/LDO2_IN treated as unrelated copper.
7. Coarse R106 screen: one legal route, 0.125 mm clearance.
8. 0.05 mm local refine: 88 candidates / 16 legal; selected screen path with 0.184166 mm minimum clearance.
9. Removed overlap with the already-existing VSYS segment before materialization.

Selected effective new copper:
- `(7.350,28.250)`
- → `(7.200,28.250)`
- → `(7.200,26.400)`
- → `(5.270826,26.400)`
- → `R106.1/VSYS (5.270826,25.865834)`

Scope:
- 4 F.Cu segments
- 0 vias
- width 0.30 mm
- segment lengths 0.150 / 1.850 / 1.929174 / 0.534166 mm
- total new copper 4.463340 mm
- independent limiting clearance to R106.2/LDO2_IN = 0.184166 mm

## Phase B — executed
1. Reproduced route-1bk.
2. Re-ran local refine inside the validation workflow.
3. Ran exact PCB-identity/net/coordinate/path probe.
4. Materialized only the selected four VSYS segments.
5. Compared route-1bk and route-1bl physical track/via/footprint state:
   - added tracks = exactly 4 expected VSYS segments;
   - removed tracks = 0;
   - added vias = 0;
   - all footprint position/rotation states unchanged;
   - existing VSYS source track preserved exactly once.
6. Ran KiCad 9.0.9 DRC.
7. Required exact 113 → 112 unconnected decrement.
8. Ran 268-node physical pin/net audit.
9. Packaged evidence Artifact with SHA256SUMS.
10. Downloaded Artifact in a second Actions job and re-verified hashes/JSON gates.
11. Independently downloaded and re-verified ZIP SHA, SHA256SUMS, DRC, audit, probe, scope and PCB SHA.

Executed acceptance authority:
- run 33339645685
- validate job 99332825730 — SUCCESS
- verify-artifact job 99333473586 — SUCCESS
- result: 0 violations / 112 unconnected / 268 PASS

## Invariants
- No rule reduction.
- No via-in-pad.
- No component move/rotation.
- No RF/nRF-internal/supplier-gated changes.
- R106.2/LDO2_IN remains deferred and unrouted.
- Existing VSYS source segment `(8.9875,28.25) → (7.35,28.25)` remains unchanged.
- CHG_5V and SYS_I2C_SCL geometry-gated routing remain untouched.
- Release remains NOT_FOR_GERBER.
