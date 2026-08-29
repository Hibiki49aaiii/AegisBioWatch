# Human Understanding — Issue #8

## What
This task tests whether the still-unrouted left ground terminal of the J9 side-button footprint can be stitched into the internal ground plane with one short trace and one normal through-via.

## Why
Route-1ba safely closed the right duplicate J9 ground pad. The left duplicate pad is a plausible low-risk next increment that does not enter RF, PMIC, I2C, or supplier-gated regions.

## How
The accepted route-1ba board is reconstructed first. The candidate adds only:
- one 0.30 mm F.Cu segment from left J9.1/GND (20.850,5.775);
- one 0.60/0.30 mm GND through-via initially targeted at (19.850,5.775).

KiCad then refills zones and performs full DRC. The physical pin/net audit must still cover all 268 source nodes.

## Important decisions
- Footprint symmetry is not accepted as electrical proof.
- Executed KiCad 9.0.9 decides acceptance.
- A single clearance violation rejects the candidate; no design-rule waiver is allowed.
- Existing route-1ba geometry is frozen during this increment.

## Failure modes
- left-side copper is less clear than the right side;
- the proposed via collides with another pad/track/zone rule;
- duplicate-pad selection targets the wrong physical J9 pad;
- connectivity changes by more than the intended single ratsnest decrement.

## Change impact
If accepted, the unrouted count should move from 122 to 121 with no other design change. If rejected, route-1ba remains the accepted authority unchanged.
