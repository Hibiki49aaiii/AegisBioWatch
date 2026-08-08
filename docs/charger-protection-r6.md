# Magnetic dock input protection — r6

## Schematic

```text
MAG dock +5V
    |
    +---- PESD5V0S1UL ---- GND
    |
PMEG2010AEJ
    |
  CHG_5V
    |
 nPM1300 VBUS
```

- `PESD5V0S1UL`: 5 V unidirectional ESD protection, SOD882; cathode to `DOCK_5V_RAW`, anode to GND.
- `PMEG2010AEJ`: 20 V / 1 A Schottky in SOD323F; provides simple reverse-polarity blocking.

## Design notes

- Put D102 at the pogo/contact entry with the shortest practical ESD return to ground.
- Put D101 after the ESD node and before nPM1300 VBUS decoupling.
- Mechanical magnet/key geometry is the primary polarity control; D101 is the electrical backup.
- Validate VBUS margin at maximum intended input current with actual dock cable/contact resistance and D101 forward drop.
- The nPM1300 input-current limit and battery charging current are separate settings. Do not automatically set both to the dock maximum.
