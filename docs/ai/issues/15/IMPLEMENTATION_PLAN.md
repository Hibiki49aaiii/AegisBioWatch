# Issue #15 Implementation Plan — route-1bi candidate screening

## Base
- Branch: `agent/phase1-mainboard-schematic`
- Base accepted SHA: `cf138dd4835cc152c60c49d99f8a6d145745acbb`
- Authority: route-1bg = 0 / 116 / 268 PASS

## Phase A
Reproduce route-1bg and evaluate seven direct 0.30 mm F.Cu candidates read-only.

Scoring:
1. conservative different-net/unnetted copper clearance >= 0.100 mm;
2. larger clearance;
3. shorter length;
4. clearer endpoint semantics.

RF, J7, U1-adjacent, buck-switch, CHG_5V, LDO2_IN and supplier-gated items are excluded.

## Phase B
Only the winning candidate receives a materializer and dedicated KiCad 9.0.9 validation. Acceptance target is 0 / 115 / 268 PASS.

## Safety
Phase A writes no board. Any Phase B probe/DRC/audit failure leaves route-1bg authoritative.
