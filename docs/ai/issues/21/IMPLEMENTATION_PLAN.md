# Issue #21 Implementation Plan — route-1bo from route-1bn

## Base
- Branch: `agent/phase1-mainboard-schematic`
- Base repository HEAD: `b4bf981181b11a9d1851137d56efafad421003e9`
- Accepted electrical authority: route-1bn = 0 violations / 110 unconnected / 268 PASS
- Accepted Artifact: 9766085905
- Accepted PCB SHA-256: `5abd1e61dc4686ffe0241a06864b0914a3e6ce143f7b2346a0095b528f4738db`
- Accepted reproducer: `tools/reproduce-route1bn-accepted.sh`

## Phase A1 — current route-1bn read-only screen
1. Reproduce route-1bn and assert 0 / 110 / 268 PASS.
2. Record the actual 110-item ratsnest without modifying the board.
3. Reuse the parameterized max-four-segment screening engine with the route-1bn PCB/report and expected-unconnected=110.
4. Preserve existing frozen/deferred semantic exclusions.
5. Search ordinary endpoints <=12 mm using L, HVH/VHV, and HVHV/VHVH on a 0.25 mm grid with ±4 mm margin.
6. Use provisional 0.30 mm F.Cu width and require conservative unrelated/unnetted copper clearance >=0.100 mm.
7. Record all numerical passes and exclusion counts.
8. Perform semantic/topology review after the executed screen; numerical ranking alone does not select a route.

## Phase A2
If a semantically acceptable family remains:
1. prove exact source/target identity;
2. choose exactly one family;
3. refine only that family at 0.05 mm;
4. keep the board unchanged.

## Phase B
For one selected candidate:
1. exact identity/net/coordinate/path probe;
2. materialize only documented copper;
3. physical before/after delta audit;
4. KiCad 9.0.9 DRC;
5. require exact 110 -> 109 unconnected decrement;
6. 268-node physical pin/net audit PASS;
7. Artifact + downloaded verification + independent verification;
8. formal evidence and accepted reproducer;
9. archive temporary workflows and update Issue/PR/HANDOFF.

## Invariants
- route-1bn remains authority until every Phase B gate passes.
- No rule reduction, via-in-pad, component move, or rotation.
- Frozen RF/nRF-internal/supplier-gated interfaces remain untouched.
- Existing deferred power/interface nets remain deferred.
- Release remains NOT_FOR_GERBER.
