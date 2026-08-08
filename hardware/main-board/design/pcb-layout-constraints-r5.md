# Phase 1 r5 — PCB / RF layout constraints

Status: **pre-layout authority document / not manufacturing release**

## Layer stack

Use **at least 4 layers** for Rev.0.

Preferred baseline:
1. L1 — components, RF, short high-current power loops, critical signals
2. L2 — continuous solid GND plane
3. L3 — power distribution and low/medium-speed signals
4. L4 — low-speed signals, test access, ground pour where useful

Do not route ordinary signals on L2. Short escape routing is only acceptable where unavoidable and must not cut the return path below PMIC switching loops or the nRF RF path.

The exact 50 Ω RF trace width is **not guessed**. It is calculated after the PCB fabricator stack-up, copper thickness, dielectric thickness, and dielectric constant are frozen.

## nRF54L15 RF / power

- Copy the QFAA reference relative placement and return-current geometry as closely as mechanics permit.
- Keep the ANT matching/harmonic network on L1 with a continuous L2 GND reference.
- Preserve a tuning provision between the Nordic reference network and final antenna.
- Follow Nordic's special RF capacitor return geometry through the pin-32 / VSS die-pad region; do not use an arbitrary remote ground point.
- No battery cell, display metal/shield, haptic mass, EDA electrode metal, strap buckle, or steel enclosure feature inside the final antenna keep-out.
- Final RF values are subject to VNA/OTA tuning in the actual enclosure.

## nPM1300

- Put the PMIC, BUCK inductors, BUCK input caps, and BUCK output caps in one compact power island.
- Minimize the loops PVDD → switch → inductor/output → PVSS.
- Place each BUCK input capacitor as close as possible to PVDD and its corresponding local PVSS return.
- Keep SW1/SW2 copper short and small. Do not route sensor, touch, crystal, or RF traces under or beside the switch nodes.
- Keep `PVSS1_LOCAL` and `PVSS2_LOCAL` as very short top-layer high-current return regions and join each to the **same continuous L2 GND plane** at the explicit net-tie/via location, matching the Nordic QFN reference intent.
- The net-tie is a schematic/DRC boundary for return-current placement; it must **not** create a split, moat, or star-ground partition in L2.
- The physical net-tie copper/via geometry is layout-specific and must be frozen by side-by-side comparison with the Nordic QFN reference layout; do not assume the generic KiCad 0.5 mm net-tie footprint is production-authoritative.
- Use ground vias directly beside the local power-ground copper and capacitor ground pads.
- Keep L2 intact directly below all PMIC high-current paths.
- Keep VBAT, VBUS, AVSS, and battery/NTC routing away from switch nodes and display/haptic clocks.

## Sensor coexistence

- Do not route `AUX_SPI_SCK`, display QSPI clock, haptic outputs, SW1, or SW2 near the Bio connector analog-sensitive side.
- The PPG optical module and skin-temperature sensor belong on the Bio Sensor Board, physically separated from PMIC/MCU heat.
- EDA/ECG electrode paths must not share noisy return current with the charger, haptic driver, display, or BUCK loops.
- Charging and on-body electrode acquisition are mutually exclusive in the prototype architecture.

## Power-budget gate

Architectural limits:
- BUCK1: 200 mA
- BUCK2: 200 mA
- LOADSW/LDO in LDO mode: 50 mA
- LOADSW/LDO in load-switch mode: 100 mA

Before assigning `DISP_SW` or `BIO_SW` to a final load, record startup, average, and peak current for AMOLED/touch, PPG/AFE, EDA, IMU, haptic/LRA, Flash, and always-on logic.

If any provisional rail exceeds margin, use a dedicated external regulator/load switch rather than overloading nPM1300.

## Placement freeze checklist

- [ ] fab stack-up frozen
- [ ] 50 Ω RF geometry calculated by fab/field solver
- [ ] antenna model and keep-out frozen with enclosure
- [ ] nRF reference layout side-by-side review complete
- [ ] PMIC switch-loop side-by-side review complete
- [ ] no L2 splits under RF or PMIC power loops
- [ ] Bio analog/optical region separated from PMIC/haptic/display noise
- [ ] thermal isolation path for skin-temperature sensor frozen
- [ ] current-budget gate closed
