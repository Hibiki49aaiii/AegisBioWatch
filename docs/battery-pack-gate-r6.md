# Battery pack release gate — r6

## Cell candidate

EEMB LP372435TB:
- Li-polymer, 3.7 V nominal, 300 mAh
- 24.5 x 36 x 4.0 mm
- 6 g
- -20 to +70 °C listed operating range
- bare cell with solder tabs

The bare cell **must not** be connected directly to the nPM1300 in the released watch. Nordic requires a battery pack connected to VBAT to contain overvoltage, undervoltage and overcurrent-discharge protection.

## Pack procurement specification

Production pack shall be based on LP372435TB geometry/cell unless qualification changes it, with:
1. overvoltage protection;
2. undervoltage protection;
3. overcurrent discharge protection;
4. three-wire output: VBAT / NTC / GND;
5. thermally coupled Murata NXRT15XH103FA5B030 or electrically equivalent approved NTC;
6. insulated tabs/leads and mechanical strain relief suitable for a wrist device.

## NTC

Selected NTC: NXRT15XH103FA5B030
- R25: 10 kOhm ±1%
- B25/50: 3380 K ±1%
- B25/85: approximately 3434 K

nPM1300 explicitly supports the 10 kOhm / B25/50 3380 K / B25/85 3434–3435 K class. Firmware must select the corresponding ADCNTCRSEL configuration before enabling charging.

## Charge current

Do not hard-code the final fast-charge current from nominal capacity alone. Until EEMB/custom-pack charge specifications are received and pack thermal behavior is measured, firmware remains conservative and treats charge current as a qualification parameter.
