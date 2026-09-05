# Issue #17 Implementation Plan — route-1bk from route-1bj

## Base
- Branch: `agent/phase1-mainboard-schematic`
- Base accepted/archive SHA: `5e2cc80c83d63e10bf76c78eb7f7956ccc627e14`
- Accepted electrical authority: route-1bj = 0 violations / 114 unconnected / 268 PASS
- Accepted Artifact: 9713740190
- Accepted PCB SHA-256: `64b3f16ad984c45fb995c2694c3714d7200db9fb07f21be7fcb391aa9e04b6d8`

## Phase A1 — current-state ordinary screen
- run 33253752823 / job 99103802453;
- Artifact 9715225538;
- ZIP SHA-256 `e7407646b496b8d531e0be98b2be5be5ad701d472541cdc0cb33d01cb704988a`;
- 13 ordinary candidates evaluated / 3 geometry pass.

Passes:
1. C305.1/VSYS_HAPTIC → C304.1/VSYS_HAPTIC
   - VHV, 3 segments, 11.960 mm, clearance 0.125 mm.
2. D101.2/DOCK_5V_RAW → D102.1/DOCK_5V_RAW
   - longer input-power path; not selected.
3. +1V8 track → R403.1
   - 0.099999 mm model result; rejected as below engineering threshold.

## Phase A2 — expanded ordinary screen
- run 33254148238 / job 99104830838;
- Artifact 9715340474;
- ZIP SHA-256 `405c4a42d2069a27f3fa2030ba19109c6af15d41a5d21c99d695146f49370737`;
- endpoint window expanded to 18 mm and lane margin to ±6 mm;
- no better ordinary low-risk candidate emerged.
- NRF_RESET_N geometric pass was rejected because its nearest copper is C11/RF_B and RF routing remains frozen.

## Phase A3 — targeted low-current multibend
Targets:
- R502↔R501 / CHG_SENSE_GATE;
- R501↔Q501 / CHG_SENSE_GATE;
- U4↔R303 / HAPTIC_TRIG.

Optimized coarse run:
- run 33255144664 / job 99107430649;
- Artifact 9715676488;
- ZIP SHA-256 `83c8b1654ec65d2806da2993a650af208266a28663cc52fc8bdd0b831d29be71`;
- 0.25 mm grid, ±3 mm margin, max 4 segments;
- all three targets: **0 passing paths**.

The earlier exhaustive 0.10 mm run was retired because the Cartesian four-segment search was computationally excessive and had not produced an acceptance result.

## Selected Phase B candidate
**C305.1/VSYS_HAPTIC → C304.1/VSYS_HAPTIC**

Exact path:
- C305.1: `(6.805,22.335)`
- bend: `(6.805,21.650)`
- bend: `(16.005,21.650)`
- C304.1: `(16.005,23.725)`

Geometry:
- family VHV;
- 3 segments;
- segment lengths 0.685 / 9.200 / 2.075 mm;
- total 11.960 mm;
- F.Cu width 0.30 mm;
- zero vias;
- conservative minimum unrelated-copper clearance 0.125 mm;
- nearest unrelated copper: GND via `(12.750,22.225)`, size 0.60 mm.

Independent local gap:
- vertical separation from horizontal centerline to via center = 0.575 mm;
- candidate half-width = 0.150 mm;
- via radius = 0.300 mm;
- copper clearance = **0.125 mm**.

## Power-path review
VSYS_HAPTIC context:
- C305 = 1uF;
- C304 = 100nF;
- U4 = DRV2605LDGSR, pin10 = VSYS_HAPTIC;
- R305 = 0R / FB OPTION, pad2 = VSYS_HAPTIC, pad1 = VSYS.

Current board stack-up:
- F.Cu thickness = **0.018 mm (18 µm)**.

Approximate candidate DC resistance using copper resistivity 1.724e-8 Ωm:
- 11.96 mm × 0.30 mm × 18 µm ≈ **38 mΩ**.
- This is a resistance sanity check, not a thermal/current-limit certification.

TI DRV2605L datasheet context:
- VDD supports 2–5.2 V operation.
- TI layout guidance recommends 75–100 µm at solder-pin escape, then increasing width for improved current flow.
- 0.30 mm is wider than the pin-escape width; exact KiCad DRC and later full haptic power/actuator signoff remain required.
- Official reference: https://www.ti.com/document-viewer/DRV2605L/datasheet

DOCK_5V_RAW remains deferred because it is a primary input-power path and should be routed under coordinated current/ESD/dock design rather than as a generic ratsnest decrement.

## Phase B
1. Reproduce route-1bj.
2. Re-run exact current-state route-1bk screen.
3. Execute exact C305/C304/U4/R305 identity/net/coordinate/path probe.
4. Materialize only the documented three-segment 0.30 mm F.Cu route.
5. Run KiCad 9.0.9 DRC.
6. Require exact 114 → 113 unconnected decrement.
7. Run 268-node physical pin/net audit.
8. Verify exact scope, no placement changes, no RF/supplier changes.
9. Upload evidence Artifact.
10. Download Artifact in a second job and re-verify SHA256SUMS and JSON gates.
11. Independently download/re-verify before formal acceptance.
12. Commit acceptance/rejection evidence and reproducer.
13. Archive/retire temporary workflow.

## Invariants
- route-1bj remains authority unless all Phase B gates pass.
- No rule reduction.
- No via-in-pad.
- No component move/rotation.
- No RF/nRF-internal/supplier-gated changes.
- C305.2/GND and C304.2/GND remain untouched.
- U4 pin10 and R305 VSYS_HAPTIC endpoints are not routed in this increment.
- CHG_5V and SYS_I2C_SCL geometry-gated routing remain untouched.
- Release remains NOT_FOR_GERBER.
