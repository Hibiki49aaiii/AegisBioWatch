# AegisBioWatch — Codex complete handoff

Updated: 2026-09-01 01:22 JST  
Repository: `Hibiki49aaiii/AegisBioWatch`  
Development branch: `agent/phase1-mainboard-schematic`  
Draft PR: #2  
Manufacturing status: **NOT_FOR_GERBER**

## Current authoritative status

Issue #20 has completed the route-1bn validation gates. The accepted Main Board routing authority is now:

**route-1bn = 0 KiCad 9.0.9 DRC violations / 110 unconnected / 268-node physical pin-net audit PASS**

Authority evidence:
- candidate commit: `89f495f8f792bb53ae3cef8422610f6a3d3f7f45`
- validation run: `33413080742`
- validate job: `99557105934`
- downloaded Artifact verify job: `99558773007`
- Artifact: `9766085905` / `r13-route1bn-r403-1v8-evidence`
- Artifact ZIP SHA-256: `a3e27b162ec50809f90d5f7b6937621d63de455ca6a70b4937be158f647bb0fd`
- PCB SHA-256: `5abd1e61dc4686ffe0241a06864b0914a3e6ce143f7b2346a0095b528f4738db`
- formal evidence: `docs/pcb-route-r13-1bn-validation.json`
- accepted reproducer: `tools/reproduce-route1bn-accepted.sh`

route-1bn adds exactly four 0.30 mm F.Cu `+1V8` segments, zero vias:

```text
(41.005,14.975)
 -> (41.005,15.650)
 -> (39.600,15.650)
 -> (39.600,25.975)
 -> (40.255,25.975)  R403.1/+1V8
```

Total new copper: 13.060 mm. The existing +1V8 source track is preserved. R403.2/SYS_I2C_SDA is untouched. Exact conservative clearance is 0.260 mm; the co-limiting unrelated pads are R403.2/SYS_I2C_SDA and C4.2/GND, both at 0.260 mm. Required rule remains 0.100 mm. No rule waiver, via-in-pad, footprint move, or rotation was used.

A first Phase B validation run `33412259518` failed before materialization because the probe incorrectly required a single nearest obstacle (C4.2). Exact geometry showed R403.2 first; Artifact inspection proved R403.2 and C4.2 are equal 0.260 mm co-limiters. Commit `89f495f8…` corrected the evidence gate without weakening any design rule. The subsequent validation and independent Artifact verification passed.

## Mandatory continuation rules

- GitHub source and executed evidence are authoritative; stale handoff text is not.
- If local PC access is available, reuse the existing `E:\AegisBioWatch` repository and preserve all uncommitted/untracked work.
- Before any repository write, confirm current branch/remote HEAD.
- Promote only one isolated r13 routing increment at a time.
- Every new accepted increment must execute KiCad 9.0.9 DRC = 0, exact ratsnest decrement, 268-node audit PASS, exact intended track/via delta, no placement mutation, no frozen-interface mutation, Artifact verification, and independent verification.
- Do not lower clearances, use via-in-pad, move components, or route through frozen RF/supplier-gated regions just to reduce ratsnest count.
- Current release remains **NOT_FOR_GERBER**. No Gerber generation, PCB order, production deployment, or manufacturing release is authorized.

## Frozen/deferred scope

Continue to exclude unless a separate Issue/decision explicitly releases them:
- U1 adjacent-pad/high-density closures
- J7
- J3/J5/J6 supplier/mechanical interfaces
- C7/C8/C9/C10/C11/C12/C401 and RF-sensitive passives
- RF_A/RF_B/RF_ANT/RF_MCU/NRF_DECA_RF
- NRF_DECD internal regulator/decoupling
- nRF crystal nets
- BIO_SW / DISP_SW by default
- CHG_5V
- U2.30/LDO2_IN ↔ R106.2
- U2.14/SYS_I2C_SCL ↔ R104.2
- PMIC_SW1 / PMIC_SW2 / PVSS1_LOCAL
- duplicate/internal-common switch terminal bridges
- DOCK_5V_RAW coordinated input-power routing
- rule reduction, via-in-pad, component moves/rotations

## Repository authority to read first

1. `AGENTS.md`
2. `.ai/index.md`
3. `.ai/intelligence/mainboard-routing-safety-invariants.md`
4. `.ai/decisions/pcb-routing-acceptance-authority.md`
5. `.ai/rules/validated.md` and `.ai/rules/rejected.md`
6. `docs/pcb-route-r13-1bn-validation.json`
7. `tools/reproduce-route1bn-accepted.sh`
8. the active routing Issue and PR #2

Historical phase-status files and old PCB README text are not current routing authority when they conflict with executed evidence.

## Exact next action

Issue #21 is now the active next routing increment: **route-1bo from route-1bn 0/110/268 PASS**. Phase A1 is read-only. Execute `.github/workflows/r13-route1bo-inventory.yml`, require route-1bn reproduction at 0/110/268 PASS, inventory the actual 110 ratsnest, and run the existing parameterized max-four-segment screen engine against the route-1bn PCB. Do not materialize route-1bo until one ordinary non-frozen candidate has passed semantic review and a dedicated 0.05 mm local refine.

## Paste into a new Codex task

```text
Continue AegisBioWatch from GitHub.

Repository: Hibiki49aaiii/AegisBioWatch
Branch: agent/phase1-mainboard-schematic
Draft PR: #2
Handoff: HANDOFF.md

Current accepted routing authority is route-1bn = 0 KiCad 9.0.9 DRC violations / 110 unconnected / 268-node audit PASS.
Evidence: docs/pcb-route-r13-1bn-validation.json
Accepted reproducer: tools/reproduce-route1bn-accepted.sh
Validation run: 33413080742
Artifact: 9766085905
Release: NOT_FOR_GERBER

If local access exists, reuse E:\\AegisBioWatch and preserve all local changes. Re-check GitHub HEAD/Issue/PR/Actions before writes. Start the next isolated routing increment read-only from route-1bn; do not lower rules or enter frozen scope.
```
