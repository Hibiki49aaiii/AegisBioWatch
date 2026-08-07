# Rev.0 power tree

```text
Magnetic dock 5 V
      │
      ▼
   nPM1300
      │
      ├──────── VBAT ↔ 1S LiPo + NTC
      │
      ├──────── VSYS ──────────────┐
      │                             │
      ├─ BUCK1 1.8 V ── +1V8       │
      │    ├ nRF54L15               │
      │    ├ Flash                  │
      │    ├ PMIC VDDIO             │
      │    └ digital I/O domains    │
      │
      ├─ BUCK2 3.0 V ── +3V0
      │    └ analog/bio domains as required
      │
      ├─ LS/LDO1 ── DISP_SW
      └─ LS/LDO2 ── BIO_SW
```

## Startup defaults

- `VSET1 = 47 kΩ` → VOUT1 = **1.8 V**
- `VSET2 = 150 kΩ` → VOUT2 = **3.0 V**

## Safety behavior

When charge input is present:

1. firmware receives PMIC charge/input event;
2. bio acquisition is stopped;
3. `BIO_SAFE_EN` is deasserted;
4. bio board is required to disconnect or high-impedance any skin electrodes;
5. on-body bio-electrode acquisition remains inhibited until charger removal.

The exact hardware implementation of electrode disconnect lives on the Bio
Sensor Board and is reviewed independently.
