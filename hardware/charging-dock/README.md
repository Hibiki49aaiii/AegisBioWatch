# AegisBioWatch charging dock — Rev.0 interface seed

The charging dock is a separate PCB/mechanical subassembly from the wearable Main Board.

## Selected dock-side electrical contact

Harwin `P70-7000045` vertical SMT pogo pin.

Design basis from the Harwin technical drawing:

- recommended PCB pad: Ø1.20 ±0.05 mm;
- free height: 2.50 ±0.15 mm;
- normal working height: 2.00 mm;
- allowed working range shown by Harwin: 1.95–2.10 mm;
- nominal force at normal height: 0.68 N ±0.19 N per contact;
- 2 A current rating;
- 30 mΩ max contact resistance;
- 10,000-cycle durability.

KiCad footprint:

`kicad/AegisBioWatch_Dock.pretty/Harwin_P70-7000045.kicad_mod`

The footprint has been parsed/exported successfully with `kicad-cli 9.0.9`.

## Watch-side target

Preferred target: Harwin `S70-125161545R`.

Do not create/freeze its production solder land from body dimensions alone. The official Harwin landing-pattern/CAD data must be obtained and reviewed first.

## Mechanical rule

Magnets are for alignment/retention only and are not electrical conductors. The two electrical contacts are dedicated `DOCK_5V_RAW` and `GND` paths.
