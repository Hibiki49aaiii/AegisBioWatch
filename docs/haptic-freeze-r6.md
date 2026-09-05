# Haptic subsystem freeze — r6

## Driver
TI DRV2605LDGSR, VSSOP-10.

- VDD operating range supports direct Li-ion/system supply.
- C(REG) = 1 uF.
- local VDD bulk = 1 uF; r6 retains an additional 100 nF HF bypass.

## Actuator
Precision Microdrives C10-100:
- 10 mm diameter x 3.7 mm
- 175 Hz typical resonant frequency
- 2 Vrms rated
- 2.05 Vrms maximum operating voltage
- 67 mA typical, 90 mA maximum rated current

The LRA is fed by DRV2605L from `VSYS_HAPTIC`, not the +3V0 bio buck. R305 is a 0-ohm population position that can become a ferrite only if enclosure EMI/vibration tests justify it.

Auto-resonance behavior must be calibrated in the actual watch because the actuator response depends strongly on the mounted mass. Firmware must not exceed the actuator voltage limit.
