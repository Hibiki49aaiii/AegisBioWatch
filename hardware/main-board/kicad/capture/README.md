# KiCad Phase 1 capture — r4

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

## r4 electrical-connectivity audit

A previous structural pass revealed that the capture had labels and component
symbols but no explicit `Wire Wire Line` records around standard passive and
connector symbols. r4 corrects this rather than treating the drawings as
connected by appearance.

Explicit wire counts after correction:

| Sheet | Explicit wires | Validated endpoint/net checks |
|---|---:|---:|
| MCU_RF_CLOCK | 42 | 36 / 36 |
| PMIC_CHARGER | 13 | 13 / 13 |
| STORAGE_HAPTIC | 20 | 20 / 20 |
| DISPLAY_TOUCH | 26 | 26 / 26 |
| BIO_INTERFACE | 29 | 29 / 29 |

No checked wire-connected node contains conflicting net labels. Legacy KiCad
`Connector_Generic` pin geometry was also checked; even-row connector placement
was shifted by 50 mil where required so the drawn wires terminate on the real
symbol pin endpoints.

See `docs/electrical-connectivity-validation-r4.json` for the machine-readable
check result.

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

### PMIC_CHARGER

Captured:
- nPM1300 QFN32 pin allocation;
- 1S battery/NTC logical interface;
- magnetic 5 V charge input logical interface;
- BUCK1 startup target 1.8 V via 47 kΩ VSET1;
- BUCK2 startup target 3.0 V via 150 kΩ VSET2;
- 2.2 µH BUCK inductors;
- system I2C and switched `DISP_SW` / `BIO_SW` interfaces.

Still gated:
- complete nPM1300 reference-passive/decoupling capture and ERC;
- final battery and NTC curve;
- charge-current policy;
- magnetic-dock ESD/surge protection.

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
