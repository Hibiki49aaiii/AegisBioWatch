# Issue #13 Implementation Plan — route-1bg C5.1 to L101.2 +1V8

## Base
- Branch: `agent/phase1-mainboard-schematic`
- Base SHA: `85d993250798f44163b093c220a37a41245c54dd`
- Accepted authority: route-1bf = 0 violations / 117 unconnected / 268 PASS

## Objective
Connect `C5.1/+1V8 (9.255,22.225)` directly to the existing +1V8 rail endpoint at `L101.2/+1V8 (8.964712,24.126353)`.

## Candidate
- C5 = 100nF
- L101 = 2.2uH / DCR<400mR
- direct length = 1.923385 mm
- width = 0.30 mm
- layer = F.Cu
- segments = 1
- vias = 0

## Implementation
1. Reproduce accepted route-1bf.
2. Run a read-only pcbnew probe.
3. Gate:
   - C5/L101 identities;
   - exact pad nets and coordinates;
   - C5.2/GND and L101.1/PMIC_SW1 preservation;
   - existing L101.2→C107.1 +1V8 track;
   - no unrelated F.Cu pad/track/via in a conservative direct-route envelope.
4. Add exactly one 0.30 mm F.Cu segment C5.1→L101.2.
5. Refill zones, synchronize nets, rebuild connectivity.
6. Execute KiCad 9.0.9 DRC and 268-node audit.
7. Require 0 / 116 / 268 PASS.
8. Package evidence, re-download it in a second job, verify hashes and JSON gates.
9. Accept only if all gates pass.

## Invariants
- C5.1 stays +1V8; C5.2 stays GND.
- L101.1 stays PMIC_SW1; L101.2 stays +1V8.
- Existing L101.2→C107.1 +1V8 rail remains.
- No move/rotation.
- No via.
- No rule waiver.
- RF, supplier-gated, PMIC/I2C deferred regions untouched except the explicit C5→L101 +1V8 segment.
- route-1bf geometry otherwise unchanged.

## Rollback
Any probe, DRC, ratsnest, pin/net, scope, or Artifact verification failure rejects/defer route-1bg. route-1bf remains authoritative.
