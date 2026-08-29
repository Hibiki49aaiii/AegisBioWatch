# Human Understanding — Issue #10

## What
This task tests one short +1V8 trace between adjacent decoupling capacitors C3 and C4 on the far-right edge of the Main Board.

## Why
route-1bc safely connected C2.1 to C3.1 using the same local geometry class. C3.1 and C4.1 are likewise vertically aligned, same-net, require no via, and stay outside RF, PMIC, I2C, and supplier-gated regions.

## How
The accepted route-1bc board is reconstructed first. The candidate adds one straight 0.30 mm F.Cu segment from:
- C3.1: (41.005,13.475)
to
- C4.1: (41.005,14.975)

No via or placement change is introduced.

## Important decisions
- Previous success of route-1bc is supporting evidence only, not automatic acceptance.
- KiCad 9.0.9 DRC remains the acceptance authority.
- A single DRC violation rejects the candidate; no rule waiver is allowed.
- The longer C4→C302 path is deliberately left for a separate later increment.

## Failure modes
- clearance to C3.2/C4.2 or nearby copper is smaller than expected;
- same-net topology changes the ratsnest by an unexpected amount;
- route-1bc source geometry is accidentally modified;
- zone refill causes unintended connectivity.

## Change impact
If accepted, the routing authority becomes route-1bd at 0 violations / 119 unconnected / 268 PASS. If rejected, route-1bc remains authoritative.
