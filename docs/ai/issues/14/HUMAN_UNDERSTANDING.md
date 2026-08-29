# Human Understanding — Issue #14

## What
C301 is a 100nF capacitor and R404 is a provisional 4.7k pull-up resistor. Their +1V8 pads are currently separated by one ratsnest edge.

## Why this candidate
Shorter remaining ratsnest edges are concentrated in explicitly deferred U1-adjacent, RF, C401, or J7 geometry. C301→R404 is the shortest remaining ordinary discrete +1V8 candidate after those exclusions.

## Geometry
- C301.1/+1V8: (13.755,23.725)
- C301.2/GND: (14.395,23.725)
- R404.1/+1V8: (15.755,26.725)
- R404.2/SYS_I2C_SCL: (16.395,26.725)

The direct +1V8 segment length is 3.605551 mm.

## Why a stronger probe
A large axis-aligned corridor rectangle can falsely classify nearby pads as blockers. This increment instead computes the candidate segment's conservative shortest distance to each unrelated F.Cu pad, track and via.

KiCad DRC remains the final electrical/layout authority; the probe is an early hard gate, not a substitute for DRC.

## Important decisions
- Route only the +1V8 pads.
- Preserve C301 GND.
- Preserve R404 SYS_I2C_SCL.
- Do not treat R404 pull-up routing as permission to resolve the separately geometry-gated U2.14↔R104 SCL item.
- Reject/defer rather than reduce rules.

## Change impact
If accepted, authority advances from route-1bg 0/116/268 to route-1bh 0/115/268. Release remains NOT_FOR_GERBER.
