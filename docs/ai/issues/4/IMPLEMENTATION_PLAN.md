# Issue #4 Implementation Plan — route-1az R304.2/GND acceptance

## Issue

#4 — `pcb: accept r13 route1az R304 GND closure`

## Base Commit SHA

`e71fa194960e8941244aa2b2d0af1dd6274e920e`

## Target branch

`agent/phase1-mainboard-schematic`

## Requirements

Promote the already-materialized route-1az candidate to accepted routing authority only when the dedicated executed KiCad 9.0.9 evidence proves all established acceptance gates:

- 0 DRC rule violations
- 123 unconnected items
- physical pin/net audit PASS
- 268 audited source nodes
- exact scope: one 0.30 mm F.Cu segment + one 0.60/0.30 mm through-via
- zero component moves/rotations
- R304 identity/net/geometry invariants
- accepted route-1ay geometry unchanged
- RF routing untouched
- supplier-gated interfaces untouched
- release remains NOT_FOR_GERBER

## Current architecture

Routing stages are generated from reproducible Python materializers rather than checked in as permanent generated PCB directories.

Each accepted stage has three durable elements:

1. the materializer/report code that defines the isolated candidate;
2. an executed GitHub Actions validation run using KiCad 9.0.9 plus the physical 268-node audit;
3. after success, an acceptance JSON and an accepted reproducer, while the one-shot active validation workflow is moved to `.github/workflow-archive/r13/`.

Electrical acceptance is determined by executed topology/geometry/DRC/audit gates. Historical artifact hashes remain provenance only and are not electrical acceptance criteria.

## Proposed architecture

Keep the same architecture and promote route-1az without changing its routing geometry:

`route-1ay accepted reproducer`
→ `materialize-pcb-r13-route1az-r304-gnd.py`
→ KiCad 9.0.9 DRC
→ physical pin/net audit
→ route-1az invariant checks
→ accepted route-1az baseline

Durable repository records added:

- `docs/pcb-route-r13-1az-validation.json`
- `tools/reproduce-route1az-accepted.sh`
- archived route-1az workflow

The active workflow is removed after archival so GitHub Actions only contains active candidate validation workflows.

## Data flow

1. `tools/reproduce-route1ay-accepted.sh` reconstructs and verifies route-1ay.
2. `tools/materialize-pcb-r13-route1az-r304-gnd.py` loads route-1ay.
3. Materializer validates R304 identity and fixed pad geometry.
4. One GND track and one GND through-via are added.
5. Board zones are refilled and connectivity is rebuilt.
6. `kicad-cli pcb drc --format json --severity-all` produces route-1az DRC evidence.
7. `tools/audit-pcb-pin-nets.py` compares physical PCB pin/net connectivity against the recovered r8 logical XML.
8. Explicit route-1az gates validate the only permitted geometry mutation and frozen regions.
9. The acceptance record captures the successful execution provenance.

## State transition

`route-1az CANDIDATE`
→ dedicated workflow success
→ evidence reviewed against invariants
→ `route-1az ACCEPTED_EXECUTED_KICAD`

Failure of any gate leaves route-1ay as authority.

## Files to change

### New

- `docs/pcb-route-r13-1az-validation.json`
- `tools/reproduce-route1az-accepted.sh`
- `.github/workflow-archive/r13/r13-route1az-r304-gnd-validation.yml`
- `docs/ai/issues/4/IMPLEMENTATION_PLAN.md`
- `docs/ai/issues/4/HUMAN_UNDERSTANDING.md`

### Delete

- `.github/workflows/r13-route1az-r304-gnd-validation.yml`

### External repository metadata

- Draft PR #2 body
- Issue #4 body/checklists/result

## API changes

None.

## DB changes / migrations

None.

## Error handling

The accepted reproducer is fail-closed:

- shell uses `set -euo pipefail`
- source baseline must independently pass before route-1az is materialized
- any DRC count drift fails
- any ratsnest count drift fails
- any audit count/result drift fails
- any R304 identity or coordinate drift fails
- any unexpected route scope or placement change fails
- any RF/supplier-gated mutation fails

## Security considerations

- no credential or Secret changes
- no external input is trusted as electrical authority
- no design-rule waiver
- no via-in-pad exception
- no RF mutation
- no supplier-gated interface mutation
- no personal or identifiable health information

## Testing strategy

### Executed evidence already available

Workflow run `33221754996`, job `99017070424`:

- completed: success
- KiCad 9.0.9
- 0 rule violations
- 123 unconnected items
- PASS / 268 audited nodes
- 1 segment + 1 via
- zero moves/rotations
- R304 identity/nets/geometry gates passed
- predecessor geometry preserved
- RF and supplier-gated interfaces untouched

Artifact:

- ID `9705459069`
- name `r13-route1az-r304-gnd-evidence`
- digest `sha256:7e4f7091235fadcece258811a9658bdb1ded3d557e7beac00eaaa6d8c81021ec`
- size 76884 bytes

Materializer-reported route-1az PCB SHA-256:

`29a90df3ff7ef6fd038a68bf3bc3e91ae6c9ce6c79ed742eb57b1dcf7b400a4f`

### Repository verification

After implementation:

- fetch final files from GitHub and compare contents against plan
- verify active workflow is absent and archived workflow is present
- inspect branch head/diff for unrelated changes
- inspect PR #2 text
- inspect Issue #4 completion state

## Implementation order

1. Freeze Issue #4 requirements and base SHA.
2. Write this plan and Human Understanding summary.
3. Run review passes below.
4. Create accepted route-1az evidence JSON.
5. Create accepted route-1az reproducer.
6. Copy the successful workflow into archive.
7. Remove the active workflow.
8. Review resulting files and branch history.
9. Update Draft PR #2.
10. Update Issue #4 with actual result and verification.

## Pre-Implementation Review

### Pass 1 — Requirements

Result: **PASS with one clarification adopted**.

Clarification: route-1az already exists at the Base Revision, so implementation must not rewrite or “improve” its geometry. This task is acceptance/promotion only.

### Pass 2 — Architecture

Result: **PASS**.

Adopted:
- reuse route-1ay accepted-baseline pattern exactly;
- keep generated PCB directory ephemeral;
- archive the one-shot candidate workflow.

Rejected:
- direct check-in of generated route-1az PCB;
- creating a new generalized routing framework during an acceptance-only task.

### Pass 3 — Risk

Result: **PASS with controls**.

Controls:
- pin workflow/job/head provenance explicitly;
- preserve `NOT_FOR_GERBER`;
- preserve the historical-byte-identity policy;
- keep all difficult/frozen nets deferred;
- validate final diff for scope creep.

No security-critical design choice remains unresolved.

## Rollback

Fully reversible.

If acceptance metadata or reproducer is later shown incorrect:

- revert the acceptance commit(s);
- restore route-1ay as routing authority;
- re-enable/correct the candidate workflow;
- do not alter the already accepted route-1ay data.

No database or irreversible data migration exists.

## Known risks

- GitHub Actions artifact contents may expire; durable acceptance must therefore preserve the essential observed electrical gates in repository text.
- A future KiCad version could regenerate byte-different PCB files; this is expected and does not supersede the explicit electrical/geometry gates.
- route-1az is not manufacturing approval and does not reduce the remaining supplier, RF, charging, or full-routing gates.
