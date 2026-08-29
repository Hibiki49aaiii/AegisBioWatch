# Human Understanding — Issue #18

## Why route-1bl must rescreen
route-1bk connected the C305/C304 VSYS_HAPTIC capacitor islands. KiCad therefore reports a new 113-item ratsnest. That actual accepted state is the only valid input for route-1bl.

## Preferred current candidate
The shortest ordinary non-frozen-looking pad-to-existing-rail item is:
- `C301.1/+1V8 @ (13.755,23.725)`
- → existing `+1V8` rail endpoint `(15.755,26.725)`
- ratsnest distance ≈ 3.6056 mm.

C301 is a 100 nF 0201 bypass capacitor:
- C301.1 = +1V8;
- C301.2 = GND at (14.395,23.725).

The target coordinate is the top endpoint of the accepted route-1bj segment:
- (15.755,26.725) → (15.755,26.200)
- +1V8
- F.Cu width 0.30 mm.

The DRC coordinate alone does not authorize a T-junction. The exact probe must verify that the target is a real endpoint of the accepted same-net segment and that the new route lands there without altering the existing route.

## Alternatives
A VSYS track→R106.1 item is only slightly longer, but R106.2 is the explicitly deferred LDO2_IN node. It is therefore lower priority.

Shorter items involving U1, J7, RF passives, C401, CHG_5V or nRF internal rails remain frozen/deferred.

## Search policy
Use a read-only 0.05 mm Manhattan screen with 0.30 mm provisional F.Cu width and a hard conservative clearance floor of 0.100 mm.

## Rollback
Any failed screen, endpoint proof, exact probe, DRC, 113→112 decrement, audit, scope or Artifact-integrity gate leaves route-1bk unchanged as the accepted authority.
