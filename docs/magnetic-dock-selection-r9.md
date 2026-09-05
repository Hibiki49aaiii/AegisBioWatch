# Phase 1 r9 — magnetic dock contact selection

## Direction

Separate magnetic retention from electrical contact:

- enclosure magnets provide alignment/retention;
- watch PCB provides two wear-resistant electrical targets;
- dock PCB carries two spring-loaded pogo contacts;
- existing ESD and reverse-polarity protection remain upstream of nPM1300 VBUS.

This avoids using the magnets themselves as electrical conductors.

## Preferred contact family

### Watch side target

**Harwin S70-125161545R**

- SMT rectangular contact pad;
- 2.50 × 1.60 × 0.15 mm body;
- gold contact surface;
- beryllium-copper base;
- rated 6 A;
- explicitly intended by Harwin as a hard-wearing mating surface for spring contacts / pogo pins.

Status: **PART_FAMILY_SELECTED / LAND_PATTERN_GATE**.

The exact production footprint is not frozen until the Harwin S70 technical drawing or verified CAD landing pattern is available in the design repository. Do not infer solder-land geometry from body dimensions.

### Dock side pogo

**Harwin P70-7000045**

- vertical SMT spring-loaded contact;
- free height: 2.50 mm;
- normal working height: 2.00 mm;
- maximum working height: 2.10 mm;
- minimum working height / allowed travel: 1.95 mm;
- rated current: 2 A;
- contact resistance: 30 mΩ max;
- force at normal height: 0.68 N ±0.19 N;
- durability: 10,000 cycles;
- recommended dock-PCB solder pad: Ø1.20 ±0.05 mm.

For two pogo pins, nominal total spring force is about 1.36 N at the normal working height before tolerance. Magnet retention must exceed the required contact force with margin after enclosure/tolerance/contamination testing.

## Mechanical interface target

Prototype target:

- two electrical contacts only: `DOCK_5V_RAW` and `GND`;
- magnets are mechanically separate from both nets;
- target pogo compression is designed around the P70 **2.00 mm normal working height**;
- 180-degree reversal should be prevented mechanically/magnetically;
- PMEG2010AEJ remains backup reverse-polarity protection, not the primary alignment mechanism.

Contact center-to-center pitch is **not yet frozen**. It must be co-designed with the rear case, magnet position, sensor window and charging-dock tolerances.

## Qualification required before PCB release

- obtain/verify S70-125161545R recommended solder land;
- freeze contact pitch and datum relative to case;
- tolerance stack for pogo compression over case/PCB/adhesive variation;
- verify contact force and magnetic retention across tolerance;
- contact-drop test at configured charger current;
- contamination/sweat/corrosion test;
- insertion-cycle test;
- ESD test through assembled dock;
- verify no dock metal interferes with PPG/EDA sensing or antenna tuning.

## Release state

`J3` remains an open footprint gate even though the preferred mating-contact family is now selected.
