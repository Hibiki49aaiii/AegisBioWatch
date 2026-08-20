# Repository Agent Instructions

This file is the thin control layer for repository work. Durable investigation and decision knowledge lives under `.ai/`; do not expand this file into a knowledge dump.

## Task start

1. Understand the current user request and preserve the current development objective.
2. Inspect the current code, Git branch/status/history, active changes, tests, and CI relevant to the task.
3. Read `.ai/index.md`.
4. Extract the current domain, files, symbols, errors, interfaces, and other useful search terms.
5. Search `.ai/` with targeted tools such as `rg`, `grep`, filenames, keywords, and Git history.
6. Read only the highest-relevance records, then validate them against the current repository state.
7. Never load all External Intelligence or all cases by default.

## Evidence priority

Treat stored knowledge as evidence, not immutable truth. Resolve conflicts in this order:

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

Preserve the active branch and in-progress work. Do not reset, discard, force-push, or rewrite unrelated history to maintain External Intelligence. External Intelligence is secondary to the requested product result, correctness, security, and validation.
