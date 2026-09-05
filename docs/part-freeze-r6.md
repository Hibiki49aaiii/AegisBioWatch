# Phase 1 r6 — part freeze

Status: selected where evidence is sufficient; manufacturing release is still blocked by footprints, supplier drawings, ERC and pack qualification.

| Function | r6 selection | Status | Key reason |
|---|---|---|---|
| 32 MHz HFXO | Golledge MP06003 | MPN selected | Used on nRF54L15 DK; 8 pF; ESR/drive fit Nordic guidance |
| 32.768 kHz LFXO | Abracon ABS06-32.768KHZ-9-T | MPN selected | 2012 2-pad; 9 pF; ±20 ppm |
| Local Flash | Winbond W25Q256JWPIQ | MPN selected | 32 MB, 1.7–1.95 V, 6x5 WSON, active/procurable |
| Haptic driver | TI DRV2605LDGSR | MPN selected | Existing design, 2–5.2 V |
| LRA | Precision Microdrives C10-100 | MPN selected | 10x3.7 mm, 175 Hz, DRV2605L-compatible |
| Cell | EEMB LP372435TB | Cell selected, pack not released | 300 mAh, 24.5x36x4.0 mm, 6 g |
| Battery NTC | Murata NXRT15XH103FA5B030 | MPN selected | Exact nPM1300-supported 10k/B3380 class |
| Reverse-polarity diode | Nexperia PMEG2010AEJ | MPN selected | 20 V/1 A, SOD323F |
| Dock ESD | Nexperia PESD5V0S1UL | MPN selected | 5 V VRWM, SOD882, 30 kV IEC ESD |
| AMOLED | GL175AMC10C | preferred candidate only | excellent mechanical fit; FPC electrical docs not public |

## Flash capacity change

Rev.0 changes from the 64 MB class target to **32 MB**. The watch is not intended to archive indefinite full-rate raw signals; Android is the durable store. 32 MB materially improves package area and procurement while preserving disconnected buffering and event-window logging.

## Haptic power change

DRV2605L no longer consumes the +3V0 BUCK2 budget. It is fed from `VSYS_HAPTIC`, derived from VSYS through R305 (0 ohm initially). This keeps the Bio analog rail cleaner and avoids using a 200 mA buck for a load that can be driven directly from the battery/system domain.
