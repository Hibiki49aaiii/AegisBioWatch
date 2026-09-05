# Human Understanding — Issue #18

## What changed
route-1bl closes one VSYS ratsnest item by connecting the existing VSYS source track to `R106.1/VSYS`.

New copper:
`(7.35,28.25) → (7.20,28.25) → (7.20,26.40) → (5.270826,26.40) → (5.270826,25.865834)`

This is 4 segments, 0 vias, 0.30 mm F.Cu, total 4.463340 mm.

## Why this candidate was selected
The first preference, `C301.1/+1V8`, was not legal under the current geometry:
- 2,884 four-segment candidates;
- 0 passes;
- best clearance 0.074999 mm.

Other candidates were also rejected:
- +1V8→R403: 0.099999 mm, below the 0.100000 mm threshold;
- NRF_RESET_N: route approached frozen RF_B/C11 context.

The R106.1 VSYS candidate was the next ordinary candidate that could pass full clearance while preserving the explicitly deferred `R106.2/LDO2_IN` node.

## Why the final route differs from the screen path
The best screen path started at `(8.9875,28.25)`, but an accepted VSYS segment already exists from `(8.9875,28.25)` to `(7.35,28.25)`.

Materializing that portion again would create redundant overlapping copper, so route-1bl starts at the existing endpoint `(7.35,28.25)` and adds only the missing four segments.

## Clearance
The refined screen found 16 legal paths out of 88 candidates.

Selected geometry has:
- modeled minimum unrelated-copper clearance = 0.184166 mm;
- independent limiting gap to `R106.2/LDO2_IN` = 0.184166 mm;
- required rule = 0.100000 mm.

The limiting relation is the horizontal segment at y=26.400 mm passing above the R106.2 pad.

## DRC representative instability
KiCad may report different representative coordinates/descriptions for the same unconnected VSYS islands after regeneration. Those representative strings are not used as electrical authority.

The durable gates are:
- source DRC = 0 / 113;
- exact PCB source-track identity;
- exact R106.1/R106.2 pad identity/net/coordinates;
- exact route geometry;
- executed output DRC = 0 / 112;
- 268-node audit PASS.

## Physical scope proof
A pcbnew before/after comparison verifies:
- exactly four expected VSYS tracks added;
- no track removed;
- no via added;
- all footprint positions and rotations unchanged;
- existing VSYS source track unchanged.

## Acceptance
Dedicated validation run 33339645685 passed:
- KiCad 9.0.9 DRC = 0 violations;
- unconnected = 112;
- physical pin/net audit = 268 PASS;
- downloaded Artifact verification = PASS;
- independent Artifact verification = PASS.

Release remains NOT_FOR_GERBER.
