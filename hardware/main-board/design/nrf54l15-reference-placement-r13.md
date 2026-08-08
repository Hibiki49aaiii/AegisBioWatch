# nRF54L15-QFAA reference placement — Phase 1 r13

## Scope

This note defines the physical-layout authority and mapping rules for the U1 / nRF54L15-QFAA block before any RF-critical coordinates are frozen.

It does **not** replace the Nordic reference layout, does not freeze final RF impedance geometry, and does not authorize Gerber release.

## Authority

For the selected `nRF54L15-QFAA` QFN48 package, the physical authority is Nordic Semiconductor's current QFN48 reference layout plus the current nRF54L15 reference circuitry / PCB-layout guidance.

At the time of this r13 review, Nordic's nRF54L15 product reference-layout page selects:

- package: QFN48 / QFAA
- reference layout: `nRF54L15-QFAA Reference Layout 0_8`
- package: 6.0 mm × 6.0 mm nominal, 0.40 mm pitch, exposed die pad

The project must re-check Nordic's product page and applicable silicon errata before release; a cached or third-party copy is not release authority.

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

The project does not reuse Nordic reference designators blindly. Functional identity is the authority when translating the reference circuit into AegisBioWatch designators.

### Internal regulator / RF supply

AegisBioWatch currently implements:

- `L1`: `NRF_DCC` ↔ `NRF_DECD`, 4.7 µH
- `C6`: `NRF_DECD` → GND, 2.2 µF
- `FB1`: `NRF_DECA_RF` ↔ `NRF_DECD`, 120 Ω @ 100 MHz ferrite bead
- `C7`: `NRF_DECA_RF` → GND, 2.2 µF
- `C8`: `NRF_DECA_RF` → GND, 10 nF
- `C9`: `NRF_DECA_RF` → GND, 2.2 nF
- `DECA` pin 43 and `DECRF` pin 33 share `NRF_DECA_RF`

These values/topology are electrically consistent with the project's r8 authority; performance-critical exact MPN and high-frequency behavior remain release gates.

### RF matching / harmonic filter

AegisBioWatch currently implements:

- `L2`: 2.7 nH, `RF_MCU` → `RF_A`
- `C10`: 1.5 pF, `RF_A` → GND
- `L3`: 3.5 nH, `RF_A` → `RF_B`
- `C11`: 2.0 pF, `RF_B` → GND
- `L4`: 3.5 nH, `RF_B` → `RF_ANT`
- `C12`: 0.3 pF, `RF_ANT` → GND

The current Nordic QFN48 configuration-1 BOM uses the same RF nominal sequence: 2.7 nH series, 1.5 pF shunt, 3.5 nH series, 2.0 pF shunt, 3.5 nH series, 0.3 pF shunt.

### Critical designator translation: Nordic C6 != Aegis C6

Nordic's PCB-layout note states that **Nordic reference capacitor C6**, the first 1.5 pF RF shunt capacitor, is not grounded directly to the general ground plane. Its return is routed via pin 32 `VSS_PA` and the exposed VSS die-pad structure for additional harmonic filtering.

In AegisBioWatch, that functional component is:

- **Aegis `C10` = 1.5 pF first RF shunt**

It is **not** Aegis `C6`, which is the 2.2 µF `DECD` capacitor.

Therefore the PCB rule is:

> Aegis C10 RF-ground return must reproduce the Nordic first-shunt / VSS_PA / die-pad return topology. Do not give Aegis C10 a generic nearest-GND-via return, and do not apply this special RF return rule to Aegis C6 merely because of the designator name.

This functional translation is a hard r13/routing constraint.

## Placement constraints

### U1 and crystals

- `Y1` 32 MHz must remain immediately adjacent to `XC1/XC2` and follow the Nordic reference orientation/return geometry as closely as the board allows.
- `Y2` 32.768 kHz must remain immediately adjacent to `XL1/XL2` with short, symmetric, quiet traces.
- Crystal traces must not run beside PMIC switching nodes, display QSPI clocks, or RF feed structures.

### DCC / DECD / DECA / DECRF

- `L1`, `C6`, `FB1`, `C7`, `C8`, and `C9` must be treated as one reference-layout-controlled cluster.
- DCC-to-L1-to-DECD copper must be short and compact.
- DECA and DECRF must remain connected as required by the Nordic reference circuitry.
- High-frequency decoupling placement and return paths take precedence over cosmetic alignment.

### RF path

- U1 pin 31 `ANT` → `L2` → shunt → `L3` → shunt → `L4` → shunt → antenna feed must remain a compact monotonic path.
- The first 1.5 pF shunt return uses the special VSS_PA/die-pad topology described above.
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

Until then, r13 may reserve the route corridor and enforce topology/keep-outs, but it must not present a provisional width as manufacturing authority.

## Why exact U1 RF coordinates are not generated from generic geometry

Nordic explicitly recommends following the QFN reference design closely for RF component values, geometry, relative placement, stack-up and trace lengths. A generic QFN48 polar/radial placement algorithm would therefore be weaker authority than the official reference design.

Accordingly:

- exact U1 RF/reference coordinates are not inferred from nRF52 boards or unrelated nRF54 boards;
- third-party coordinates are not copied;
- the current r11 U1 seed may be inspected, but RF-critical placement is frozen only after the Nordic QFAA reference geometry is available for direct cross-check;
- non-RF work continues in parallel.

## r13 validation requirements

Before U1 placement is declared frozen:

- verify U1 pad/net mapping against the official QFAA pin table;
- verify all r8 functional components are present in the PCB footprint set;
- compare RF/DC-DC/crystal relative placement against the Nordic QFAA reference layout;
- run KiCad 9.0.9 PCB DRC;
- report rule violations and unconnected items separately;
- keep final RF impedance geometry open until fab stack-up is known.

## Release gates added/clarified

- current Nordic QFAA reference-layout version re-check at release;
- applicable nRF54L15 silicon revision / errata review;
- direct QFAA reference geometry review before RF placement freeze;
- RF capacitor/inductor MPN closure, including high-Q/tolerance requirements;
- final stack-up and impedance geometry;
- VNA / antenna tuning and pre-compliance RF verification.

## Privacy boundary

This file contains only hardware engineering information. It contains no individual health history, private correspondence, medication names/doses, or identifiable health information.
