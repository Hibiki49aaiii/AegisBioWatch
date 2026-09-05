# Flash retention budget — r6

Selected device: W25Q256JWPIQ, 256 Mbit = 32 MiB class local NOR.

AegisBioWatch uses local Flash as a **temporary disconnected-phone/event buffer**, not as the primary long-term database. Android remains the durable store.

Illustrative payload budgets excluding filesystem/metadata overhead:

| Stored data rate | Approx. 32 MiB duration |
|---:|---:|
| 256 B/s | ~36.4 h |
| 512 B/s | ~18.2 h |
| 1 KiB/s | ~9.1 h |
| 2 KiB/s | ~4.6 h |

Firmware therefore needs tiered logging:
- continuous derived features/status at low rate;
- selected raw PPG/EDA windows around events;
- higher-rate sleep windows only when useful;
- aggressive sync-and-reclaim once Android reconnects.
