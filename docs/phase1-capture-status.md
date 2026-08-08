# Phase 1 capture status — Rev.0 r5

## Completed through r5

- nRF54L15-QFAA QFN48 pin map and RF/internal-regulator reference capture
- nPM1300 QFN32 pin map
- nPM1300 Configuration-1 reference passive network and local PVSS return topology
- dedicated AMOLED QSPI and separate AUX SPI
- shared I2C/TWI, interrupts and SWD
- 32 MHz + 32.768 kHz clock interfaces
- RF matching/harmonic network
- 512 Mbit / 64 MB-class SPI NOR storage capture
- DRV2605LDGSR + LRA haptic capture
- logical display/touch and Main↔Bio interfaces
- hardware `CHG_PRESENT_N` safety indication independent of MCU firmware
- PCB/RF layout constraint document
- explicit power-budget release gate
- nPM1300 Revision/build-code errata gate
- r5 connectivity audit: 172 explicit wires; 166/166 mapped wire endpoints; nPM1300 pin labels 33/33; zero checked net-label conflicts
- no personal case/medication details in Git

## Hard release gates

- [ ] native KiCad 9 conversion
- [ ] ERC passed
- [ ] final 32 MHz / 32.768 kHz crystal MPN and load-cap strategy
- [ ] effective-capacitance/DC-bias check for all PMIC MLCCs
- [ ] final nPM1300 inductor MPNs
- [ ] final nPM1300 build code / errata applicability
- [ ] final Flash MPN/package/footprint
- [ ] final LRA MPN and current budget
- [ ] final battery, PCM and NTC curve
- [ ] charger input ESD/reverse-polarity protection MPNs
- [ ] charge current / VBUS current-limit policy
- [ ] exact AMOLED/FPC/power sequence
- [ ] touch I/O voltage / level shifting
- [ ] power-budget gate for display / bio / haptic
- [ ] antenna selection, matching footprint and RF keep-out
- [ ] final 4-layer stack-up and 50 Ω geometry
- [ ] physical Main↔Bio connector
- [ ] Bio Board electrode-disconnect/high-Z implementation

## Status

`SCHEMATIC_CAPTURE_R5_PMIC_LAYOUT_REVIEW`

**PCB fabrication remains prohibited until all hard gates are closed.**
