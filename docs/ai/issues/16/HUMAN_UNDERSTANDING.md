# Human Understanding — Issue #16

## Why route-1bj starts with a new screen
Route-1bi connected U3.8/+1V8 to C1.1/+1V8. That changed +1V8 connectivity and therefore changed which same-net islands KiCad reports as the next ratsnest edges.

The accepted route-1bi Artifact shows 115 unconnected items. The old route-1bg ordering is not treated as current truth.

## What remains ordinary
After excluding frozen and intentionally deferred regions, current ordinary candidates include +1V8 island connections, the R302/R404 pull-up rail pair, DOCK_5V_RAW, CHG_SENSE_GATE, HAPTIC_TRIG, VSYS and VSYS_HAPTIC.

A short Euclidean ratsnest edge is not enough to justify routing. The previous work already showed that direct paths can cross unrelated copper, while a standards-compliant Manhattan path may exist.

## Search policy
The first Phase A screen used 0.25 mm lane spacing. The selected R404/R302 candidate had only 0.125 mm conservative clearance, so the same current route-1bi geometry was re-screened at 0.05 mm lane spacing rather than accepting a marginal lane.

The refined best path moved the horizontal lane from y=26.25 to y=26.20 and improved conservative clearance to 0.175 mm without increasing total length.

The geometric screen is only preflight. KiCad DRC, exact ratsnest decrement and the 268-node physical pin/net audit remain the acceptance authority.

## Selected route
R404 and R302 are both pull-up resistors whose pad1 is +1V8:
- R404 = 4.7k provisional pull-up; pad2 is SYS_I2C_SCL.
- R302 = 47k pull-up; pad2 is FLASH_HOLD_N.

Selected path:
- R404.1 at (15.755,26.725)
- down to (15.755,26.200)
- across to (20.255,26.200)
- up to R302.1 at (20.255,25.975)

This keeps the new rail on the pad1 side and does not touch either signal pad.

The nearest unrelated copper is R501.1/CHG_5V. Conservative clearance is 0.175 mm versus the 0.100 mm rule.

## Why other geometric passes are not preferred
- NRF_DECD routes belong to the nRF internal regulator/decoupling network and are not treated as an ordinary pull-up closure.
- DOCK_5V_RAW has strong clearance but is a materially longer power path and should be designed with dock-power current/placement intent.
- The R403 path lands at 0.099999 mm in the conservative model, so it is rejected rather than rounded upward.

## Rollback
Any failed exact probe, DRC, 115→114 decrement, audit, exact-scope or Artifact-integrity gate leaves route-1bi unchanged as the accepted authority.
