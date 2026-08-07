# Phase 1 capture status — Rev.0 r2

## Completed in r2

- nRF54L15-QFAA QFN48 local KiCad symbol with pins 1–49
- nPM1300 QFN32 local KiCad symbol with pins 1–33
- MCU pin-endpoint net assignment
- dedicated AMOLED QSPI mapping
- AUX SPI / I2C / interrupt / SWD mapping
- 32 MHz and 32.768 kHz clock nets
- PMIC pin-endpoint net assignment
- BUCK1 1.8 V architecture (`VSET1 = 47 kΩ`)
- BUCK2 3.0 V architecture (`VSET2 = 150 kΩ`)
- 2.2 µH buck inductors
- 1S Li-Po / NTC interface naming
- magnetic 5 V charge input naming
- privacy boundary maintained: no personal case/medication details

## Hard release gates

- [ ] exact nRF54L15 DECA / DECRF / DECD / DCC network captured from QFAA reference
- [ ] exact RF harmonic/matching network captured and reviewed
- [ ] KiCad 9 native conversion
- [ ] ERC passed
- [ ] final battery and NTC curve selected
- [ ] charger input ESD/surge protection selected
- [ ] exact AMOLED/FPC/power sequence selected
- [ ] antenna selected and RF keep-out frozen
- [ ] Main↔Bio connector frozen

## Status

`SCHEMATIC_CAPTURE_IN_PROGRESS`

PCB fabrication is prohibited until all hard release gates are closed.
