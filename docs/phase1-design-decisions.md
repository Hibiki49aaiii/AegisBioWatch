# Phase 1 design decisions

## D1 — QFN packages for first prototype
Use nRF54L15 QFN48 and nPM1300 QFN32. Rev.0 prioritizes assembly yield,
inspection and rework over maximum miniaturization.

## D2 — nPM1300 Configuration 1
Use both bucks and both load-switch/LDO resources. Startup rails are 1.8 V and
3.0 V.

## D3 — display owns dedicated QSPI
The 390×450 AMOLED can generate much larger traffic bursts than the data logger.
The dedicated nRF54L15 QSPI pin group is therefore assigned to display.

## D4 — Flash uses regular SPI
64 MB logging storage remains, but Flash is connected to a separate SPIM bus.
This prevents a display/Flash chip-select and bandwidth coupling problem.

## D5 — no NFC in Rev.0
P1.02/P1.03 are released to GPIO use.

## D6 — local-first safety
Charging state is made visible to both Main Board firmware and Bio Board safety
logic. Bio-electrode measurement is inhibited during charging.

## D7 — panel connector is not frozen
No production FPC pinout is committed until an actual supplier datasheet and
sample are selected.
