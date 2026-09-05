# Short GND escape pattern has repeatedly been low-risk

Status: observation  
Date: 2026-08-20  
Source case: `.ai/cases/2026-08-20-route1ao-u3-gnd/`  
Confidence: medium

## Context

Recent accepted Phase 1 Main Board routing increments include multiple GND pads closed with one short 0.30 mm F.Cu segment and one 0.60/0.30 mm standard through-via into the continuous In1.Cu GND reference.

## Observation

For non-RF GND pads with adequate local clearance, this pattern has repeatedly reduced the unconnected count by exactly one without introducing an executed DRC violation or changing component placement.

## Evidence

- PR #2 records accepted route-1ak through route-1ao progression from 138 to 134 unconnected items.
- `docs/pcb-route-r13-1an-validation.json`: J2.3/GND accepted at 135.
- `docs/pcb-route-r13-1ao-validation.json`: U3.4/GND accepted at 134 with one segment + one via, zero moves/rotations, and 268-node audit PASS.

## Why it matters

It is a useful candidate-selection heuristic: evaluate uncomplicated non-RF GND escapes before forcing geometry-gated signal or power routes.

## Applicability

Current r13 Phase 1 Main Board routing, when a pad has a clean short escape into the continuous In1.Cu GND plane.

## Exceptions / Limitations

This is not permission to auto-route or auto-accept. Candidate-specific copper clearance, board edge, neighboring pads/tracks, RF sensitivity, PMIC constraints, and frozen interfaces still require inspection and executed KiCad validation. A future board stack-up or plane change can invalidate the pattern.

## Related files

- `docs/pcb-route-r13-1ao-validation.json`
- `tools/materialize-pcb-r13-route1ao-u3-gnd.py`

## Related cases

- `.ai/cases/2026-08-20-route1ao-u3-gnd/`
