# PCB reference-placement review — Phase 1 r12

## Purpose

r12 is an **evidence review**, not a new routed-board revision.

The purpose is to determine whether r11 has enough physical space for the final
Nordic reference-style placement and to prevent third-party coordinates from
silently becoming design authority.

## nPM1300 cross-check

A public KiCad implementation was reviewed:

- repository: `hlord2000/nPM1300-Stamp`
- board: `nPM1300-Stamp.kicad_pcb`
- license: CERN-OHL-P-2.0
- board stack: four copper layers

The implementation places its nPM1300 (`U1`) at `(150.5, 99.5)` mm. Sampled
source-local components occupy the following offsets from the PMIC origin:

| Ref in source | ΔX mm | ΔY mm |
|---|---:|---:|
| L1 | -6.33 | -1.63 |
| L2 | -6.53 | +1.28 |
| C1 | -0.25 | +4.20 |
| C2 | -4.21 | +1.28 |
| C3 | -4.21 | -1.74 |
| C4 | +5.64 | +1.00 |
| C5 | +5.64 | -0.57 |

The sampled bounding box is approximately **12.17 × 5.94 mm** around the PMIC.
This is only a density/adjacency cross-check. The source-local designators are
not mapped one-to-one onto AegisBioWatch's C101…/L101… references.

### r11 implication

The r10/r11 PMIC reserve is 12.5 × 11 mm, so the current board envelope has
sufficient area to compact the PMIC cluster significantly. The current r11
positions should therefore be treated as staging positions, not as an argument
for increasing board size.

The final placement must still be reconstructed from Nordic's nPM1300 QFN
reference guidance, especially the BUCK input/output loops and PVSS return
geometry.

## nRF54L15-QFAA review

Multiple public KiCad boards containing nRF54L15 were found. However, the raw
QFN implementations inspected so far either:

- have no clearly applicable hardware-source license; or
- use an nRF54L15 module instead of the QFAA raw SoC.

Therefore **no third-party nRF54L15 PCB coordinates are being copied into
AegisBioWatch**.

The CC0 `feastorg/KiCad-Master-Lib` QFAA reference block remains useful for
schematic topology/value verification, but it does not provide a PCB placement
that can replace Nordic's official layout guidance.

## r12 decision

- Keep the r11 board/net/footprint synchronization unchanged.
- Do not route U1/RF or U2/PMIC yet.
- nPM1300: use the CERN-OHL-P implementation only as a density/adjacency
  cross-check; use Nordic as final physical authority.
- nRF54L15-QFAA: retain seed positions until authoritative/licensed placement
  evidence is available.
- Do not enlarge the PCB based on the current loose r11 PMIC seed.

## Release status

r12 makes **no board-coordinate changes** and does not change the electrical
revision. Manufacturing status remains blocked.
