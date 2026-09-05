# Phase 1 r9 — AMOLED / touch supplier-data gate

## Preferred module candidate

`GL175AMC10C` remains the preferred mechanical/display candidate.

Public supplier data currently establishes:

- 1.75 inch AMOLED;
- 390 × 450 pixels;
- QSPI display interface;
- CO5300AF-41 display driver;
- CST820B touch controller;
- module outline 34.12 × 40.28 × 2.42 mm;
- connector `OK-118RM024-35`;
- 24 pins.

## What is still missing

The public product information does **not** provide the 24-pin electrical definition required for a production PCB.

Do not infer or copy pin order from a different CO5300/CST820B module. Similar modules may use different rail assignments, FPC routing, connector orientation, touch reset/interrupt pins or power sequencing.

Required supplier package before J5/J6 electrical freeze:

1. GL175AMC10C full datasheet and revision.
2. FPC drawing with pin-1 marker and contact orientation.
3. Complete 24-pin pin table.
4. Exact mating connector manufacturer / full MPN and land pattern.
5. Display power rails, min/typ/max current and startup peak.
6. I/O voltage for QSPI, TE and RESET.
7. Required power-on / power-off sequence and timing.
8. CO5300AF-41 initialization command table for this panel revision.
9. QSPI clock/timing limits.
10. CST820B supply and I/O voltage.
11. CST820B I2C address, reset timing and interrupt polarity.
12. ESD recommendations and required external passives.
13. Touch/display behavior during panel sleep/AOD states.
14. Mechanical drawing including FPC bend/keep-out and stiffener thickness.

## J5 / J6 architecture decision

The public module page identifies one 24-pin module connector and an integrated CST820B touch controller. This makes a **single shared physical module connector plausible**, but that is only an engineering inference until the supplier pin table is received.

Therefore:

- `J5` remains the logical display-module interface;
- `J6` remains a logical touch placeholder;
- do not collapse J5/J6 into one physical connector in the authoritative schematic yet;
- after supplier data arrives, replace both placeholders with the actual 24-pin connector and pin mapping in one controlled revision.

## Release state

`J5` and `J6` remain hard release gates. No PCB fabrication release is allowed from guessed FPC pin assignments.
