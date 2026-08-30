# Issue #19 Implementation Plan — route-1bm from route-1bl

## Base
- Branch: `agent/phase1-mainboard-schematic`
- Base accepted/archive SHA: `228fea4698bc661dd6f052cbc6cd9aefa8068690`
- Accepted electrical authority: route-1bl = 0 violations / 112 unconnected / 268 PASS
- Accepted Artifact: 9740198510
- Accepted PCB SHA-256: `01db4298b0b713ba0c7fb224bee0971110b19b93a79d8f574c3a8f6efe57d7eb`

## Phase A1 — current-state broad screen
1. Reproduce route-1bl with `tools/reproduce-route1bl-accepted.sh`.
2. Assert source DRC = 0 / 112 and physical audit = 268 PASS.
3. Parse the reproduced 112-item ratsnest.
4. Exclude U1/J7/RF/nRF-internal/supplier-gated/PMIC-switch/CHG_5V/LDO2_IN/SYS_I2C_SCL/BIO_SW/DISP_SW/DOCK_5V_RAW/duplicate-terminal items.
5. Search ordinary endpoints <= 18 mm using:
   - L-HV / L-VH;
   - HVH / VHV;
   - 0.05 mm lane grid;
   - ±6.0 mm lane margin;
   - provisional 0.30 mm F.Cu width.
6. Require conservative unrelated/unnetted copper clearance >= 0.100 mm.
7. Record every pass and rejection reason.
8. Do not materialize in A1.

## Phase A2 — max-four-segment targeted screen
If A1 yields no semantically acceptable winner:
1. Choose only ordinary candidates surviving semantic exclusions.
2. Search HVHV/VHVH up to four segments on a 0.25 mm coarse grid with ±4 mm local margin.
3. Reject any path below 0.100 mm without rounding/waiver.
4. Refine any credible family at 0.05 mm before selection.

## Phase B
For one selected candidate:
1. exact PCB identity/net/coordinate/path probe;
2. exact target/source track identity where applicable;
3. materialize only documented copper;
4. before/after physical delta audit;
5. KiCad 9.0.9 DRC;
6. require exact 112 → 111 unconnected decrement;
7. 268-node physical pin/net audit PASS;
8. Artifact + SHA256SUMS;
9. second-job downloaded Artifact verification;
10. independent Artifact re-verification;
11. formal evidence/reproducer;
12. archive/retire temporary workflows;
13. Issue/PR update.

## Invariants
- route-1bl remains authority until all Phase B gates pass.
- No rule reduction.
- No via-in-pad.
- No component move/rotation.
- No RF/nRF-internal/supplier-gated changes.
- R106.2/LDO2_IN remains deferred.
- CHG_5V and SYS_I2C_SCL geometry-gated routes remain deferred.
- Existing accepted route-1bl VSYS geometry remains unchanged unless a same-net landing is explicitly proven.
- Release remains NOT_FOR_GERBER.
