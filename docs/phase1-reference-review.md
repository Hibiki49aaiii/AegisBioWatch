# Phase 1 reference review — r3

## nRF54L15-QFAA

Two independent KiCad reference sources were compared:

1. `feastorg/KiCad-Master-Lib` QFAA reference block — CC0 1.0.
2. `hlord2000/nordic-lib-kicad` QFN-48 reference block — CERN-OHL-P-2.0.

Both expose the same QFN48 pin map and the same RF filter values/topology.

### Captured as real circuitry in r3

- VDD: 10 uF bulk + four 100 nF local decouplers.
- RF chain: 2.7 nH / 1.5 pF / 3.5 nH / 2.0 pF / 3.5 nH / 0.3 pF.
- reset: 1 kΩ series and 3.9 pF MCU-side shunt.

### Staged, not electrically connected

The reference blocks expose the following internal-regulator values:

- FB1: 100 Ω @ 100 MHz
- C6: 2.2 uF
- C7: 10 nF
- C8: 10 nF
- C9: 2.2 uF
- L1: 4.7 uH

The `DECA/DECRF/DECD/DCC` connectivity remains a hard release gate until it is checked directly against the current Nordic Product Specification. No guessed topology is used.

## RF layout consequence

The component values do not authorize arbitrary placement. The RF section must copy the Nordic QFAA relative placement/ground return as closely as the watch mechanics allow, then be tuned with the actual enclosure and antenna.
