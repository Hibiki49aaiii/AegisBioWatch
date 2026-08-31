# Executed KiCad validation is routing acceptance authority

Status: active  
Date: 2026-08-20

## Context

The Phase 1 Main Board is being routed through isolated, auditable increments. Preflight geometry can reject obviously unsafe candidates, but acceptance must distinguish a plausible route from a route actually validated by the pinned toolchain and logical pin/net audit.

## Decision

For the current r13 routing series, formal acceptance is based on executed KiCad 9.0.9 DRC plus the repository's 268-node pin/net audit, exact ratsnest expectation, exact routing scope, placement invariants, target component/net/geometry checks, and frozen-interface checks. Preflight/seed data and historical Artifact hashes remain supporting provenance.

## Alternatives considered

- Accept a route from manual/visual or geometric preflight alone: rejected because it does not execute KiCad's real DRC/connectivity model.
- Accept a route from a reduced ratsnest count alone: rejected because it can hide violations, wrong nets, or unintended changes.
- Require historical Artifact byte identity on every reproduction: rejected because byte differences can occur independently of the electrical/geometry acceptance state.

## Evidence / Rationale

- `docs/pcb-route-r13-1an-validation.json` and `tools/reproduce-route1an-accepted.sh` encode the corrected provenance-vs-electrical distinction.
- `docs/pcb-route-r13-1ao-validation.json` records executed result `0 violations / 134 unconnected / 268 audited nodes PASS`, exact 1 segment + 1 via, and zero moves/rotations.
- route-1ao successful workflow run `32282264856`, job `96163538284`, Artifact `9376332330`.
- route-1ao formal acceptance commit `9d1280f5b0296e8febd6d7e48e0544e76846eb78`.
- route-1bm successful workflow run `33403962140` validated `0 violations / 111 unconnected / 268 audited nodes PASS`, exact 4-track / 0-via scope, and downloaded plus independent Artifact verification; evidence is `docs/pcb-route-r13-1bm-validation.json`.\n- route-1bn successful workflow run `33413080742` validated `0 violations / 110 unconnected / 268 audited nodes PASS`, exact 4-track / 0-via +1V8 closure to R403.1, no placement change, 0.260 mm exact conservative clearance to co-limiting R403.2/SYS_I2C_SDA and C4.2/GND pads, downloaded Artifact verification, and independent ZIP/SHA256SUMS/JSON/PCB verification; evidence is `docs/pcb-route-r13-1bn-validation.json`.

## Tradeoffs

This adds CI/toolchain cost and makes acceptance slower than visual inspection, but it makes each baseline reproducible and prevents a lower ratsnest count from being mistaken for correctness.

## Consequences

- Do not create the next routing candidate until the current candidate has executed validation and formal acceptance.
- Do not weaken DRC rules for progress metrics.
- When handoff text disagrees with current source or Artifact evidence, reopen the evidence and correct the record.

## Revisit when

The board revision, KiCad version, pin/net audit authority, or manufacturing-release workflow changes materially.

## Related code

- `tools/audit-pcb-pin-nets.py`
- `tools/reproduce-route1ao-accepted.sh`
- `.github/workflow-archive/r13/r13-route1ao-u3-gnd-validation.yml`
