# Phase 1 capture status — Rev.0 r3

## Completed through r3

- nRF54L15-QFAA QFN48 verified pin map
- nPM1300 QFN32 verified pin map
- dedicated AMOLED QSPI and separate AUX SPI
- shared I2C/TWI, interrupts and SWD
- 32 MHz + 32.768 kHz clock interfaces
- nPM1300 BUCK1=1.8 V / BUCK2=3.0 V architecture
- 1S Li-Po / NTC / magnetic 5 V charge interfaces
- nRF QFN48 VDD decoupling captured
- RF harmonic/matching network captured with **no net-name bypass** (`RF_MCU` ≠ `RF_ANT`)
- reset network captured with **no series-resistor bypass** (`NRF_RESET_RAW` ≠ `NRF_RESET_N`)
- 512 Mbit / 64 MB-class SPI NOR storage capture
- DRV2605LDGSR + LRA haptic capture
- third-party reference notices retained
- no personal case/medication details in Git

## Hard release gates

- [ ] official Nordic product-spec cross-check for exact `DECA/DECRF/DECD/DCC` connectivity
- [ ] native KiCad 9 conversion
- [ ] ERC passed
- [ ] final 32 MHz / 32.768 kHz crystal MPN and load-cap strategy
- [ ] final Flash MPN/package/footprint
- [ ] final LRA MPN and DRV2605L peak-current verification
- [ ] final battery and NTC curve
- [ ] charger input ESD/surge protection
- [ ] exact AMOLED/FPC/power sequence
- [ ] antenna selection, matching footprint and RF keep-out
- [ ] Main↔Bio connector

## Status

`SCHEMATIC_CAPTURE_R3_REFERENCE_REVIEW`

**PCB fabrication remains prohibited until all hard gates are closed.**
