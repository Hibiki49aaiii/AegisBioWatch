# Human Understanding — Issue #20

## Why route-1bn must start from route-1bm
route-1bm closed R305.2/VSYS_HAPTIC to U4.10/VSYS_HAPTIC and reduced the executed ratsnest from 112 to 111. Therefore all route-1bl candidate rankings are stale.

The accepted route-1bm evidence records:
- 0 KiCad DRC violations;
- 111 unconnected items;
- 268-node physical pin/net audit PASS;
- exactly four 0.30 mm F.Cu segments and zero vias;
- no component move/rotation;
- no frozen-interface mutation.

## What remains excluded
The next increment must still avoid U1 high-density closures, J7, RF/nRF-internal nets and passives, J3/J5/J6 supplier-gated interfaces, CHG_5V, LDO2_IN, SYS_I2C_SCL, PMIC switch nets, DOCK_5V_RAW, and default-deferred BIO_SW/DISP_SW.

## Screening rule
Phase A is read-only. It uses the actual reproduced route-1bm board. Different-net and unnetted copper are obstacles; same-net copper is context. Numerical path clearance is only a screening result, not acceptance.

DRC representative indices/descriptions can change after reproduction. Exact pad/track identity and semantic context must be proven before materialization.

## Rollback
Any failed source gate, screen, refine, exact probe, DRC, 111->110 decrement, audit, scope, or Artifact integrity gate leaves route-1bm unchanged as the accepted authority.

Manufacturing status remains NOT_FOR_GERBER.


## Phase A1 outcome — 2026-09-01
The executed current route-1bm full screen (run 33408592046) reproduced 0 / 111 / 268 PASS, kept the board unchanged, evaluated 9 ordinary candidates, and produced exactly two numerical passes.

- J8.1/+1V8 -> +1V8 track: 0.4397 mm modeled clearance, but the limiting obstacle is an unidentified/blank J8 pad. It remains HOLD and is not selected.
- +1V8 source track @ (41.005,14.975) -> R403.1/+1V8 @ (40.255,25.975): VHVH, 13.260 mm, 0.260 mm modeled clearance to C4.2/GND. It is selected as the only Phase A2 refine family.
- The R403 family selected here is not the rejected Phase A1 three-segment route that measured 0.099999 mm. It is the separately proven four-segment family.
- Focused run 33409352266 plus downloaded-Artifact verification independently confirmed both current numerical results.
- No copper was materialized. route-1bm remains the accepted authority.

Phase A2 must refine only the selected R403 VHVH family at 0.05 mm and prove exact source-track and R403 pad identity before any Phase B materialization.
