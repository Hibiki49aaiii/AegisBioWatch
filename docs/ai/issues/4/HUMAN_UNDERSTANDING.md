# Human Understanding — Issue #4

## What

route-1az closes only `R304.2/GND` by adding one short front-copper track and one standard through-via into the internal GND plane. This task does not redesign that route; it promotes the already-tested candidate into the accepted r13 routing baseline.

## Why

A successful GitHub Actions run is not enough by itself to become routing authority. The repository keeps accepted routing stages reproducible and auditable, so route-1az needs a durable acceptance record, an accepted reproducer, and archived validation workflow evidence.

## How

The accepted route-1ay baseline is reconstructed first. The route-1az materializer then checks that R304 is still the expected 100k pull-down with:

- pin 1 = `HAPTIC_EN`
- pin 2 = `GND`
- fixed pad coordinates

It adds exactly one 0.30 mm F.Cu segment from R304.2 to one 0.60/0.30 mm through-via at `(25.395,26.630)`.

KiCad 9.0.9 DRC and the repository's physical 268-node pin/net audit then prove that the increment is electrically acceptable and has not mutated unrelated routing.

## Important Decisions

- The executed KiCad run is acceptance authority; static reasoning alone is not.
- Generated PCB bytes are not checked in as the primary source of truth.
- Artifact SHA values are provenance records, not electrical correctness gates.
- route-1ay remains the fallback authority if any route-1az gate fails.
- RF, supplier-gated interfaces, CHG_5V, SYS_I2C_SCL, and LDO2_IN remain outside this task.

## Invariants

The following must never change as part of Issue #4:

- 0 KiCad rule violations
- exactly 123 unconnected items for route-1az
- 268/268 logical pin/net nodes PASS
- exactly one added segment and one added via
- no component move or rotation
- `R304 = 100k PD`
- `R304.1 = HAPTIC_EN`
- `R304.2 = GND`
- accepted route-1ay geometry unchanged
- RF untouched
- supplier-gated interfaces untouched
- release status remains `NOT_FOR_GERBER`

## Failure Modes

Acceptance must fail if:

- the source baseline no longer reproduces route-1ay;
- KiCad reports any DRC violation;
- the ratsnest count differs from 123;
- the physical audit is not PASS/268;
- R304 value/net identity or pad geometry changes;
- more routing geometry than the one intended segment/via is added;
- placement changes;
- RF or supplier-gated regions are touched.

## Change Impact

Future routing increments should use route-1az only after this acceptance is complete. Any later change to R304, HAPTIC_EN routing, nearby GND geometry, the recovered logical topology, or KiCad design rules can invalidate the assumptions used here and therefore must re-run the accepted reproducer.

This acceptance does **not** make the board ready for Gerber generation or manufacturing.
