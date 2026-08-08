# Preferred AMOLED candidate — r6

Preferred candidate: **GL175AMC10C**.

Supplier-published properties:
- 1.75 inch
- 390 x 450
- QSPI
- CO5300AF-41 display driver
- CST820B touch controller
- outline 34.12 x 40.28 x 2.42 mm
- active area 29.02 x 33.48 mm
- 24-pin
- connector reported as OK-118RM024-35
- reported brightness 650–700 cd/m²

## Mechanical fit against Rev.0 envelope

Target enclosure top plan is 39.5 x 45.0 mm. A 34.12 x 40.28 mm module leaves nominal plan-view allowance of approximately:
- 2.69 mm per side across 39.5 mm;
- 2.36 mm per side across 45.0 mm.

This is a strong geometric fit for the current industrial-design concept.

## Not electrically frozen

Do **not** assign production pins from the 24-pin connector until the supplier provides:
1. FPC pinout;
2. rail voltage limits;
3. power-on/off sequence;
4. QSPI timing;
5. CO5300 initialization/command table for this exact panel;
6. CST820B supply/I/O thresholds and address/reset timing;
7. panel/FPC mechanical drawing and approved mating-connector drawing.

The public listing is sufficient for candidate/mechanical lock only, not PCB connector release.
