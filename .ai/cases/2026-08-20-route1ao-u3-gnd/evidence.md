# Evidence

## Executed validation

Successful route-1ao Artifact `9376332330` (`r13-route1ao-u3-gnd-evidence`) reports:

- KiCad 9.0.9 workflow run `32282264856`, job `96163538284`
- `rule_violations = 0`
- `unconnected_items = 134`
- `pin_net_audit = PASS`
- `audited_nodes = 268`
- `added_segments = 1`
- `vias_added = 1`
- `component_moves = []`
- `component_rotations = []`
- U3.4 pad `(3.58, 8.53)`
- GND via `(2.8, 8.53)`
- accepted route-1an geometry unchanged
- RF/supplier-gated interfaces untouched

Artifact digest: `sha256:abac53552156c789f03dd4921961b0c1d045adf9f1a86933e4601eedc090df08`. PCB SHA-256: `0854849492c272968117c1c96676ea94fac4671810b3f8a41c59ef5c8d6a4b9a`.

## Component identity

Current materializer and accepted evidence agree on:

- `U3 = W25Q256JWPIQ 256Mbit`
- U3.1 `FLASH_CS_N`
- U3.2 `AUX_SPI_MISO`
- U3.3 `FLASH_WP_N`
- U3.4 `GND`
- U3.5 `AUX_SPI_MOSI`
- U3.6 `AUX_SPI_SCK`
- U3.7 `FLASH_HOLD_N`
- U3.8 `+1V8`

## Reproduction sources

- `docs/pcb-route-r13-1ao-validation.json`
- `tools/reproduce-route1ao-accepted.sh`
- `tools/audit-pcb-pin-nets.py`
- formal acceptance commit `9d1280f5b0296e8febd6d7e48e0544e76846eb78`
