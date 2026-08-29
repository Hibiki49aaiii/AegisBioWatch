# Human Understanding — Issue #11

## What
The C2→C3→C4 +1V8 chain now needs to reach C302, the 1uF +1V8 decoupler in the right-edge/haptic area.

## Why this task is different
route-1bc and route-1bd were simple 1.5 mm straight segments. C4→C302 is several millimetres long and non-collinear. There is already accepted C302 GND copper nearby, so blindly drawing a line would be poor routing practice.

## How
The first implementation is deliberately read-only: regenerate route-1bd in GitHub Actions, inspect exact C4/C302 pad geometry and enumerate all pads/tracks/vias inside a broad corridor. Only then choose the route.

## Important decisions
- C302.1 coordinate is measured in CI, not inferred from C302.2.
- A previous GND route passing DRC does not prove a +1V8 corridor.
- A route is allowed to be deferred if standard-rule geometry is not clean.
- No rule waiver or component move is an acceptable shortcut.

## Failure modes
- intuitive F.Cu corridor intersects existing copper;
- layer transition is more intrusive than leaving the net unrouted;
- route creates unintended same-net topology change;
- candidate passes local intuition but fails KiCad DRC.

## Change impact
Probe phase changes no PCB geometry. If Phase B is later accepted, authority advances from route-1bd 0/119/268 to route-1be with the executed expected ratsnest.
