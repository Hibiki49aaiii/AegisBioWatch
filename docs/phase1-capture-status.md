# Phase 1 capture status — Rev.0 r4

## Completed through r4

- nRF54L15-QFAA QFN48 verified pin map
- nPM1300 QFN32 verified pin map
- dedicated AMOLED QSPI and separate AUX SPI
- shared I2C/TWI, interrupts and SWD
- 32 MHz + 32.768 kHz clock interfaces
- nPM1300 BUCK1=1.8 V / BUCK2=3.0 V startup architecture
- 1S Li-Po / NTC / magnetic 5 V logical charge interfaces
- nRF QFN48 VDD decoupling
- RF harmonic/matching network with distinct `RF_MCU` / `RF_ANT`
- reset network with distinct raw/external reset nets
- **current Nordic QFN48 Config.1 internal regulator topology captured**
- 512 Mbit / 64 MB-class SPI NOR storage capture
- DRV2605LDGSR + LRA haptic capture
- logical AMOLED/touch interface capture without inventing supplier FPC pinout
- logical Main↔Bio 20-signal interface
- hardware `CHG_PRESENT_N` safety indication independent of MCU firmware
- explicit legacy-wire connectivity added to all five capture sheets
- 124/124 mapped passive/connector endpoint-to-net checks pass
- no conflicting net labels on checked wire-connected nodes
- privacy boundary maintained

## Closed in r4

- [x] `DECA/DECRF/DECD/DCC` topology cross-check
- [x] current Config.1 correction: `FB1 = 120 Ω @ 100 MHz`
- [x] current RF-supply bypass correction: `2.2 nF`
- [x] Display/Touch logical net capture
- [x] Bio-interface logical net capture
- [x] missing explicit Wire records corrected
- [x] KiCad legacy even-row connector 50 mil alignment corrected
- [x] mapped endpoint/net connectivity validation passed

## Hard release gates

- [ ] native KiCad 9 conversion
- [ ] ERC passed
- [ ] complete nPM1300 reference-passive / decoupling capture
- [ ] final 32 MHz / 32.768 kHz MPNs
- [ ] final Flash MPN/package/footprint
- [ ] final LRA MPN and peak-current verification
- [ ] final battery and NTC curve
- [ ] charger input ESD/surge protection
- [ ] exact AMOLED/touch MPN, FPC drawing and power sequence
- [ ] touch I/O-voltage compatibility / level-shifter decision
- [ ] antenna selection and RF keep-out/tuning
- [ ] physical Main↔Bio connector and pin order
- [ ] Bio Board electrode-disconnect/high-Z safety implementation

## Status

`SCHEMATIC_CAPTURE_R4_ELECTRICAL_WIRES_VALIDATED`

**PCB fabrication remains prohibited until all hard gates are closed.**
