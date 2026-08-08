# Phase 1 r5 — Power budget and rail ownership

Status: **hard release gate**

The Main Board currently exposes logical rails named `DISP_SW` and `BIO_SW`.
Those names do **not** yet authorize the nPM1300 LOADSW/LDO outputs as the
production power source.

nPM1300 limits relevant to this design:
- BUCK1: 200 mA
- BUCK2: 200 mA
- LOADSW/LDO as LDO: 50 mA
- LOADSW/LDO as load switch: 100 mA

## Rev.0 provisional assignment

| Rail | Source | Status |
|---|---|---|
| `+1V8` | nPM1300 BUCK1 | retained |
| `+3V0` | nPM1300 BUCK2 | retained |
| `DISP_SW` | nPM1300 LS/LDO1 output | provisional only |
| `BIO_SW` | nPM1300 LS/LDO2 output | provisional only |
| `VSYS` | nPM1300 system rail | high-current upstream rail |

R105/R106 provide an optional VSYS feed to VINLDO1/VINLDO2 and are intentionally
treated as option links until the final mode is decided.

## Required measurements/specs before freeze

For every load record:
- operating voltage range;
- average current;
- peak current and pulse duration;
- startup/inrush current;
- acceptable rail ripple;
- power-up/down sequencing requirements.

## Decision rule

If a domain cannot maintain at least 30% current headroom under worst-case
simultaneous load, do not source it from the provisional nPM1300 LS/LDO rail.
Use an external load switch or regulator sized for that domain.

This file deliberately contains no personal health or medication information.
