# Issue #8 Implementation Plan — route-1bb J9 left GND closure

## Base
- Branch: `agent/phase1-mainboard-schematic`
- Base SHA: `fd5e94e26f878b4d60362339e6a2deee1ac3f2c4`
- Accepted authority: route-1ba = 0 violations / 122 unconnected / 268 PASS

## Objective
Evaluate exactly one additional local GND stitch for the left physical J9.1 pad at (20.850,5.775). Candidate geometry is one 0.30 mm F.Cu segment to a 0.60/0.30 mm through-via at (19.850,5.775). Accept only if executed KiCad 9.0.9 returns 0 violations / 121 unconnected and the 268-node audit passes.

## Architecture
The implementation follows the existing isolated-routing pipeline:
1. reproduce accepted route-1ba;
2. materialize route-1bb only;
3. refill zones;
4. run KiCad DRC;
5. run pin/net audit;
6. assert exact route scope, J9 physical-pad identity, placement invariants, accepted-baseline preservation, and frozen-interface preservation;
7. upload evidence;
8. accept or reject from executed evidence.

No checked-in generated PCB is treated as authority. Candidate helper scripts are deterministic reconstruction tools; executed KiCad evidence is acceptance authority.

## Design options
### A — left J9.1/GND
Selected for validation because it is an isolated duplicate GND pad in the same non-RF side-button footprint already partially routed by route-1ba. Symmetry is only a candidate-selection hint, not proof of clearance.

### B — C401.2/GND
Deferred due RF adjacency.

### C — LDO2_IN / CHG_5V / SYS_I2C_SCL
Deferred because these require coordinated geometry work and are not appropriate isolated stitches.

## Invariants
- J9 value remains EVQPUK02K_SIDE_BUTTON.
- J9.1 GND pads remain at (20.850,5.775) and (26.000,5.775).
- J9.2 SIDE_BUTTON pads remain at (20.850,7.475) and (26.000,7.475).
- Route-1ba right J9.1 closure remains unchanged.
- Exactly one new segment and one new via.
- No component move/rotation.
- No RF or supplier-gated interface changes.
- No design-rule reduction, via-in-pad, or manufacturing-release claim.

## Verification
- Python syntax/static checks where applicable.
- Dedicated GitHub Actions workflow with KiCad 9.0.9.
- DRC JSON: exactly 0 violations / 121 unconnected.
- Physical pin-net audit: PASS / 268.
- Exact route geometry and component identity gates.
- Artifact packaging and independent hash inspection before acceptance.

## Rollback
If any hard gate fails, route-1bb is rejected. The accepted authority remains route-1ba and no rule waiver is introduced.
