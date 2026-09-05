# Phase 1 reference review — r4

## nRF54L15-QFAA current reference correction

The r3 internal-regulator values were rechecked against the current Nordic
nRF54L15 QFN48 Circuit Configuration 1 rather than relying on an older
third-party KiCad block.

### Current values used in r4

- two 2.2 µF regulator decoupling capacitors
- one 10 nF regulator/RF-supply bypass capacitor
- one 2.2 nF RF-supply bypass capacitor
- FB1 = 120 Ω @ 100 MHz, 200 mA
- L1 = 4.7 µH, 120 mA
- RF chain = 2.7 nH / 1.5 pF / 3.5 nH / 2.0 pF / 3.5 nH / 0.3 pF
- reset = 1 kΩ series + 3.9 pF MCU-side shunt

### Captured internal-regulator topology

```text
DECA ─┐
      ├── NRF_DECA_RF ──┬─ 2.2 µF ─ GND
DECRF ┘                 ├─ 10 nF  ─ GND
                        ├─ 2.2 nF ─ GND
                        │
                      FB1 120 Ω @ 100 MHz
                        │
DCC ── L1 4.7 µH ── DECD ── 2.2 µF ─ GND
```

`DECA` and `DECRF` share one electrical net. The ferrite couples that node to
DECD, and the DCC inductor closes the DC/DC stage into DECD. The older 100 Ω
ferrite value is no longer used.

The current 2.2 nF value is retained specifically instead of an older 10 nF
RF-supply bypass recommendation.

## Legacy KiCad connectivity review

r4 also audits the interchange-file geometry itself. Standard passives and
connectors are now joined to labels using explicit `Wire Wire Line` records.
The KiCad 5.x `Connector_Generic` legacy definitions were checked to resolve the
pin endpoint geometry; even-row connector symbols required a 50 mil placement
correction to align the intended rows with the real symbol pins.

Machine-readable endpoint/net validation is stored in
`docs/electrical-connectivity-validation-r4.json`.

## Display / touch

The r4 sheet deliberately captures only logical signals. No supplier FPC pin
order or panel footprint is claimed. Direct shared-I2C links are conditional on
the final touch controller being compatible with the 1.8 V I/O domain.

## Bio interface

A logical 20-signal Main↔Bio interface is captured. `BIO_SW` is the switched Bio
power rail. A hardware active-low `CHG_PRESENT_N` path is generated from
`CHG_5V` independently of MCU firmware.

This is a safety interlock signal only, not medical isolation.

## Primary references

- Nordic nRF54L15 Product Specification, QFN48 Circuit Configuration 1
- Nordic nRF54L15 QFN48 pin assignments
- Nordic nRF54L15-DK public schematic (PCA10156)
- KiCad 5.1.9 `Connector_Generic.lib` symbol geometry for legacy-import checking


## r5 — nPM1300 full passive capture

The current Nordic nPM1300 reference circuitry and Hardware Design Guidelines
were used as the electrical authority.

Captured functional requirements include VBUS, VBUSOUT, VBAT, VSYS/PVDD,
BUCK output, LS/LDO output, VDDIO, TWI, and local power-ground return passives.

For RF-sensitive applications, a 100 nF high-frequency bypass was added at the
VSYS/PVDD region in addition to the larger capacitors.

### Power rail caution

`DISP_SW` and `BIO_SW` remain provisional. nPM1300 limits are 50 mA in LDO mode
and 100 mA in load-switch mode; exact AMOLED/PPG/haptic current data is required
before those rails can be frozen.

### Errata gate

nPM1300 Revision 1 build-code-specific charger/LDO anomalies are now a
manufacturing and firmware release gate.


### PVSS net-tie interpretation

The current nPM1300 QFN Configuration 1 schematic explicitly shows a `Net tie`
for both PVSS1 and PVSS2 with a via into the GND layer. r5 therefore retains
`PVSS1_LOCAL` / `PVSS2_LOCAL` and net-tie symbols. This does **not** authorize a
split ground plane: L2 remains one uninterrupted GND plane. The net-ties encode
the short top-layer switching-current return geometry and the intended nearby
GND-layer transition.

The production net-tie copper/via geometry is layout-specific and is not frozen
to a generic KiCad net-tie footprint.
