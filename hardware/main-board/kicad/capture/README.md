# AegisBioWatch Main Board — capture/migration sources

## Canonical r7 source

Do **not** use the legacy/intermediate files in this directory as the Phase 1 r7 electrical authority.

Materialize the validated native KiCad 9 project from the repository root:

```bash
python3 tools/materialize-native-r7.py
```

The canonical project will be written to:

```text
hardware/main-board/kicad/native-r7/
```

Open:

```text
hardware/main-board/kicad/native-r7/AegisBioWatch-MainBoard-Rev0.kicad_sch
```

The payload and materializer are hash-verified. See:

- `hardware/main-board/kicad/native-r7-payload/manifest.json`
- `tools/materialize-native-r7.py`
- `docs/native-kicad-r7.md`
- `docs/erc-r7.json`

## Validation

KiCad CLI: **9.0.9**

Integrated native ERC with `--severity-all`: **0 violations**.

Critical pin-to-net checks: **63/63 pass**.

Footprints: **72 assigned / 7 deliberately unresolved**.

## This directory

The `.sch`, `.lib`, cache and other files retained here are migration/history inputs. They may be useful for audit and comparison but are not the r7 release source.

**Do not release Gerbers yet.** Physical interfaces, PCB stack-up/RF layout, Bio Board safety hardware and PCB DRC/DFM remain open release gates.
