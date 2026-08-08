# Phase 1 capture status — Rev.0 r8

## Verified through r8

- KiCad CLI: **9.0.9**
- Integrated native ERC (`--severity-all`): **0 violations**
- BOM rows: **79**
- Footprints assigned: **76/79**
- Remaining physical-interface footprint gates: **3** — J3, J5, J6
- r8 interface netlist checks: **12/12 PASS**
- Battery connector remains Hirose DF57H-3P.
- Main↔Bio connector remains Hirose FH12-20S-0.5SH.
- nRF54L15-QFAA / nPM1300 validated pin-to-net mapping and PVSS NetTie semantics are retained.
- Privacy scan: **PASS**

## Reproducing the native project

Run from the repository root:

```bash
python3 tools/materialize-native-r8.py
cd hardware/main-board/kicad/native-r8
kicad-cli sch erc --format json --severity-all \
  -o erc-r8.json AegisBioWatch-MainBoard-Rev0.kicad_sch
```

The r8 materializer first hash-verifies/materializes r7, verifies the expected r7 base hashes, applies the compact hash-verified r7→r8 unified diff, and then verifies every authoritative r8 file against its final SHA-256.

## Interfaces closed in r8

- `J8`: Tag-Connect TC2030 six-pin SWD target.
- `J9`: Panasonic EVQPUK02K side button.
- `J101`: Panasonic EVQPLDA15 ship/wake button.
- `J4`: C10-100 LRA direct-solder lead termination with strain-relief footprint.

## PCB-release status

**NOT manufacturing-ready.**

Three physical interfaces/footprints remain intentionally unresolved:

- `J3` magnetic charging dock physical contact geometry
- `J5` AMOLED supplier FPC pinout, rails and power sequence
- `J6` touch physical connector and I/O voltage decision

PCB stack-up/controlled impedance/antenna keep-out, Bio Board charging-time electrode disconnect, PCB DRC/DFM and prototype bring-up also remain release gates.

**Do not release Gerbers yet.**
