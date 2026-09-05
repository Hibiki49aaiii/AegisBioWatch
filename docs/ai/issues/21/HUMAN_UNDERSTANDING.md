# Human Understanding — Issue #21

## Why the screen must be regenerated
route-1bn added the R403.1/+1V8 closure and reduced the executed ratsnest from 111 to 110. Any candidate list from route-1bm is therefore stale.

The accepted route-1bn authority proves:
- KiCad 9.0.9 DRC = 0;
- 110 unconnected items;
- 268-node physical pin/net audit PASS;
- exactly four 0.30 mm F.Cu +1V8 segments and zero vias;
- no removed copper;
- no component move/rotation;
- no frozen-interface mutation;
- source +1V8 track preserved;
- R403.2/SYS_I2C_SDA preserved.

## Phase A meaning
Phase A is discovery only. The actual route-1bn board is reproduced first, then its current 110-item ratsnest is screened. The screen can reject unsafe geometry and rank numerical passes, but it cannot accept copper.

The generic screening engine is reused with explicit route-1bn source PCB/report inputs and expected-unconnected=110. Its internal historical revision label is wrapped into route-1bo evidence; executed source gates and explicit source paths are authority.

## Safety boundary
Keep U1 high-density, J7, supplier-gated J3/J5/J6, RF/nRF internal/critical passives, CHG_5V, LDO2_IN, SYS_I2C_SCL, PMIC switch nets, DOCK_5V_RAW and default-deferred BIO_SW/DISP_SW outside this increment.

A numerical pass involving unresolved interface context (for example an unidentified/blank pad) remains HOLD until semantic identity is proven.

## Rollback
Any failed source gate, screen, refine, exact probe, DRC, 110->109 decrement, audit, physical scope, or Artifact integrity gate leaves route-1bn unchanged as the accepted authority.

Manufacturing status remains NOT_FOR_GERBER.
