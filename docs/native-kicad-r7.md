# Phase 1 r7 — Native KiCad 9 validation

## Toolchain

- KiCad CLI: **9.0.9**
- Canonical materialization: `python3 tools/materialize-native-r7.py`
- Canonical output: `hardware/main-board/kicad/native-r7/AegisBioWatch-MainBoard-Rev0.kicad_sch`
- Structure: native hierarchical KiCad 9 project

## ERC result

```bash
kicad-cli sch erc --format json --severity-all \
  -o erc-r7.json AegisBioWatch-MainBoard-Rev0.kicad_sch
```

Result: **0 violations**.

## Independent netlist validation

63 critical MCU, PMIC, Flash, haptic and NetTie pin-to-net expectations are checked against KiCad's exported netlist. Result: **63/63 pass**.

Examples include:

- U1 pin 27 → `DISP_RST_N`
- U1 pins 11–16 → dedicated AMOLED QSPI signals
- U1 pins 17/19/20 → AUX SPI
- U2 pin 32 → `+3V0`
- U2 pin 21 → `CHG_5V`
- U3 pin 1 → `FLASH_CS_N`
- NT101 → `PVSS1_LOCAL` ↔ `GND` using NetTie semantics
- NT102 → `PVSS2_LOCAL` ↔ `GND` using NetTie semantics

## Footprint state

- assigned: **72**
- deliberately empty/unfrozen: **7** (`J3`, `J101`, `J4`, `J5`, `J6`, `J8`, `J9`)

`J8` is deliberately unresolved. The desired debug target is TC2030-IDC-NL 6-pin SWD, while the current validated schematic still contains the earlier 8-pin debug header. A six-pad footprint must not be attached to the eight-pin symbol merely to silence the footprint audit.

## Reproducibility

The repository stores a compressed native-r7 source payload plus a manifest containing source and post-materialization SHA-256 hashes. The materializer rejects unsafe archive paths, verifies all source hashes, applies reviewed footprint assignments, and verifies all resulting file hashes.

## Important limitation

**ERC 0 does not mean manufacturing-ready.** Physical interfaces, PCB geometry, Bio Board safety hardware and PCB DRC/DFM remain release gates.
