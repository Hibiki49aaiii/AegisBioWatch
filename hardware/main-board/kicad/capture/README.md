# KiCad Phase 1 capture — r3

This directory contains **real KiCad schematic capture sources**, but they are
deliberately marked as pre-freeze.

## Open in KiCad 9

1. Open `MCU_RF_CLOCK.sch`, `PMIC_CHARGER.sch`, or `STORAGE_HAPTIC.sch`.
2. KiCad will import the legacy Eeschema v4 schematic.
3. Save it as the native `.kicad_sch` format.
4. Keep `AegisBioWatch.lib` and `sym-lib-table` beside the files during import.

The legacy format is being used only as a deterministic interchange format
because the current automation environment does not contain `kicad-cli`.

## Current completion

### MCU_RF_CLOCK
Captured:
- exact QFN48 pad/pin numbering;
- display QSPI allocation;
- auxiliary SPI allocation;
- I2C allocation;
- GPIO/interrupt allocation;
- SWD/reset;
- 32 MHz and 32.768 kHz crystal placeholders;
- VDD decoupling block;
- RF harmonic/matching network;
- reset series/shunt network.

Gated:
- exact DECA/DECRF/DECD/DCC connectivity against the Nordic Product Specification;
- final antenna implementation and tuning.

### PMIC_CHARGER
Captured:
- exact QFN32 pin numbering;
- 1S battery / NTC interface;
- magnetic 5 V VBUS input;
- BUCK1 1.8 V / 47 kΩ VSET1;
- BUCK2 3.0 V / 150 kΩ VSET2;
- 2.2 µH buck inductors;
- output/bulk decoupling;
- system I2C;
- switched display/bio rails as named interfaces.

Still blocked:
- final battery/NTC values;
- final charge-current register policy;
- final surge/ESD device selection for magnetic dock.

### STORAGE_HAPTIC
Captured:
- 512 Mbit / 64 MB 1.8 V SPI-NOR class on AUX SPI;
- WP#/HOLD# pull-ups and local decoupling;
- DRV2605LDGSR VSSOP-10 on shared I2C;
- boot-safe trigger/enable pull-downs;
- differential LRA output connector.

Still blocked:
- exact Flash MPN/package;
- exact LRA actuator;
- TI-datasheet final verification for REG capacitor and peak-current budget.

## r3 RF/reset corrections

- raw MCU RF is `RF_MCU`, filtered output is `RF_ANT`, so the matching network cannot be bypassed by a shared net label;
- raw MCU reset is `NRF_RESET_RAW`, external reset is `NRF_RESET_N`, so the 1 kΩ series resistor cannot be bypassed;
- internal-regulator reference parts are staged but deliberately unconnected until the Nordic product-spec connectivity check closes.

## Manufacturing status

**NOT manufacturing-ready. Do not order PCBs from this capture yet.**
