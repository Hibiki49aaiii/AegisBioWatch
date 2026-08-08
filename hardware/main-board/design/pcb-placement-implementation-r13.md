# PCB placement implementation — Phase 1 r13

## Scope

r13 converts the staged nPM1300 area from r11 into a deterministic reference-style placement implementation.

The source remains the hash-verified r11 real-net placement seed. `U2` stays at the r11 PMIC-zone datum; the nPM1300 local passives are repositioned from the **actual U2 pad geometry and AegisBioWatch net names**, not from third-party absolute coordinates.

This revision is still **not manufacturing authority** and must not be used for Gerber release.

## Authority

Physical-layout authority for this block is Nordic Semiconductor documentation:

1. nPM1300 QEAA/QFN current reference-layout release (1.2 at r13 implementation time);
2. nPM1300 Product Specification, configuration 1 reference circuitry and QFN32 pin assignment;
3. Nordic nPM1300/nPM1304 Hardware Design Guidelines for component placement, switching-current loops and ground-plane integrity.

The earlier `hlord2000/nPM1300-Stamp` review remains density/adjacency evidence only. r13 does **not** copy its component coordinates.

## Electrical configuration retained

No r8 electrical topology is changed by r13.

- BUCK1: `+1V8`, VSET1 = 47 kΩ
- BUCK2: `+3V0`, VSET2 = 150 kΩ
- L101/L102: 2.2 µH class
- PVSS1/PVSS2: project-local switching return nets
- NT101/NT102: explicit transition from local PVSS return to the continuous GND system
- In1.Cu role: continuous GND; no split ground plane

The current Nordic QEAA reference-layout 1.2 release explicitly includes GND net-ties to PVSS1/PVSS2. The exact final top-copper/via shape still requires board-level KiCad review and is not inferred from a third-party board.

## Implemented placement policy

`tools/materialize-pcb-r13.py` first materializes r11 and refuses to continue unless the r11 PCB SHA-256 matches the recorded electrical-placement source.

It then checks critical U2 pad/net assignments before moving any component.

### BUCK block

The BUCK-side coordinate frame is derived from U2 pins 2…6.

- `C103` / `C104`: VSYS input capacitors placed against the PVDD/PVSS1/PVSS2 side.
- `C114`: high-frequency application decoupling kept immediately at the PVDD/VSYS side.
- `L101` / `L102`: placed radially from SW1/SW2 to minimize SW copper length.
- `C107` / `C108`: output capacitors staged directly beyond their corresponding inductors, with their local-return orientation facing the PMIC return region.
- `NT101` / `NT102`: placed adjacent to the corresponding local-return region so the local switching return can enter the continuous GND reference over a short transition.

This implements the Nordic current-loop rules: minimize the high-di/dt input loop, keep PVDD/PVSS/SW components close, and retain an intact second-layer ground reference.

### Other nPM1300 local passives

The following are placed from the relevant U2 package pins rather than arbitrary board coordinates:

- `C101`: VBUS / charging-input decoupling
- `C102`: VSYS decoupling
- `C105`: VBUSOUT decoupling
- `C106`: VBAT decoupling
- `C113`: VDDIO / +1V8 decoupling
- `R101` / `R102`: VSET1/VSET2
- `C109` / `C110`: DISP_SW output capacitance
- `C111` / `C112`: BIO_SW output capacitance
- `R105` / `R106`: optional LS/LDO input links
- `R103` / `R104`: optional TWI pull-ups

## Reproduction

From repository root:

```bash
python3 tools/materialize-pcb-r13.py
```

Generated files:

```text
hardware/main-board/pcb/placement-r13/AegisBioWatch-MainBoard-Placement-r13.kicad_pcb
hardware/main-board/pcb/placement-r13/AegisBioWatch-MainBoard-Placement-r13.kicad_pro
hardware/main-board/pcb/placement-r13/placement-implementation-r13.json
```

## KiCad validation requirement

Run with **KiCad CLI 9.0.9**:

```bash
cd hardware/main-board/pcb/placement-r13
kicad-cli pcb drc --format json --severity-all \
  -o drc-r13.json AegisBioWatch-MainBoard-Placement-r13.kicad_pcb
```

Report these separately:

- rule violations;
- unconnected items.

r13 currently changes placement only, so the intended pre-routing topology baseline remains 186 unconnected items. This number is an expectation to be checked by KiCad, not a substitute for the check.

The branch workflow `.github/workflows/phase1-r13-kicad.yml` reproduces r11, runs the r11 baseline DRC, materializes r13, runs the r13 DRC and preserves the generated board plus DRC evidence as a workflow artifact.

**Do not describe r13 as DRC-clean until that KiCad run reports rule violations = 0.**

## Routing gate after placement validation

After the r13 placement itself is KiCad-clean, routing begins in this order:

1. short local PVSS/GND transition and GND stitching strategy;
2. VSYS/PVDD input loop;
3. SW1/L101 and SW2/L102;
4. +1V8/+3V0 output paths and output-cap returns;
5. VBAT and charging input;
6. remaining PMIC low-speed/control nets.

Power copper must be kept away from the nRF54L15 RF reserve. In1.Cu remains continuous GND.

## Unchanged release gates

r13 does not close any supplier- or fabrication-specific unknown by assumption. The following remain gated, among others:

- J3 watch-side magnetic-dock contact land pattern;
- J5 AMOLED official FPC pin definition;
- J6 touch physical/electrical interface;
- protected battery-pack drawing and limits;
- actual procured nPM1300 build code / applicable errata;
- performance-critical capacitor effective capacitance and final MPNs;
- fabricator stack-up and final RF impedance geometry;
- nRF54L15 RF/crystal reference placement and antenna tuning;
- Bio Board electrode disconnect/high-Z charging safety;
- fully routed PCB with KiCad violations = 0 and unconnected = 0;
- DFM and Rev.0 prototype bring-up.

## Privacy boundary

This hardware revision stores only engineering abstractions and contains no individual health history, private messages, medication names/doses, or identifiable health information.
