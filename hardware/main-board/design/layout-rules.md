# Layout rules — Phase 1

## RF
- Copy Nordic QFAA reference matching/harmonic-filter topology.
- Preserve relative placement, grounding, and RF component orientation.
- Keep an antenna matching pi-network/tuning provision.
- RF transmission line is controlled impedance after matching network.
- No battery, display ground shield, EDA electrode metal, or steel midframe in
  the antenna keep-out.
- Final RF values are subject to VNA/tuning after enclosure assembly.

## nRF54L15
- Continuous GND reference immediately below top layer.
- Decouplers at the exact supply pins they serve.
- DCC inductor loop extremely small.
- Follow Nordic's special C6 grounding instruction near VSS_PA/die pad.

## nPM1300
- PMIC, BUCK inductors, and input/output caps tightly clustered.
- Keep SW1/SW2 copper small and away from sensor interface.
- Do not route Bio analog/interconnect traces under switching nodes.
- Wide, short VSYS/VBAT/VOUT paths.

## Display
- QSPI group length-matched reasonably; no need for extreme DDR constraints at
  intended clock rates.
- Avoid running display clock parallel to PPG/EDA connector traces.
- Put panel ESD parts at connector if panel FPC exits enclosure/has exposed path.

## Haptic
- LRA current path isolated from Bio interface and temperature sensing.
- Haptic driver supply decoupling at device.
- Mechanical vibration coupling is handled in enclosure design.

## Testability
- Pogo access to SWDIO, SWDCLK, nRESET, GND, +1V8.
- Test points for VBAT, VSYS, +1V8, +3V0, CHG_5V.
- Optional 0-ohm/current-measurement links on early prototypes where practical.
