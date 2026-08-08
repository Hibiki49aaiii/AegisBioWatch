# Third-party / reference notices

## Nordic Semiconductor

The nRF54L15 and nPM1300 design uses Nordic Semiconductor product
specifications/reference-design guidance as the engineering authority.

## feastorg/KiCad-Master-Lib — nRF54L15 QFAA reference block

Reference used for independent nRF54L15-QFAA circuit/pin/value cross-check:
`https://github.com/feastorg/KiCad-Master-Lib`

The repository publishes its work under CC0 1.0 Universal.

## hlord2000/nordic-lib-kicad — nRF54L15 QFN48 reference block

Reference used for a second independent implementation cross-check:
`https://github.com/hlord2000/nordic-lib-kicad`

License: CERN Open Hardware Licence Version 2 — Permissive (CERN-OHL-P-2.0).

Modification notice — 2026-08-07:
AegisBioWatch adapts only the relevant nRF54L15-QFN48 reference values/topology
into a watch-specific design, renames nets, removes unrelated development-board
features, and adds project-specific display/storage/haptic/bio interfaces.

## hlord2000/nPM1300-Stamp — placement-density cross-check

Reference reviewed during Phase 1 r12:
`https://github.com/hlord2000/nPM1300-Stamp`

License: CERN Open Hardware Licence Version 2 — Permissive (CERN-OHL-P-2.0).

The r12 review extracts a small set of relative PMIC/passive coordinates only to
cross-check achievable component density and adjacency. AegisBioWatch does **not**
treat this third-party board as the final placement authority; Nordic's nPM1300
reference layout/current-return guidance remains authoritative.

Modification/use notice — 2026-08-09:
The source coordinates are normalized to the PMIC origin and recorded as review
evidence. Source-local designators are not copied or mapped one-to-one into the
AegisBioWatch PCB, and no nPM1300-Stamp board geometry is directly imported.

## DRV2605L pinout

DRV2605LDGS pin numbering was cross-checked against KiCad's haptic-driver symbol
representation and a generated SKiDL mirror. The AegisBioWatch symbol is local
and purpose-built.
