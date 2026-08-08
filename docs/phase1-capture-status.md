# Phase 1 capture status — Rev.0 r7

## Completed

- Native KiCad **9.0.9** hierarchical schematic is reproducible from the hash-verified r7 payload.
- Integrated ERC with `--severity-all`: **0 violations**.
- Critical exported-netlist validation: **63/63 pass**.
- Production/package footprints assigned to **72** schematic components.
- Battery connector uses the KiCad Hirose DF57H-3P footprint.
- Main↔Bio connector uses the KiCad Hirose FH12-20S-0.5SH footprint.
- nRF54L15-QFAA / nPM1300 pin-to-net mapping remains validated after footprint assignment.
- PVSS1/PVSS2 local switching returns retain explicit NetTie semantics into the same continuous GND plane.

## Reproducing the native project

Run from the repository root:

```bash
python3 tools/materialize-native-r7.py
cd hardware/main-board/kicad/native-r7
kicad-cli sch erc --format json --severity-all \
  -o erc-r7.json AegisBioWatch-MainBoard-Rev0.kicad_sch
```

The materializer verifies the archive SHA-256, source-file hashes, applies the reviewed footprint assignments deterministically, and verifies the resulting native files against post-materialization hashes.

## PCB-release status

**NOT manufacturing-ready.**

Seven physical interfaces/footprints remain intentionally unresolved:

- `J3` magnetic charging dock
- `J4` C10-100 LRA mechanical/electrical attachment
- `J5` AMOLED physical FPC/module interface
- `J6` touch physical interface
- `J8` debug connector: canonical r7 still uses the earlier 8-pin debug header; target is TC2030-IDC-NL 6-pin and requires a deliberate pin-map refactor
- `J9` side button contact
- `J101` ship/wake button

The next phase is physical-interface/footprint freeze and PCB floorplanning, not Gerber release.
