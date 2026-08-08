# AegisBioWatch Main Board — KiCad Phase 1 r7

## Source of truth

The authoritative design is now the native KiCad 9 hierarchical project:

- `AegisBioWatch-MainBoard-Rev0.kicad_pro`
- `AegisBioWatch-MainBoard-Rev0.kicad_sch`

Child sheets:

- `MCU_RF_CLOCK.kicad_sch`
- `PMIC_CHARGER.kicad_sch`
- `STORAGE_HAPTIC.kicad_sch`
- `DISPLAY_TOUCH.kicad_sch`
- `BIO_INTERFACE.kicad_sch`
- `SYSTEM_POWER.kicad_sch`

Native local libraries:

- `AegisBioWatch.kicad_sym`
- `AegisBioWatch.pretty/`
- `sym-lib-table`
- `fp-lib-table`

The legacy `.sch`, `.lib` and cache files are retained only for migration/history
and must not be treated as the r7 electrical authority.

## Verified toolchain

`kicad-cli 9.0.9`

## ERC

The complete hierarchical project passes:

```text
Found 0 violations
```

The machine-readable result is stored in `docs/erc-r7.json`.

## Generated outputs

`../generated/` contains:

- `AegisBioWatch-MainBoard-Rev0.net`
- `BOM-r7.csv`

These are generated from the native root schematic.

## Manufacturing status

**NOT manufacturing-ready.** ERC is clean and 71/77 BOM rows have footprints,
but six enclosure/mechanical-interface footprints, display FPC/electrical data,
PCB stack-up/RF layout, protected battery-pack details, and Bio Board safety
circuitry remain open release gates.
