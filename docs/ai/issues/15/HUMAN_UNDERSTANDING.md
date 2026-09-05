# Human Understanding — Issue #15

The prior direct candidate failed before copper was created. The routing process was therefore changed from repeated single-candidate guessing to staged geometric screening.

## What the screens established

### Phase A1
Seven hand-picked direct candidates were compared. Only J9 and J101 duplicate switch-terminal pairs had comfortable direct geometry. They were not selected because routing between duplicate/internal-common switch terminals is electrically redundant and would optimize the ratsnest count rather than the board design.

### Phase A2
The full ordinary direct-route set was screened after excluding U1, J7, RF-sensitive passives/nets, PMIC switch nodes, CHG_5V, LDO2_IN, SYS_I2C_SCL, supplier-gated connectors and other frozen items.

The corrected screen evaluated 17 ordinary direct candidates and found **zero** that meet the conservative 0.100 mm F.Cu clearance requirement.

This means the easy one-straight-segment routing phase is effectively exhausted.

## Why Phase A3 changes path shape

The next safe step is not to weaken the rule. It is to search for standard-rule Manhattan paths that go around local blockers.

The Phase A3 screen tries:
- one-turn L paths;
- two-turn H-V-H paths;
- two-turn V-H-V paths.

The lane is swept on a 0.25 mm grid around each candidate. Each segment is checked against different-net/unnetted F.Cu pad, track and via copper using the same conservative geometry model.

## What the screen cannot prove

A geometric pass does not prove a route is acceptable. It does not fully model KiCad keepouts, zones, all shape details, or connectivity side-effects. Therefore the selected path must still pass:
- KiCad 9.0.9 DRC;
- exact 116→115 ratsnest decrement;
- 268-node pin/net audit;
- exact-scope checks;
- independent Artifact verification.

The accepted route-1bg board remains untouched until those gates pass.
