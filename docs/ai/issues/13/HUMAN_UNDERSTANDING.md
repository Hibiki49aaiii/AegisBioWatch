# Human Understanding — Issue #13

## What
C5 is a 100nF +1V8 decoupling capacitor whose +1V8 pad remains disconnected. L101.2 is already the endpoint of an accepted +1V8 power rail that continues to C107.1.

## Why this endpoint
Connecting to L101.2 is preferable to terminating on the midpoint of the existing rail:
- endpoint geometry is explicit;
- no track splitting/T-junction ambiguity;
- only one new segment is required;
- the route leaves C5 away from its GND pad.

## How
A direct 0.30 mm F.Cu segment runs from C5.1 at (9.255,22.225) to L101.2 at (8.964712,24.126353). The direct length is 1.923385 mm.

Before adding copper, a read-only probe checks a conservative route envelope for unrelated F.Cu pads, tracks and vias. Same-net +1V8 rail copper is recorded as context, not a blocker.

## Important decisions
- Preserve C5.2/GND exactly.
- Preserve L101.1/PMIC_SW1 exactly.
- Join the rail at L101.2, not at a track midpoint.
- Do not reroute the existing L101.2→C107.1 segment.
- Do not relax clearance if the direct path fails.

## Failure modes
- unexpected unrelated copper intersects the direct envelope;
- candidate creates a DRC violation near GND or PMIC_SW1;
- ratsnest changes by more than one;
- pin/net audit changes.

## Change impact
If accepted, authority advances from route-1bf 0/117/268 to route-1bg 0/116/268. Release remains NOT_FOR_GERBER.
