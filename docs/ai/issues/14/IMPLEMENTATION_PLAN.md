# Issue #14 Implementation Plan — route-1bh C301-R404 +1V8

## Base
- Branch: `agent/phase1-mainboard-schematic`
- Base SHA: `cf138dd4835cc152c60c49d99f8a6d145745acbb`
- Accepted authority: route-1bg = 0 violations / 116 unconnected / 268 PASS

## Objective
Close one +1V8 ratsnest edge:
`C301.1/+1V8 (13.755,23.725)` → `R404.1/+1V8 (15.755,26.725)`.

## Candidate
- C301 = 100nF
- R404 = 4.7k PU PROV
- direct length = 3.605551 mm
- track width = 0.30 mm
- layer = F.Cu
- segments = 1
- vias = 0

Adjacent non-target pads:
- C301.2/GND = (14.395,23.725)
- R404.2/SYS_I2C_SCL = (16.395,26.725)

## Implementation
1. Reproduce accepted route-1bg.
2. Execute a read-only pcbnew probe.
3. Gate exact ref/value/net/coordinates.
4. Calculate conservative geometric clearance between the candidate centerline and every unrelated F.Cu pad, track and via:
   - pad: segment-to-pad bounding-box distance minus candidate half-width;
   - track: segment-to-segment centerline distance minus both half-widths;
   - via: point-to-segment distance minus via radius and candidate half-width.
5. Require minimum conservative clearance >= 0.100 mm.
6. Materialize exactly one 0.30 mm F.Cu segment.
7. Refill zones, synchronize nets and rebuild connectivity.
8. Execute KiCad 9.0.9 DRC and 268-node audit.
9. Require 0 violations / 115 unconnected / 268 PASS.
10. Upload evidence and independently re-download/verify it.

## Invariants
- C301.1 remains +1V8.
- C301.2 remains GND.
- R404.1 remains +1V8.
- R404.2 remains SYS_I2C_SCL.
- No component moves/rotations.
- No vias.
- No design-rule waiver.
- No via-in-pad.
- RF and supplier-gated regions untouched.
- Geometry-gated U2.14↔R104 SYS_I2C_SCL item remains deferred.
- route-1bg geometry otherwise unchanged.

## Rollback
Any probe, DRC, ratsnest, audit, scope or Artifact-integrity failure rejects/defer route-1bh. route-1bg remains authoritative.
