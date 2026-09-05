# Attempts

## Candidate hypothesis

A single short leftward U3.4/GND escape using the standard GND segment/via geometry should remove exactly one unconnected item while preserving route-1an geometry and frozen interfaces.

## Preflight

Conservative geometry screening made the candidate plausible, but it was deliberately not treated as acceptance authority. The candidate was committed with materializer, report helper, and validation workflow together so the executed toolchain could decide acceptance.

## Executed attempt

The route-1ao CI attempt reached materialization, KiCad 9.0.9 DRC, audit, evidence packaging, and Artifact upload successfully. No electrically failed route-1ao attempt is recorded in this case.

## Evidence correction during acceptance

A handoff summary contained stale/incorrect route-1ao hashes and U3 net labels. The successful Artifact and current materializer were re-opened and independently compared; they agreed with each other and replaced the handoff values as acceptance evidence. This is why repository/current Artifact evidence must outrank narrative handoff memory.
