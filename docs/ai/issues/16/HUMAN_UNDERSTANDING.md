# Human Understanding — Issue #16

## Why route-1bj starts with a new screen
Route-1bi connected U3.8/+1V8 to C1.1/+1V8. That changed +1V8 connectivity and therefore changed which same-net islands KiCad reports as the next ratsnest edges.

The accepted route-1bi Artifact shows 115 unconnected items. The old route-1bg ordering is not treated as current truth.

## What remains ordinary
After excluding frozen and intentionally deferred regions, current ordinary candidates include +1V8 island connections, the R302/R404 pull-up rail pair, DOCK_5V_RAW, CHG_SENSE_GATE, HAPTIC_TRIG, VSYS and VSYS_HAPTIC.

A short Euclidean ratsnest edge is not enough to justify routing. The previous work already showed that direct paths can cross unrelated copper, while a standards-compliant Manhattan path may exist.

## Search policy
The Phase A screen searches one- and two-turn orthogonal paths at 0.25 mm lane spacing. It is deliberately conservative and treats 0.100 mm as a hard minimum.

The geometric screen is only preflight. KiCad DRC, exact ratsnest decrement and the 268-node physical pin/net audit remain the acceptance authority.

## Selection policy
Prefer a route that:
1. connects real functional endpoints rather than duplicate/internal switch terminals;
2. has fewer segments;
3. is short;
4. has clear margin above 0.100 mm;
5. does not create a new high-current/RF/bring-up-sensitive design decision.

## Rollback
Any failed probe, DRC, ratsnest, audit, exact-scope or Artifact-integrity gate leaves route-1bi unchanged as the accepted authority.
