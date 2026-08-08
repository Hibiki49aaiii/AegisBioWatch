# Phase 1 capture status — Rev.0 r7

## Completed through r7

- Native KiCad 9.0.9 hierarchical Main Board project created.
- Native project-specific symbol library created and validated.
- Native project-specific footprint library created and validated.
- nRF54L15-QFAA and nPM1300 custom symbols normalized to KiCad schematic grid.
- MP06003 HFXO represented as a four-pad device with grounded lid pads.
- MCU/RF, PMIC/charger, storage/haptic, display/touch, Bio interface and system
  power are connected as child sheets under one Main Board root.
- Real KiCad ERC: **0 violations**.
- Native netlist export: PASS.
- Native BOM export: PASS.
- Privacy scan: PASS.

## r7 validation result

| Check | Result |
|---|---|
| KiCad version | 9.0.9 |
| Hierarchical sheets | 7 including root |
| ERC | 0 violations |
| Custom native symbols | 8 |
| Reviewed custom footprints | 4 |
| Native BOM rows | 77 |
| BOM rows still without footprint | 6 |
| Netlist export | PASS |
| BOM export | PASS |
| Privacy scan | PASS |

## Still blocked before PCB release

- Resolve the six remaining enclosure/mechanical footprint gates (dock, LRA, display/touch and buttons).
- Freeze exact PMIC/nRF passive MPNs where electrical performance depends on
  DCR, Q, tolerance, DC-bias or effective capacitance.
- Freeze Main↔Bio FPC cable length/contact-side/stiffener geometry.
- Obtain the official AMOLED/touch FPC pinout, rail requirements and power
  sequence.
- Close touch I/O voltage/level-shifter decision.
- Freeze the protected battery-pack construction, harness pin numbering and wire colors.
- Close magnetic-dock contact-drop/ESD/reverse-polarity validation.
- Freeze PCB fab stack-up and calculate controlled-impedance RF geometry.
- Reproduce Nordic RF/current-return placement constraints in PCB layout.
- Capture and review the Bio Sensor Board, including hardware electrode
  disconnect/high-Z behavior during charging.
- Run PCB DRC, DFM and assembled-prototype bring-up tests.

**Do not release Gerbers yet.**
