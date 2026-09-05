# Human Understanding — Issue #17

## Why route-1bk rescreened from route-1bj
route-1bj changed the +1V8 topology, so the accepted 114-item DRC output was used as current routing truth rather than reusing prior ratsnest ordering.

## Screening outcome
The ordinary screen found only:
- VSYS_HAPTIC C305→C304;
- DOCK_5V_RAW D101→D102;
- a borderline +1V8→R403 route.

Expanded search did not produce a better ordinary low-risk route. A reset route passed geometrically but approached RF_B/C11, so it was rejected under the RF freeze.

Targeted low-current searches for CHG_SENSE_GATE and HAPTIC_TRIG found no legal route with up to four orthogonal segments under the 0.100 mm rule.

## Why VSYS_HAPTIC is selected
C305 and C304 are both local bypass capacitors on the DRV2605L supply net:
- C305 = 1uF;
- C304 = 100nF;
- U4 pin10 = VSYS_HAPTIC;
- R305 is the 0R / ferrite-bead option that feeds VSYS_HAPTIC from VSYS.

The selected route joins the two local supply-capacitor islands. It does not yet route the source feed or U4 VDD pin, so those remain available for later power-intent optimization.

Selected path:
- (6.805,22.335)
- (6.805,21.650)
- (16.005,21.650)
- (16.005,23.725)

The modeled minimum clearance is 0.125 mm to a 0.60 mm GND via centered at (12.750,22.225). The same value is independently reproduced from the simple vertical geometry.

## Power-width rationale
The board stack-up records 18 µm F.Cu. At 0.30 mm width and 11.96 mm length, the candidate copper resistance is approximately 38 mΩ at room-temperature resistivity.

TI's DRV2605L layout guidance says to use 75–100 µm at solder-pin escape and increase width after escape for current flow. The selected 0.30 mm route is wider than the recommended pin-escape width, but this does not replace final actuator-current and thermal signoff.

DOCK_5V_RAW is not selected because it is a primary input-power path with ESD/current implications and deserves coordinated power routing.

## Acceptance authority
The geometry model is preflight only. Acceptance requires:
- KiCad 9.0.9 DRC = 0;
- exact 114→113 ratsnest decrement;
- 268-node physical pin/net audit PASS;
- exact three-segment zero-via scope;
- downloaded Artifact re-verification.

Any failure leaves route-1bj authoritative.
