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
