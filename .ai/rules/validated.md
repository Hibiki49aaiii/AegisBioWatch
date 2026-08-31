# Validated Rules

Validated Rules are operational guidance with scoped applicability, reproducible evidence, and known exceptions.

## Phase 1 routing increment acceptance gate

Status: validated  
Confidence: high  
Keywords: mainboard, pcb, routing, acceptance, kicad, drc, audit, ratsnest, 268

**Rule:** When promoting a Phase 1 Main Board r13 routing increment to the accepted baseline, require all of the following before calling it accepted:

- executed KiCad **9.0.9** DRC with `rule_violations == 0`,
- the exact expected `unconnected_items` for that increment,
- `tools/audit-pcb-pin-nets.py` result `PASS`,
- `audited_present_source_nodes == 268`,
- exact intended routing scope, including the expected added segment/via count,
- `component_moves == []` and `component_rotations == []`,
- exact component identity/net/geometry gates for the target connection, and
- no mutation of frozen RF or supplier-gated interfaces.

Treat preflight calculations, routing seeds, and historical Artifact byte hashes as supporting provenance, not substitutes for the executed electrical/geometry gates.

### Applicability

The current r13 incremental Phase 1 Main Board routing series and its accepted reproducers.

### Verification

1. Reproduce the prior accepted baseline.
2. Materialize exactly one isolated candidate increment.
3. Run KiCad 9.0.9 DRC and the 268-node pin/net audit.
4. Assert the exact ratsnest delta and routing/placement scope.
5. Assert target component identity, nets, geometry, and frozen-interface status.
6. Store concise evidence and archive the candidate workflow only after success.

### Exceptions

Do not silently weaken this rule. If a future board revision, KiCad/toolchain version, or manufacturing-authority process requires different gates, record a superseding Decision and revalidate the rule.

### Evidence

- `docs/pcb-route-r13-1an-validation.json`
- `tools/reproduce-route1an-accepted.sh`
- `docs/pcb-route-r13-1ao-validation.json`
- `tools/reproduce-route1ao-accepted.sh`
- route-1ao successful workflow run `32282264856`, job `96163538284`, Artifact `9376332330`
- `docs/pcb-route-r13-1bm-validation.json` and `tools/reproduce-route1bm-accepted.sh`
- route-1bm successful workflow run `33403962140`, validate job `99526815463`, downloaded-Artifact verify job `99528757252`, Artifact `9762571974`, with independent ZIP/SHA256SUMS/JSON/PCB verification PASS
\n- `docs/pcb-route-r13-1bn-validation.json` and `tools/reproduce-route1bn-accepted.sh`\n- route-1bn successful workflow run `33413080742`, validate job `99557105934`, downloaded-Artifact verify job `99558773007`, Artifact `9766085905`, with independent ZIP/SHA256SUMS/JSON/PCB verification PASS\n