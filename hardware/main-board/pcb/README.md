# AegisBioWatch Main Board PCB work

## Current PCB-stage artifacts

### r10 — floorplan

- `AegisBioWatch-MainBoard-Floorplan-r10.kicad_pcb`

r10 defines the provisional 41 × 34 mm board envelope, 0.8 mm / four-layer planning stack, mechanical projections and RF keep-outs. It is a floorplan-only artifact.

### r11 — electrically synchronized placement seed

Materialize from repository root:

```bash
python3 tools/materialize-pcb-r11.py
```

Output:

```text
hardware/main-board/pcb/placement-r11/
```

The r11 board imports the validated r8 electrical nets and the 76 currently frozen footprints into the r10 floorplan. `J3`, `J5` and `J6` remain intentionally absent until their physical interfaces are frozen.

Validate the unrouted baseline with:

```bash
cd hardware/main-board/pcb/placement-r11
kicad-cli pcb drc --format json --severity-all \
  -o drc-r11.json AegisBioWatch-MainBoard-PlacementSeed-r11.kicad_pcb
```

Expected pre-routing baseline:

```text
0 rule violations
186 unconnected items
```

The 186 unconnected items are intentional ratsnest connections. **Routing has not started.** r11 is not a production PCB and not a Gerber authority.

## Authority model

- Electrical authority: validated Phase 1 **r8** native schematic.
- Physical-interface review: **r9**.
- Mechanical/floorplan constraints: **r10**.
- PCB net/footprint placement seed: **r11**.

Critical U1/RF, U2/PMIC and PVSS NetTie coordinates in r11 are seed/staging positions. Reproduce the corresponding Nordic reference placement/current-return geometry before routing these blocks.

See:

- `hardware/main-board/design/pcb-floorplan-r10.md`
- `hardware/main-board/design/pcb-placement-seed-r11.md`
- `docs/pcb-floorplan-validation-r10.json`
- `docs/pcb-placement-seed-validation-r11.json`
