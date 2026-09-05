# Layout rules — Phase 1

## RF
- Use the **revision-matched Nordic QFAA reference design** for the actual procured nRF54L15 silicon revision; do not assume a universal QFAA reference-layout release.
- Preserve matching/harmonic-filter topology, relative placement, grounding, component orientation, local via pattern, and reference-controlled trace geometry.
- Translate Nordic reference designators by **electrical function**, not by equal reference number.
- In the reviewed QFN48 reference example, Nordic's first 1.5 pF RF shunt (`C6` in that reference) uses the VSS_PA / exposed-die-pad return. In AegisBioWatch the corresponding part is **C10**, not Aegis C6.
- If the selected revision-matched Nordic reference design requires an isolated-layer return for its following RF shunt (for example the `C9` rule present in reviewed reference material), apply that rule to the corresponding Aegis functional part (**currently C11, 2.0 pF**), not by reference-number matching. Confirm this directly against the selected silicon-revision design files before copper freeze.
- Keep an antenna tuning provision beyond the mandatory SoC harmonic/matching network as required by the antenna implementation.
- RF transmission line becomes controlled impedance only after actual fabricator stack-up is frozen.
- Do not present a provisional width from the planning stack as manufacturing authority.
- No battery, display ground shield, electrode metal, or steel midframe in the antenna keep-out.
- No PMIC SW node or high-edge-rate display clock may intrude into the RF reserve.
- Final RF values are subject to VNA/tuning after enclosure assembly.

## nRF54L15
- Identify actual silicon revision/build code before freezing RF, crystal, or internal-regulator reference placement.
- Use the Nordic compatibility matrix to select the matching QFAA design-file release and review the corresponding errata.
- Continuous GND reference immediately below top layer except where the selected Nordic RF reference explicitly requires a special layer-isolated return structure.
- Decouplers at the exact supply pins they serve.
- DCC inductor loop extremely small.
- `L1/C6/FB1/C7/C8/C9` are treated as a reference-layout-controlled internal-supply cluster; note that **Aegis C6 is the DECD 2.2 µF capacitor**, not Nordic reference-designator C6 from the RF network.
- `Y1` HFXO and `Y2` LFXO routes remain short, quiet, and separated from PMIC switching and fast display signals.

## nPM1300
- Nordic nPM1300 QEAA reference layout and hardware-design guidance are physical authority.
- PMIC, BUCK inductors, and input/output caps tightly clustered.
- Minimize the high-di/dt input loops and SW1/SW2 copper area.
- PVSS1/PVSS2 remain short local switching-return nets and enter the continuous board GND system through the explicit NetTie topology used by the project.
- In1.Cu remains a continuous GND plane; do not split it around the PMIC.
- Keep SW1/SW2 copper away from the nRF RF/crystal reserve and sensor interface.
- Do not route Bio analog/interconnect traces under switching nodes.
- Wide, short VSYS/VBAT/+1V8/+3V0 paths; final widths must still satisfy current, thermal, fab and clearance constraints.

## Display
- QSPI group length-matched reasonably; no need for extreme DDR constraints at intended clock rates.
- Avoid running display clock parallel to PPG/EDA connector traces.
- Put panel ESD parts at connector if panel FPC exits enclosure/has exposed path.
- J5/J6 routing remains gated until the exact supplier FPC/touch electrical definitions are obtained.

## Haptic
- LRA current path isolated from Bio interface and temperature sensing.
- Haptic driver supply decoupling at device.
- Mechanical vibration coupling is handled in enclosure design.

## Testability
- Pogo access to SWDIO, SWDCLK, nRESET, GND, +1V8.
- Test points for VBAT, VSYS, +1V8, +3V0, CHG_5V.
- Optional 0-ohm/current-measurement links on early prototypes where practical.

## Validation language
- Run KiCad's own ERC/PCB DRC for release evidence; project Python audits are supplementary only.
- Report `rule violations` and `unconnected items` separately.
- Do not say `PCB DRC PASS` while intentional/unintentional unrouted connections remain.
