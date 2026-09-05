# AegisBioWatch Main Board PCB floorplan — Phase 1 r10

## Status

This file set is a **provisional PCB floorplan**, not a Gerber/production PCB release.

The electrical authority remains the validated **Phase 1 r8 native schematic** until the remaining J3/J5/J6 physical-interface gates are closed and the schematic is deliberately synchronized into the PCB.

## Mechanical envelope

| Item | r10 planning value |
|---|---:|
| Case maximum | 45.0 × 39.5 mm |
| Provisional Main Board | 41.0 × 34.0 mm |
| Main Board thickness | 0.8 mm planning value |
| Display candidate envelope | 40.28 × 34.12 mm when rotated into the case |
| Battery candidate | 24.5 × 36.0 × 4.0 mm |
| Bio Sensor Board reserve | 12.0 × 12.5 mm |
| LRA reserve | Ø10.4 mm |

The case top-left is the mechanical datum `(0,0)`. The provisional Main Board starts at `(2.0, 2.75)` in that datum.

## Planning stack-up

r10 uses a **four-layer planning stack** only:

1. F.Cu — 18 µm
2. 0.10 mm prepreg
3. In1.Cu — continuous GND reference, 18 µm
4. 0.526 mm core
5. In2.Cu — power / low-speed routing, 18 µm
6. 0.10 mm prepreg
7. B.Cu — 18 µm

The fabricator stack-up is **not frozen**. No 50 Ω trace width is frozen until the selected PCB house provides actual dielectric thickness / Dk / copper data.

Nordic's PMIC PCB guidance recommends at least four layers because close ground planes improve return-current paths, crosstalk, EMI behavior and controlled impedance. The nPM1300 QFN reference layout also places no components on the bottom layer.

## Placement strategy

### RF / MCU

`U1 + RF + XO` is reserved in the upper-right region immediately below the RF window.

The RF window is a conservative **12.0 × 6.25 mm all-copper/all-component keep-out**. It also implies a plastic/non-metallic enclosure window: battery foil, display metal, magnets and enclosure metal must not intrude into this zone.

The exact ANT matching layout is **not redrawn from memory**. The local ANT/VSS_PA/DECRF matching region must be reproduced from the Nordic QFAA reference layout before routing is released. In particular, Nordic notes that the RF decoupling capacitor return uses pin 32 / VSS die pad rather than a generic direct ground-plane connection.

### PMIC

The `U2 nPM1300` cluster is isolated in the lower-left zone.

Rules for the detailed placement phase:

- keep BUCK input/output switching loops inside the cluster;
- put input/output capacitors directly at their corresponding power/ground pins;
- keep PVSS local return geometry faithful to the Nordic QFN reference layout;
- do not run display, sensor, crystal or RF traces through the switching-current region.

### Storage / haptic

The Flash sits between PMIC and MCU, shortening the AUX SPI path without entering the RF matching region.

The DRV2605L is adjacent to the LRA reserve. The C10-100 itself is treated as an enclosure-mounted mechanical item; its PCB solder termination must not be used as mechanical retention.

### Back-side volume

The 24.5 × 36 mm battery is rotated vertically to preserve the upper-right RF window and leave a right-side column for the Bio Sensor Board and LRA.

The Bio Sensor Board is reserved on the rear/right-central area because it must ultimately interface to the skin-facing sensor window.

## Interface zones

The following are already electrically selected and receive physical placement zones:

- J7 — Hirose FH12-20S-0.5SH Main↔Bio
- J8 — Tag-Connect TC2030 SWD
- J9 — Panasonic EVQPUK02K side button
- J101 — Panasonic EVQPLDA15 ship/wake button
- J4 — C10-100 LRA lead termination

The following remain intentionally provisional:

- **J3 magnetic dock:** exact S70 watch-side land, contact pitch, pogo compression and case datum
- **J5 AMOLED:** official 24-pin FPC definition, rail requirements, timing and power sequence
- **J6 touch:** exact physical connector and I/O voltage / level-shifter decision

## KiCad validation

`AegisBioWatch-MainBoard-Floorplan-r10.kicad_pcb` was loaded by `kicad-cli 9.0.9` and checked with:

```bash
kicad-cli pcb drc --format json --severity-all \
  -o drc-r10.json AegisBioWatch-MainBoard-Floorplan-r10.kicad_pcb
```

Result:

```text
Found 0 violations
Found 0 unconnected items
```

**Important:** this only validates the standalone floorplan geometry. It is **not** the final electrical PCB DRC, because r8 footprints/nets have not yet been synchronized into this board.

## Next PCB step

1. Close J3 land/contact geometry if Harwin S70 CAD/land data is obtained.
2. Obtain the GL175AMC10C/CST820B supplier drawing before freezing J5/J6.
3. Import/synchronize the r8 native schematic into a production PCB file.
4. Place U1 and the RF matching network by copying the verified Nordic QFAA reference geometry.
5. Place nPM1300 and its passives from the Nordic QFN reference geometry.
6. Route power first, then crystals/RF, then display buses, then remaining digital buses.
7. Add solid In1 GND plane, controlled via stitching, and final keep-outs.
8. Run full PCB DRC/DFM after fab stack-up and controlled impedance are frozen.

## Primary references

- Nordic nRF54L15 Product Specification — QFN48 PCB layout example:
  `https://docs.nordicsemi.com/r/bundle/ps_nrf54l15/page/chapters/ref_circuitry.html-layout`
- Nordic nPM1300 Product Specification — reference circuitry / PCB guidelines:
  `https://docs.nordicsemi.com/r/bundle/ps_npm1300/page/chapters/hw_layout/ref_circuitry/frontpage.html`
- Nordic Power Management PCB Guidelines — PCB stack-up:
  `https://docs.nordicsemi.com/r/bundle/nwp_050/page/wp/nwp_050/pcb_stackup.html`
