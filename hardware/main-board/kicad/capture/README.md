# KiCad Phase 1 capture — r2

This directory contains real KiCad schematic capture sources, deliberately marked pre-freeze.

## Open in KiCad 9

1. Open `MCU_RF_CLOCK.sch` or `PMIC_CHARGER.sch`.
2. KiCad imports the legacy Eeschema v4 interchange schematic.
3. Save it as native `.kicad_sch`.
4. Keep `AegisBioWatch.lib` and `sym-lib-table` beside the schematics during import.

The legacy interchange format is used because the automation environment does not have `kicad-cli` installed. ERC therefore remains pending until opened in KiCad 9.

## Captured

### MCU_RF_CLOCK
- nRF54L15-QFAA QFN48 exact pad numbering
- AMOLED QSPI allocation
- AUX SPI allocation
- system I2C
- interrupt/GPIO allocation
- SWD/reset
- 32 MHz and 32.768 kHz clock nets

### PMIC_CHARGER
- nPM1300 QFN32 exact pad numbering
- 1S Li-Po / NTC interface
- magnetic 5 V charging input
- BUCK1 1.8 V (`VSET1=47k`)
- BUCK2 3.0 V (`VSET2=150k`)
- 2.2 uH buck inductors
- I2C / switched display and bio rails

## Hard gates before PCB layout

- unfold the exact nRF54L15 DECA/DECRF/DECD/DCC and RF reference network;
- run KiCad 9 ERC;
- select battery and NTC curve;
- select magnetic-input ESD/surge components;
- lock AMOLED FPC and panel power sequencing;
- lock antenna and enclosure RF keep-out.

**Do not order a PCB from this capture yet.**
