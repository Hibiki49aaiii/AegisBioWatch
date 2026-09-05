# Human Understanding — Issue #9

## What
This task tests one short +1V8 trace between two adjacent decoupling capacitors, C2 and C3, on the far-right edge of the Main Board.

## Why
After route-1bb, 121 unrouted items remain. C2.1 and C3.1 are vertically aligned, use the same +1V8 net, need no via, and are outside RF, PMIC, I2C, and supplier-gated regions.

## How
The accepted route-1bb board is reconstructed first. The candidate adds one straight 0.30 mm F.Cu segment from:
- C2.1: (41.005,11.975)
to
- C3.1: (41.005,13.475)

No via or placement change is introduced.

## Important decisions
- The approximately 0.26 mm preflight gap to the adjacent GND pad column is only a selection aid.
- KiCad 9.0.9 DRC remains the acceptance authority.
- A single DRC violation rejects the candidate; no rule waiver is allowed.
- This Issue does not continue from C3 to C4 even though that may later be another candidate; one logical increment is validated at a time.

## Failure modes
- clearance to C2.2/C3.2 or another copper feature is smaller than preflight suggests;
- the same-net topology changes the ratsnest by an unexpected amount;
- source route-1bb geometry is accidentally modified;
- component/net identity differs from the inspected Artifact.

## Change impact
If accepted, the routing authority becomes route-1bc at 0 violations / 120 unconnected / 268 PASS. If rejected, route-1bb remains authoritative.
