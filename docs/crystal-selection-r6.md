# Crystal selection validation — r6

## 32 MHz HFXO
Selected: **Golledge MP06003**.

Published MP06003 values:
- 32.0 MHz fundamental
- CL = 8 pF
- C0 <= 3 pF
- ESR <= 50 ohm
- drive <= 100 uW
- calibration tolerance <= ±10 ppm
- temperature stability <= ±15 ppm

These fit the nRF54L15 HFXO envelope for the 8 pF / C0<=3 pF region. Nordic staff also identifies MP06003 as the crystal used on the nRF54L15 DK.

## 32.768 kHz LFXO
Selected: **Abracon ABS06-32.768KHZ-9-T**.

Published values include CL=9 pF, ESR=90 kohm, tolerance ±20 ppm and -40..85 C operation. These sit at the nRF54L-series 9 pF / 90 kohm maximum ESR boundary, so PCB stray capacitance and oscillator startup must be measured on the prototype rather than assumed.

## Load capacitors
The nRF54L15 supports configurable internal load capacitors on HFXO and LFXO. r6 does not add external load capacitors. Firmware/DeviceTree values are calibrated after assembled-board oscillator frequency/startup testing.
