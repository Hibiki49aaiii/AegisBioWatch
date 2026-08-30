# Human Understanding — Issue #19

## Why route-1bm must start from route-1bl
route-1bl closed one VSYS item and reduced the executed ratsnest from 113 to 112. Every earlier candidate ranking is therefore stale.

The accepted route-1bl Artifact has been re-read directly:
- 0 DRC violations;
- 112 unconnected items;
- 268-node physical pin/net audit PASS.

## What is immediately excluded
The shortest remaining ratsnest entries are dominated by intentionally frozen regions:
- U1 adjacent pads;
- C7–C12 / RF passives;
- J7;
- C401 RF-adjacent GND;
- CHG_5V;
- nRF internal regulator/crystal nets;
- R106.2/LDO2_IN;
- SYS_I2C_SCL geometry-gated PMIC-side route.

These are not candidates merely because they are geometrically short.

## Ordinary candidates still worth screening
The current route-1bl ratsnest still contains ordinary-looking +1V8 island/rail items and some low-risk signal/GND items at roughly 4.7 mm and above.

C301 remains suspicious: a prior targeted four-segment route to one +1V8 rail produced 0 legal paths with only 0.074999 mm best clearance. A different DRC representative is not proof that C301 is now routable.

## Screening rule
Phase A1 is read-only. It uses the actual reproduced route-1bl board and treats different-net and unnetted copper as obstacles. Same-net copper is context, not an obstacle.

A DRC description or representative coordinate is not electrical authority. Before any materialization, the exact source/target pad or track must be proven from PCB data.

## Rollback
Any failed source gate, screen, refine, exact probe, DRC, 112→111 decrement, audit, scope, or Artifact integrity gate leaves route-1bl unchanged as the accepted authority.
