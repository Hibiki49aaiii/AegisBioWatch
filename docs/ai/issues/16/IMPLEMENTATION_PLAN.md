# Issue #16 Implementation Plan — route-1bj from route-1bi

## Base
- Branch: agent/phase1-mainboard-schematic
- Base accepted/archive SHA: df35a6cf0b82c6234024afa0f5de4764971bd733
- Accepted electrical authority: route-1bi = 0 violations / 115 unconnected / 268 PASS
- Accepted Artifact: 9712848520
- Accepted PCB SHA-256: 9e513dc10b0cf16006bebcf60bf925e78740bbdd124811852b2703e45f1fd1ca

## Phase A
1. Reproduce route-1bi with tools/reproduce-route1bi-accepted.sh.
2. Assert source DRC = 0 / 115 and physical audit = 268 PASS.
3. Parse the current 115-item DRC output rather than reusing route-1bg candidate ordering.
4. Exclude U1/J7/RF/supplier-gated/PMIC-switch/CHG_5V/LDO2_IN/SYS_I2C_SCL/duplicate-terminal items.
5. Search ordinary endpoint pairs <= 12 mm with L-HV / L-VH / HVH / VHV, initially 0.25 mm and then refined 0.05 mm lane grid, ±3.0 mm local margin, and 0.30 mm F.Cu provisional width.
6. Require conservative different-net/unnetted copper clearance >= 0.100 mm.
7. Rank passing routes by endpoint semantics, segment count, total path length, then clearance.
8. Review functional meaning before selecting the winner.

## Executed Phase A
Coarse run:
- run 33246360328 / job 99084399327;
- 16 candidates evaluated / 3 pass;
- R404.1/+1V8 → R302.1/+1V8 best ordinary candidate at 0.125 mm clearance.

Refined run:
- run 33246532809 / job 99084854067;
- Artifact 9713058941;
- ZIP SHA-256 060b4c00984ec68e7fa21aeda5d54547b21d1ad9a8802f76c732bdff16978705;
- 0.05 mm lane grid;
- 16 candidates evaluated / 6 geometric pass.

Selected Phase B candidate:
- R404.1/+1V8 (15.755,26.725)
- → (15.755,26.200)
- → (20.255,26.200)
- → R302.1/+1V8 (20.255,25.975)
- VHV / 3 segments / 5.250 mm total / 0.30 mm width;
- conservative minimum unrelated-copper clearance 0.175 mm;
- nearest unrelated copper: R501.1/CHG_5V.

Semantic context:
- R404 = 4.7k PU PROV; pad2 = SYS_I2C_SCL.
- R302 = 47k PU; pad2 = FLASH_HOLD_N.
- Candidate joins only the +1V8 pull-up rail pads and escapes away from both signal pads.

Not selected:
- NRF_DECD candidates: nRF internal supply/decoupling network; defer from this ordinary pull-up increment.
- DOCK_5V_RAW: better geometric margin but 12.555 mm power-path closure; defer for coordinated dock-power routing.
- track→R403 +1V8: 0.099999 mm boundary result; reject for insufficient margin.

## Phase B
For selected R404/R302:
1. Create exact read-only identity/net/coordinate/path probe.
2. Materialize only the documented three-segment route.
3. Run KiCad 9.0.9 DRC.
4. Require exact 115 → 114 unconnected decrement.
5. Run 268-node physical pin/net audit.
6. Verify exact scope, no placement changes, no frozen-interface changes.
7. Upload evidence Artifact.
8. Download Artifact in a second job and re-verify SHA256SUMS and JSON gates.
9. Independently download/re-verify before formal acceptance.
10. Commit acceptance/rejection evidence and reproducer.
11. Archive/retire temporary workflows.

## Invariants
- route-1bi remains authority unless all Phase B gates pass.
- No rule reduction.
- No via-in-pad.
- No component move/rotation.
- No RF/supplier-gated changes.
- R404.2/SYS_I2C_SCL and R302.2/FLASH_HOLD_N routing remain untouched.
- CHG_5V routing remains untouched.
- Release remains NOT_FOR_GERBER.
