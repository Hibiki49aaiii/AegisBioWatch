# KiCad Phase 1 capture — r6

This directory contains **real KiCad schematic capture sources** in legacy
Eeschema v4 interchange format. The design remains pre-freeze and is not yet
manufacturing-ready.

## Open in KiCad 9

Open any of:

- `MCU_RF_CLOCK.sch`
- `PMIC_CHARGER.sch`
- `STORAGE_HAPTIC.sch`
- `DISPLAY_TOUCH.sch`
- `BIO_INTERFACE.sch`

KiCad will import the legacy schematic; save the imported result as native
`.kicad_sch`. Keep `AegisBioWatch.lib` and `sym-lib-table` beside the sheets
during import.

The legacy format is used as a deterministic interchange format because the
current automation environment does not contain `kicad-cli`.

## r5 electrical-connectivity audit

r4 introduced explicit wire records around legacy passive/connector symbols.
r5 repeats the audit after expanding `PMIC_CHARGER`.

| Sheet | Explicit wires | Validated wire/component endpoint checks |
|---|---:|---:|
| MCU_RF_CLOCK | 42 | 36 / 36 |
| PMIC_CHARGER | 55 | 55 / 55 |
| STORAGE_HAPTIC | 20 | 20 / 20 |
| DISPLAY_TOUCH | 26 | 26 / 26 |
| BIO_INTERFACE | 29 | 29 / 29 |

Totals:
- **172** explicit wire segments;
- **166 / 166** mapped wire/component endpoint checks pass;
- nPM1300 U2 direct pin-label mapping: **33 / 33** pass;
- **0** conflicting net-label sets on checked wire-connected nodes.

The PMIC PVSS1/PVSS2 net-ties follow the Nordic QFN reference schematic intent:
a short local switching-current return on the top layer transitions into the
**same continuous L2 GND plane**. They do not authorize a split ground plane.
The production net-tie copper/via geometry remains layout-specific.

See `docs/electrical-connectivity-validation-r5.json` and
`docs/structural-validation-r5.json`.

## Current capture

### MCU_RF_CLOCK

Captured:
- nRF54L15-QFAA QFN48 pin allocation;
- dedicated display QSPI and separate AUX SPI;
- shared I2C and interrupt allocation;
- SWD/reset;
- HFXO/LFXO interfaces;
- VDD decoupling;
- RF matching/harmonic network;
- reset series/shunt network;
- current Nordic QFN48 Configuration 1 `DECA/DECRF/DECD/DCC` network.

Current regulator network:
- DECA and DECRF share `NRF_DECA_RF`;
- `NRF_DECA_RF` → 2.2 µF / 10 nF / 2.2 nF → GND;
- `NRF_DECA_RF` → 120 Ω @ 100 MHz ferrite → `NRF_DECD`;
- `NRF_DCC` → 4.7 µH → `NRF_DECD`;
- `NRF_DECD` → 2.2 µF → GND.

Still gated:
- final crystals and load strategy;
- antenna choice, PCB stackup/controlled impedance, keep-out and enclosure RF tuning.

### PMIC_CHARGER — r5
Captured and cross-checked against current Nordic nPM1300 guidance:
- QFN32 pin mapping;
- VBUS 1 µF decoupling;
- mandatory VBUSOUT 1 µF decoupling even when VBUSOUT is unused;
- VBAT 2.2 µF decoupling;
- VSYS nominal 10 µF decoupling;
- two additional nominal 10 µF local BUCK input capacitors from VSYS/PVDD to the local PVSS1/PVSS2 current-return regions;
- BUCK1/BUCK2 2.2 µH inductors;
- BUCK1/BUCK2 10 µF output capacitors;
- PVSS1/PVSS2 local net-ties to main GND;
- VDDIO 100 nF decoupling;
- LDO output stability network (2 × 10 µF per output);
- optional 10 kΩ TWI pull-ups;
- optional VSYS feed links for VINLDO1/VINLDO2;
- SHPHLD two-pin wake-button interface.

Application addition:
- 100 nF high-frequency VSYS/PVDD bypass for the RF-sensitive wearable environment.

Important:
- `DISP_SW` and `BIO_SW` remain **provisional** because nPM1300 LS/LDO output-current limits may be below the final display/PPG peak-current requirement.
- no Gerber release is permitted until the power-budget gate is closed.

### STORAGE_HAPTIC

Captured:
- 512 Mbit / 64 MB-class 1.8 V SPI NOR logical class on AUX SPI;
- WP#/HOLD# pull-ups and local decoupling;
- DRV2605LDGSR VSSOP-10 on shared I2C;
- boot-safe trigger/enable pull-downs;
- differential LRA output connector.

Still gated:
- exact Flash MPN/package/footprint;
- exact LRA;
- TI-datasheet final verification and rail peak-current budget.

### DISPLAY_TOUCH

Captured without inventing a supplier FPC pin order:
- AMOLED QSPI SCK/D0-D3/CS;
- reset, TE and switched display-power logical nets;
- touch I2C/reset/interrupt logical nets;
- conditional 0 Ω direct-I2C links;
- provisional shared 1.8 V I2C pull-up pair.

Still gated:
- exact AMOLED/touch MPN and FPC drawing;
- display rail voltage/current and power sequence;
- touch I/O voltage compatibility and level-shifter decision.

### BIO_INTERFACE

Captured:
- logical 20-signal Main↔Bio interface;
- switched `BIO_SW` domain;
- I2C, AUX SPI, interrupts and `BIO_SAFE_EN`;
- independent hardware-derived active-low `CHG_PRESENT_N`.

The charge-present logic is a **safety interlock signal only**, not medical
isolation. The Bio Board must independently default electrode acquisition to
high impedance/disconnected while charging or when safety state is uncertain.

Still gated:
- physical connector/footprint and pin order;
- ESD/hot-plug behavior;
- Bio Board electrode-disconnect implementation.

## Manufacturing status

**NOT manufacturing-ready. Do not order PCBs from this capture yet.**

## r6 selected-part delta

- HFXO: MP06003
- LFXO: ABS06-32.768KHZ-9-T
- Flash: W25Q256JWPIQ (32 MB)
- LRA: C10-100
- Haptic rail: VSYS_HAPTIC
- Cell candidate: LP372435TB; protected 3-wire pack required
- NTC: NXRT15XH103FA5B030
- Dock protection: PMEG2010AEJ + PESD5V0S1UL
- AMOLED preferred candidate: GL175AMC10C, logical-only pending FPC documentation
