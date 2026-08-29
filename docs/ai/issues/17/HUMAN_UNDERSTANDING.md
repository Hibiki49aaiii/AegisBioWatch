# Human Understanding — Issue #17

## Why route-1bk must rescreen
route-1bj connected R404.1/+1V8 to R302.1/+1V8. KiCad therefore reports a different set of nearest same-net islands than route-1bi did.

The accepted route-1bj Artifact contains 114 unconnected items. That current DRC output—not the previous route-1bj screening input—is the routing source for route-1bk.

## Current short ordinary-looking pairs
The current Artifact shows:
- a VSYS track-to-track pair around 3.163 mm;
- C301.1/+1V8 to the new accepted +1V8 rail around 3.182 mm;
- many shorter items that are intentionally frozen or excluded.

These are only ratsnest distances. They do not establish a legal route.

## Search policy
Use a read-only 0.05 mm Manhattan lane search with 0.30 mm provisional F.Cu width and a hard conservative clearance floor of 0.100 mm.

NRF_DECD is explicitly excluded in this increment because it belongs to the nRF internal regulator/decoupling network.

Track endpoints need extra care: the coordinate in a DRC item may be an endpoint or representative point, so any pad-to-track winner must prove the exact physical target segment and legal landing geometry.

## Selection policy
Prefer:
1. ordinary low-current rail closure;
2. clear pad-to-pad or pad-to-existing-track semantics;
3. few segments;
4. short path;
5. margin materially above 0.100 mm;
6. no new current-carrying or bring-up-sensitive design decision.

VSYS and DOCK_5V_RAW are not automatically rejected, but should not be accepted as a generic 0.30 mm route without power-path context.

## Rollback
Any failed screen, exact probe, DRC, 114→113 decrement, audit, scope or Artifact-integrity gate leaves route-1bj unchanged as the accepted authority.
