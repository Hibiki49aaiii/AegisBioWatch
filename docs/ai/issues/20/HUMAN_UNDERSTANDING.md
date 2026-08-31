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
