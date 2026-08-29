# Issue #12 Implementation Plan — route-1bf R301-R503 +1V8

## Base
- Branch: `agent/phase1-mainboard-schematic`
- Base SHA: `54839f182121172fb2261bd1c6ee73b50178cee5`
- Accepted authority: route-1be = 0 violations / 118 unconnected / 268 PASS

## Objective
Close one aligned +1V8 pull-up rail gap:
`R301.1/+1V8 (3.005,25.975)` → `R503.1/+1V8 (3.005,27.475)`.

## Preflight from accepted Artifact
- Both resistors are `47k PU` 0201.
- Direct length: 1.500 mm.
- Proposed width: 0.30 mm.
- R301.2/FLASH_WP_N and R503.2/CHG_PRESENT_N are at x=3.645.
- Conservative gap from candidate track edge x=3.155 to signal-pad copper left edge x≈3.415 is ≈0.260 mm.
- Current minimum clearance is 0.100 mm.
- No existing segment/via was observed in the direct corridor.

## Implementation
1. Reproduce accepted route-1be.
2. Execute a read-only pcbnew probe:
   - exact refs/values/nets/coordinates/sizes;
   - F.Cu-only blocker scan in track-width + rule-clearance envelope;
   - verify zero board modification.
3. If probe passes, add exactly one vertical 0.30 mm F.Cu segment.
4. Refill zones and rebuild connectivity.
5. Execute KiCad 9.0.9 DRC and 268-node audit.
6. Require 0 violations / 117 unconnected / 268 PASS.
7. Upload evidence and verify the downloaded Artifact in a second job.
8. Accept only if all hard gates pass.

## Invariants
- R301 = R503 = 47k PU.
- R301.1/R503.1 remain +1V8.
- R301.2 remains FLASH_WP_N.
- R503.2 remains CHG_PRESENT_N.
- No component moves/rotations.
- No vias.
- No rule waiver.
- RF, PMIC/I2C deferred regions, and supplier-gated interfaces untouched.
- route-1be geometry otherwise unchanged.

## Rollback
Any probe, DRC, ratsnest, audit, scope, or Artifact verification failure rejects/defer route-1bf. route-1be remains authoritative.
