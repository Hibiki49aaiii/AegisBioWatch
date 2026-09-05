# nRF54L15-QFAA reference placement — Phase 1 r13

## Scope

This note defines the physical-layout authority and mapping rules for the U1 / nRF54L15-QFAA block before any RF-critical coordinates are frozen.

It does **not** replace the Nordic reference layout, does not freeze final RF impedance geometry, and does not authorize Gerber release.

## Authority

For the selected `nRF54L15-QFAA` QFN48 package, physical authority is Nordic Semiconductor's reference design that corresponds to the **actual procured nRF54L15 silicon revision**, together with that revision's datasheet/errata and the current PCB-layout guidance.

The Nordic nRF54L15 compatibility matrix currently maps QFAA revisions to different recommended design-file releases:

- Engineering B → QFAA reference design `0.8`
- Revision 1 → QFAA reference design `0.7`
- Revision 2 → QFAA reference design `1.0`

Therefore **QFAA does not imply one universal reference-layout version**. r13 must not freeze the RF/DC-DC/crystal geometry against `0.8` until the actual device revision/build code is known. The project must identify the procured silicon revision, select the matching Nordic design files, and re-check the applicable errata before release.

Package geometry remains QFN48, nominal 6.0 mm × 6.0 mm, 0.40 mm pitch, exposed die pad.

## Official QFAA dedicated-pin mapping used by r13

The current Nordic QFN48 pin table gives the following critical pins:

- pin 1: `XL1`
- pin 2: `XL2`
- pin 25: `SWDIO`
- pin 26: `SWDCLK`
- pin 30: `nRESET`
- pin 31: `ANT`
- pin 32: `VSS_PA`
- pin 33: `DECRF`
- pin 34: `XC1`
- pin 35: `XC2`
- pin 43: `DECA`
- pin 44: `VSS`
- pin 45: `DECD`
- pin 46: `DCC`
- pins 47 and 48: `VDD`
- exposed die pad / pin 49: `VSS`

The exposed die pad must be connected to the device ground system as required by Nordic.

## AegisBioWatch functional mapping

The project does not reuse Nordic reference designators blindly. Functional identity is the authority when translating a Nordic reference circuit into AegisBioWatch designators.

### Internal regulator / RF supply

AegisBioWatch currently implements:

- `L1`: `NRF_DCC` ↔ `NRF_DECD`, 4.7 µH
- `C6`: `NRF_DECD` → GND, 2.2 µF
- `FB1`: `NRF_DECA_RF` ↔ `NRF_DECD`, 120 Ω @ 100 MHz ferrite bead
- `C7`: `NRF_DECA_RF` → GND, 2.2 µF
- `C8`: `NRF_DECA_RF` → GND, 10 nF
- `C9`: `NRF_DECA_RF` → GND, 2.2 nF
- `DECA` pin 43 and `DECRF` pin 33 share `NRF_DECA_RF`

These values/topology are the project's current r8 electrical authority. Final performance-critical passive values/MPNs must be re-checked against the Nordic design files recommended for the actual procured silicon revision; the reference circuitry has changed across nRF54L15 revisions during product maturation.

### RF matching / harmonic filter

AegisBioWatch currently implements:

- `L2`: 2.7 nH, `RF_MCU` → `RF_A`
- `C10`: 1.5 pF, `RF_A` → GND
- `L3`: 3.5 nH, `RF_A` → `RF_B`
- `C11`: 2.0 pF, `RF_B` → GND
- `L4`: 3.5 nH, `RF_B` → `RF_ANT`
- `C12`: 0.3 pF, `RF_ANT` → GND

These nominal values match the configuration reviewed for the current r8 capture, but the **actual-revision Nordic BOM/layout remains release authority**. Antenna/RF filtering components are performance-critical and remain subject to final tuning.

### Critical designator translation: Nordic C6 != Aegis C6

In the Nordic QFN48 PCB-layout example that uses a first 1.5 pF RF shunt designated `C6`, Nordic notes that this capacitor is not grounded directly to the general ground plane; its return is routed via pin 32 `VSS_PA` and the exposed VSS die-pad structure for additional harmonic filtering.

In AegisBioWatch, that functional component is:

- **Aegis `C10` = 1.5 pF first RF shunt**

It is **not** Aegis `C6`, which is the 2.2 µF `DECD` capacitor.

Therefore the PCB rule is:

> When the selected silicon-revision reference design uses this first-shunt VSS_PA/die-pad topology, Aegis C10 must reproduce that functional return. Do not give Aegis C10 a generic nearest-GND-via return, and do not apply the special RF-return rule to Aegis C6 merely because of the designator name.

Functional translation, not equal reference numbers, is the hard rule.

## Placement constraints

### U1 and crystals

- `Y1` 32 MHz must remain immediately adjacent to `XC1/XC2` and follow the selected revision's Nordic reference orientation/return geometry as closely as the board allows.
- `Y2` 32.768 kHz must remain immediately adjacent to `XL1/XL2` with short, symmetric, quiet traces.
- Crystal traces must not run beside PMIC switching nodes, display QSPI clocks, or RF feed structures.

### DCC / DECD / DECA / DECRF

- `L1`, `C6`, `FB1`, `C7`, `C8`, and `C9` are one reference-layout-controlled cluster.
- DCC-to-L1-to-DECD copper must be short and compact.
- DECA/DECRF circuitry must follow the design files and errata for the actual silicon revision.
- High-frequency decoupling placement and return paths take precedence over cosmetic alignment.

### RF path

- U1 pin 31 `ANT` → `L2` → first shunt → `L3` → second shunt → `L4` → final shunt → antenna feed remains a compact monotonic path.
- The first shunt return must reproduce the selected Nordic revision's reference-return topology; in the reviewed QFN48 layout this is the VSS_PA/die-pad return described above.
- Matching-component relative placement, geometry and local ground/via pattern must be reference-faithful; third-party PCB coordinates are not authority.
- The all-layer antenna keep-out from r10 remains in force.
- No PMIC switching node, display QSPI clock, or noisy digital escape may intrude into the RF reserve.

## RF impedance gate

Do **not** freeze a nominal 50 Ω trace width from the provisional 0.8 mm / four-layer planning stack alone.

The final feed geometry is gated on:

1. actual fabricator stack-up;
2. dielectric thickness / Dk and copper thickness;
3. selected transmission-line geometry;
4. impedance calculation / fab confirmation;
5. assembled-board RF tuning / VNA verification.

Nordic also advises a very thin RF reference dielectric for QFN designs; the final Aegis stack-up must be reviewed against the selected reference design rather than assuming the provisional layer spacing is acceptable.

Until the stack-up is frozen, r13 may reserve route corridors and enforce topology/keep-outs, but it must not present a provisional width as manufacturing authority.

## Why exact U1 RF coordinates are not generated from generic geometry

Nordic recommends following the QFN reference design closely for RF component values, geometry, relative placement, stack-up and trace lengths. A generic QFN48 polar/radial placement algorithm would therefore be weaker authority than the official revision-matched reference design.

Accordingly:

- exact U1 RF/reference coordinates are not inferred from nRF52 boards or unrelated nRF54 boards;
- third-party coordinates are not copied;
- the current r11 U1 seed may be inspected, but RF-critical placement is frozen only after the **actual silicon revision is known** and its recommended Nordic QFAA design geometry is directly cross-checked;
- non-RF work continues in parallel.

## r13 validation requirements

Before U1 placement is declared frozen:

- identify the actual procured nRF54L15 silicon revision/build code;
- select the corresponding Nordic QFAA design-file release from the compatibility matrix;
- review that revision's errata;
- verify U1 pad/net mapping against the official QFAA pin table;
- verify all required electrical functions are represented in the PCB footprint set;
- compare RF/DC-DC/crystal relative placement against the selected Nordic QFAA reference design;
- run KiCad 9.0.9 PCB DRC;
- report rule violations and unconnected items separately;
- keep final RF impedance geometry open until fab stack-up is known.

## Release gates added/clarified

- actual nRF54L15 silicon revision/build code identification;
- revision-matched Nordic QFAA reference-design selection;
- applicable nRF54L15 errata review;
- direct revision-matched QFAA reference geometry review before RF placement freeze;
- RF/internal-supply capacitor and inductor MPN closure, including high-frequency characteristics;
- final stack-up and impedance geometry;
- VNA / antenna tuning and RF pre-compliance verification.

## Privacy boundary

This file contains only hardware engineering information. It contains no individual health history, private correspondence, medication names/doses, or identifiable health information.
