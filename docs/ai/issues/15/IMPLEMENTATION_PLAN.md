# Issue #15 Implementation Plan — route-1bi candidate screening

## Base
- Branch: `agent/phase1-mainboard-schematic`
- Base accepted SHA: `cf138dd4835cc152c60c49d99f8a6d145745acbb`
- Authority: route-1bg = 0 / 116 / 268 PASS

## Phase A1 — curated direct screen
Reproduce route-1bg and evaluate seven direct 0.30 mm F.Cu candidates read-only.

Result:
- geometry-pass: J9 duplicate SIDE_BUTTON and J101 duplicate SHIP_HOLD only;
- both rejected for implementation because the switch terminals are duplicate/internal-common endpoints and body-spanning copper would be electrically redundant.

Evidence:
- run 33242917242 / job 99075208312;
- Artifact 9711921131;
- `docs/pcb-route-r13-1bi-screen-phase-a1.json`.

## Phase A2 — broad direct screen
Screen ordinary route-1bg ratsnest pairs with the same conservative segment-to-copper clearance model.

The first broad run exposed a screening exclusion bug: C7.2/GND passed geometrically even though C7 is RF-sensitive. C7/C8/C9/C10/C11/C12/C401 were then added to the reference exclusions and the screen was rerun.

Corrected result:
- 17 ordinary direct candidates evaluated;
- 0 passing direct candidates at >= 0.100 mm;
- route-1bg remained unmodified.

Corrected run:
- 33243372911 / job 99076428050;
- Artifact 9712068747.

## Phase A3 — Manhattan dogleg screen
Because the ordinary direct-route space is exhausted, search read-only 1-turn and 2-turn orthogonal paths for the same ordinary candidate set.

Path families:
- 1-turn L: H→V and V→H;
- 2-turn H→V→H with a swept X lane;
- 2-turn V→H→V with a swept Y lane.

Lane search:
- 0.25 mm grid;
- local candidate bounding box expanded by 3.0 mm;
- maximum candidate endpoint distance remains 12.0 mm;
- proposed width remains 0.30 mm;
- different-net / unnetted copper clearance must be >= 0.100 mm.

Ranking:
1. rule pass;
2. pad↔pad endpoint semantics preferred over pad↔track, then track↔track;
3. fewer segments;
4. shorter total path;
5. larger minimum conservative clearance.

The screen remains preflight only. KiCad DRC is final authority.

## Phase B
Only the winning Phase A3 candidate receives an exact materializer/report and dedicated KiCad 9.0.9 validation.

Acceptance target:
- 0 violations;
- exactly 115 unconnected;
- 268-node pin/net audit PASS;
- no component moves/rotations;
- exact candidate scope;
- no rule waiver / via-in-pad;
- downloaded Artifact re-verification PASS.

## Safety
All Phase A screens are read-only. Any Phase B probe/DRC/audit/scope failure leaves route-1bg authoritative.
