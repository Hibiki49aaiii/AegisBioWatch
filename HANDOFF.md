# AegisBioWatch — Codex complete handoff

Updated: 2026-09-01 21:30 JST  
Repository: `Hibiki49aaiii/AegisBioWatch`  
Development branch: `agent/phase1-mainboard-schematic`  
Draft PR: #2  
Manufacturing status: **NOT_FOR_GERBER**

## Current authoritative status

Issue #21 completed the route-1bo validation gates. The accepted Main Board routing authority is now:

**route-1bo = 0 KiCad 9.0.9 DRC violations / 109 unconnected / 268-node physical pin-net audit PASS**

Authority evidence:
- candidate commit: `b1a0778fba6ac1e144523465ab5bc14335aee934`
- validation run: `33447520649`
- validate job: `99669842446`
- downloaded Artifact verify job: `99671064031`
- Artifact: `9778684430` / `r13-route1bo-j8-1v8-evidence`
- Artifact digest: `sha256:9520621a3e47fbb75aab8ab1689b73977b473159a79082e7c9fa1c55437183e6`
- PCB SHA-256: `e1239dfd912fbb910313b32af3e88f23e34cbc198a742a33ec6beb7b108410c6`
- formal evidence: `docs/pcb-route-r13-1bo-validation.json`
- accepted reproducer: `tools/reproduce-route1bo-accepted.sh`

route-1bo adds exactly four 0.30 mm F.Cu `+1V8` segments, zero vias:

```text
(10.305,4.720)
 -> (9.700,4.720)
 -> (9.700,15.800)
 -> (12.105,15.800)
 -> (12.105,15.260)  J8.1/+1V8
```

Total new copper: 14.630 mm. The existing +1V8 source track is preserved. Exact conservative clearance is 0.4897 mm against a numberless J8 pad. All three numberless J8 pads were proven by KiCad API to be exact netless `PAD_ATTRIB_NPTH` and were preserved before/after. No rule waiver, via-in-pad, footprint move, or rotation was used.

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
6. `docs/pcb-route-r13-1bo-validation.json`
7. `tools/reproduce-route1bo-accepted.sh`
8. the active routing Issue and PR #2

Historical phase-status files and old PCB README text are not current routing authority when they conflict with executed evidence.

## Exact next action

Close Issue #21 as completed after this authority commit, then create the next isolated routing Issue from **route-1bo 0/109/268 PASS**. The next increment must begin read-only: reproduce route-1bo, inventory the actual 109-item ratsnest, apply the same frozen/deferred exclusions, and only refine one ordinary non-frozen candidate if semantic review passes.

## Paste into a new Codex task

```text
Continue AegisBioWatch from GitHub.

Repository: Hibiki49aaiii/AegisBioWatch
Branch: agent/phase1-mainboard-schematic
Draft PR: #2
Handoff: HANDOFF.md

Current accepted routing authority is route-1bo = 0 KiCad 9.0.9 DRC violations / 109 unconnected / 268-node audit PASS.
Evidence: docs/pcb-route-r13-1bo-validation.json
Accepted reproducer: tools/reproduce-route1bo-accepted.sh
Validation run: 33447520649
Artifact: 9778684430
Release: NOT_FOR_GERBER

If local access exists, reuse E:\\AegisBioWatch and preserve all local changes. Re-check GitHub HEAD/Issue/PR/Actions before writes. Start the next isolated routing increment read-only from route-1bo; do not lower rules or enter frozen scope.
```
