# Issue #20 Implementation Plan — route-1bn from route-1bm

## Base
- Branch: `agent/phase1-mainboard-schematic`
- Base repository HEAD: `eb3c48c43844dbfdac59027105d777e7e6178d34`
- Accepted electrical authority: route-1bm = 0 violations / 111 unconnected / 268 PASS
- Accepted Artifact: 9762571974
- Accepted PCB SHA-256: `3f801870c08fd7729ce54eb51789c710690b0248efd1689e6d8e2f679bb705c4`

## Phase A1 — current route-1bm coarse screen
1. Reproduce route-1bm with `tools/reproduce-route1bm-accepted.sh`.
2. Assert source DRC = 0 / 111 and physical audit = 268 PASS.
3. Parse the actual 111-item ratsnest.
4. Exclude U1/J7/RF/nRF-internal/supplier-gated/PMIC-switch/CHG_5V/LDO2_IN/SYS_I2C_SCL/BIO_SW/DISP_SW/DOCK_5V_RAW/duplicate-terminal items.
5. Search ordinary endpoints <= 12 mm using L, HVH/VHV, and HVHV/VHVH on a 0.25 mm coarse grid with ±4 mm margin.
6. Use provisional 0.30 mm F.Cu width and require conservative unrelated/unnetted copper clearance >= 0.100 mm.
7. Record every pass and exclusion reason.
8. Do not materialize in Phase A1.

## Phase A2
If a semantically acceptable family exists:
1. inspect exact source/target identities and topology;
2. choose exactly one family;
3. refine only that family at 0.05 mm;
4. keep the board unchanged.

## Phase B
For one selected candidate:
1. exact PCB identity/net/coordinate/path probe;
2. exact source/landing identity;
3. materialize only documented copper;
4. before/after physical delta audit;
5. KiCad 9.0.9 DRC;
6. require exact 111 -> 110 unconnected decrement;
7. 268-node physical pin/net audit PASS;
8. Artifact + SHA256SUMS;
9. downloaded Artifact verification;
10. independent Artifact verification;
11. evidence + accepted reproducer;
12. archive/retire temporary workflows;
13. Issue/PR update.

## Invariants
- route-1bm remains authority until every Phase B gate passes.
- No rule reduction or via-in-pad.
- No component move/rotation.
- Frozen RF/nRF-internal/supplier-gated interfaces remain untouched.
- CHG_5V, LDO2_IN, SYS_I2C_SCL, DOCK_5V_RAW remain deferred.
- Historical failed C301/R403 families are not considered safe without fresh exact proof.
- Release remains NOT_FOR_GERBER.
