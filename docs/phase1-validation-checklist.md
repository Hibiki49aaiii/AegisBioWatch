# Phase 1 schematic validation checklist

## Before schematic freeze
- [ ] nRF54L15 QFAA symbol pin numbers cross-checked against current Nordic datasheet
- [ ] nPM1300 QFN32 symbol pin numbers cross-checked
- [ ] nRF reference values copied from QFAA reference layout version 0.8
- [ ] nPM1300 configuration-1 passives copied from current product spec
- [ ] all VDD pins connected
- [ ] nRF exposed pad and VSS_PA grounding reviewed
- [ ] nRF DECA/DECRF relationship reviewed
- [ ] DCC inductor network reviewed
- [ ] 32 MHz and 32.768 kHz crystal specs reviewed
- [ ] VSET1 = 47k and VSET2 = 150k
- [ ] battery NTC circuit matches selected cell
- [ ] magnetic charging input has ESD/OV/current-path review
- [ ] charge-present safety path exists
- [ ] display FPC pinout verified against supplier drawing
- [ ] Flash supply voltage is 1.8 V
- [ ] I2C address collision check completed
- [ ] haptic LRA parameters verified
- [ ] Bio Board connector pinout frozen
- [ ] SWD pogo pads present
- [ ] ERC clean or every exception documented

## Before PCB layout
- [ ] Nordic QFAA reference layout open beside KiCad
- [ ] antenna and enclosure keep-out frozen
- [ ] layer stack confirmed with PCB fab
- [ ] controlled-impedance calculation requested
- [ ] component availability checked for build quantity
