# Repository Agent Instructions

This file is the thin control layer for repository work. Durable investigation and decision knowledge lives under `.ai/`; do not expand this file into a knowledge dump.

## Task start

1. Understand the current user request and preserve the current development objective.
2. Inspect the current code, Git branch/status/history, active changes, tests, CI, open Issues/PRs, and instructions relevant to the task.
3. Read `.ai/index.md`.
4. Extract the current domain, files, symbols, errors, interfaces, and other useful search terms.
5. Search `.ai/` with targeted tools such as `rg`, `grep`, filenames, keywords, and Git history.
6. Read only the highest-relevance records, then validate them against the current repository state.
7. Never load all External Intelligence or all cases by default.

## Issue-first development workflow

For significant implementation, bug fixing, hardware changes, refactors, or investigations that can change repository behavior or design:

1. Perform repository reconnaissance before modifying implementation files. Inspect actual source and validation structure, not README alone.
2. Create or identify a dedicated GitHub Issue before new implementation. Record the **Base Commit SHA**, current state, scope/out-of-scope, observable acceptance criteria, verification plan, risks, and an implementation checklist.
3. When important alternatives exist, record the options and the selected rationale. For medium/large work, add a concise implementation plan or human-understanding note only when it improves reviewability; do not create documentation for its own sake.
4. Review the plan from three distinct perspectives before implementation: **requirements coverage**, **architecture/duplication**, and **risk/regression/security**. Triage findings rather than accepting them mechanically.
5. Implement within Issue scope, reuse existing repository patterns, and avoid unnecessary dependencies or abstractions. If a material premise changes, update the Issue/design record before changing direction.
6. Execute every relevant repository verification that is available: tests, lint, typecheck, build, DRC, audits, or other domain-specific gates. Never report an unexecuted check as passing.
7. Review the completed change for correctness, regression, architecture consistency, security, maintainability, and dead code.
8. Update the Issue with actual implementation, changed files, design deviations, executed verification/results, remaining work, and checklist state.

Use the Issue as the task/specification/status record. Use `.ai/` only for durable knowledge that can improve future decisions; do not duplicate routine Issue history into External Intelligence.

Small, trivial, or documentation-only edits may reuse an existing Issue when creating a new one would add no traceability value. Never let process documentation delay the user's actual engineering result.

For safe, reversible ambiguity, choose the most reasonable repository-consistent assumption and record it when material instead of stopping for confirmation. Ask before irreversible production data loss, paid operations, credential/secret issuance or changes, direct production deployment, major specification breakage, or security-critical choices that genuinely require human selection.

## Specification priority

When requirements conflict, resolve task intent in this order:

1. the user's current explicit request
2. the dedicated GitHub Issue/specification for the task
3. current implementation and executed tests/validation
4. repository design documentation and confirmed Decisions
5. current official/primary external documentation when applicable
6. model prior knowledge

If current implementation clearly contradicts a higher-priority requirement because of a bug, record that discrepancy rather than silently treating the bug as specification.

## Evidence priority

Within an investigation or technical claim, treat stored knowledge as evidence, not immutable truth. Resolve factual conflicts in this order:

1. current implementation/code and checked-in hardware sources
2. current test, DRC, audit, or validation results
3. reproduction experiments
4. official specifications and primary sources
5. repository-confirmed Decisions
6. Validated Rules
7. Candidate Rules
8. Observations and Case Memory

If stored knowledge conflicts with the current repository, re-investigate and correct or supersede the stored entry rather than forcing current work to match stale memory.

## Retrieval

Start from `.ai/index.md`, then search selectively. Typical local flow:

```sh
rg -n "<keyword|file|symbol|error>" .ai
```

Rank results by direct relevance to the current task. Read current code before applying an old conclusion.

## Knowledge updates

At the end of meaningful work, ask whether the result will change a future decision, prevent repeated investigation/failure, preserve a non-obvious rationale, or provide reusable evidence. Save it only when the answer is yes.

Before adding an entry, search `.ai/` for equivalent knowledge. Prefer updating evidence, confidence, related cases, or lifecycle state over creating duplicates. Promote knowledge only through `Case -> Observation -> Candidate Rule -> Validated Rule` when the evidence supports promotion.

Do not store trivial work logs, raw tool output, README/source copies, facts easily re-derived from current code, unsupported guesses, or temporary status noise.

## Security and privacy

Never store API keys, private keys, seed phrases, tokens, passwords, credentials, confidential `.env` values, or unnecessary personal information in External Intelligence. Record only an abstract dependency on a credential when that fact itself is useful.

## Git safety

Preserve the active branch and in-progress work. Re-check the current branch HEAD immediately before writes when parallel work is possible. Do not reset, discard, force-push, or rewrite unrelated history to maintain process documentation or External Intelligence. Product results, correctness, security, and executed validation take priority over process maintenance.
