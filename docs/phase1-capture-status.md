# Phase 1 capture status — Rev.0 r6

## Completed through r6

- r5 electrical architecture and nPM1300 Config.1 passive network retained
- HFXO MPN selected: Golledge MP06003
- LFXO MPN selected: Abracon ABS06-32.768KHZ-9-T
- local Flash reduced/frozen to W25Q256JWPIQ, 32 MB
- haptic actuator selected: Precision Microdrives C10-100
- DRV2605L haptic power moved from +3V0 to `VSYS_HAPTIC`
- C(REG)=1uF and VDD bulk=1uF verified for DRV2605L
- battery cell candidate selected: EEMB LP372435TB 300mAh
- matching 10k/B3380 battery NTC selected: Murata NXRT15XH103FA5B030
- pack-protection requirement documented; bare cell direct connection prohibited
- magnetic dock ESD/reverse-polarity protection selected and captured
- preferred AMOLED candidate selected mechanically: GL175AMC10C
- no production 24-pin AMOLED mapping invented without supplier documentation

## r6 electrical audit

- 178 explicit wire segments
- 172 / 172 mapped endpoint checks pass
- nPM1300 direct pin-label mapping remains 33 / 33 pass
- dock ESD polarity explicitly verified: cathode to raw +5V, anode to GND
- no checked wire-connected net-label conflicts

This audit is not a substitute for KiCad ERC.

## Remaining hard release gates

- [ ] native KiCad 9 conversion and ERC
- [ ] custom/verified landing patterns for selected crystals and WSON Flash
- [ ] exact PMIC inductors/MLCC MPNs and DC-bias validation
- [ ] actual nPM1300 build code / errata record
- [ ] qualified protected battery-pack drawing, PCM and cell charging specification
- [ ] final charge-current profile and fuel-gauge battery model
- [ ] dock electrical margin test including diode/contact drop
- [ ] AMOLED supplier FPC pinout, rails, power sequence and command table
- [ ] touch I/O voltage / level shifting decision
- [ ] physical Main-Bio connector freeze
- [ ] antenna, fab stack-up and VNA tuning
- [ ] Bio Board electrode-disconnect/high-Z hardware capture

## Status

`SCHEMATIC_CAPTURE_R6_PART_SELECTION`

**PCB fabrication remains prohibited until all hard gates are closed.**
