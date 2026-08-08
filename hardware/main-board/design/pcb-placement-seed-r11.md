# AegisBioWatch Main Board PCB placement seed — Phase 1 r11

## Status

r11 is an **electrically synchronized, completely unrouted placement seed**.

It combines:

- r8 validated electrical source / XML netlist;
- r9 physical-interface selections where frozen;
- r10 provisional 41 × 34 mm PCB floorplan and RF/mechanical keep-outs.

It is not a routed PCB, not a DFM release and not a Gerber authority.

## Electrical synchronization

| Check | Result |
|---|---:|
| Schematic components | 79 |
| Footprints imported | 76 |
| Intentionally absent | J3, J5, J6 |
| Nets represented | 86 |
| Source XML pin-net assignments audited | 268 |
| Pad/net mismatches | 0 |
| Unexpected pad nets | 0 |
| Source pins missing from selected footprints | 0 |

The intentionally absent components remain the three supplier/mechanical gates:

- `J3` magnetic-dock watch-side contact geometry;
- `J5` AMOLED physical FPC;
- `J6` touch physical interface.

## KiCad DRC baseline

Validated with KiCad CLI 9.0.9.

```text
Found 0 violations
Found 186 unconnected items
```

This is the correct r11 baseline: geometry/placement rule violations are zero under the provisional r11 rules, while **186 ratsnest connections remain because routing has not started**.

Do not describe r11 as a completed PCB DRC pass.

Hard geometry categories currently at zero:

- courtyard overlap;
- copper clearance;
- shorting items;
- drill-out-of-range under the r11 planning rule;
- copper-to-edge clearance;
- solder-mask bridge.

## Planning rules are not fabrication rules

The r11 project uses the following planning minima only:

- minimum clearance: 0.10 mm;
- minimum copper-to-edge: 0.20 mm;
- minimum through-hole drill: 0.20 mm.

The 0.20 mm drill planning value is required by the selected nPM1300 QFN thermal-via footprint. Actual via technology, finished drill tolerance, annular ring and PCB-house capability must be frozen with the fabricator before release.

## Critical-placement warning

### nRF54L15 / RF

`U1`, its crystals and RF matching passives are currently **seed positions only**.

Before routing this block, reproduce the verified Nordic nRF54L15-QFAA reference geometry rather than optimizing it from the seed. The ANT matching network, VSS_PA / pin-32 return and RF decoupling geometry are layout-critical. The exact antenna radiator and enclosure tuning remain separate release gates.

### nPM1300

`U2`, its BUCK inductors/capacitors and local return components are also **seed positions only**.

Before routing, reproduce the Nordic QFN reference placement/current-return topology: compact switching loops, passives close to the corresponding pins, and the intended PVSS local-return geometry into the continuous ground reference.

### PVSS NetTies

`NT101` / `NT102` are deliberately **staged, not final** in r11. Their final copper/via geometry must follow the reviewed nPM1300 layout rather than the seed coordinates.

## Routing order after placement freeze

1. Reproduce/freeze the nPM1300 power cluster.
2. Reproduce/freeze the nRF54L15 RF / HFXO / LFXO cluster.
3. Establish the solid In1 GND reference and stitching strategy.
4. Route VBAT / VSYS / BUCK outputs and other high-current paths.
5. Route crystals and RF path.
6. Route display QSPI and AUX SPI.
7. Route Main↔Bio, I2C, interrupt/control lines and SWD.
8. Complete ground pours / stitching and re-run DRC.
9. Freeze the fabricator stack-up, calculate final 50-ohm geometry and perform DFM review.

## Reproduction

From repository root:

```bash
python3 tools/materialize-pcb-r11.py
cd hardware/main-board/pcb/placement-r11
kicad-cli pcb drc --format json --severity-all \
  -o drc-r11.json AegisBioWatch-MainBoard-PlacementSeed-r11.kicad_pcb
```

Expected r11 result before routing:

```text
0 rule violations
186 unconnected items
```

## References

Use the current Nordic reference circuitry / layout documentation as the physical-layout authority for the nRF54L15-QFAA and nPM1300 blocks. The r11 seed itself must never be treated as a replacement for those reference layouts.
