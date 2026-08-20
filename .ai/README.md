# Codex External Intelligence

`.ai/` is a selective, evidence-backed memory layer for repository work. Its purpose is to reduce repeated investigation while keeping current code and current validation authoritative.

## Knowledge model

- **Case Memory**: a bounded issue, feature, investigation, or validation outcome.
- **Observation**: a potentially reusable fact seen in one or more cases, not yet a general rule.
- **Failure Memory**: a failed approach worth avoiding or recognizing later.
- **Decision**: a deliberate architecture, process, compatibility, security, or engineering choice and its rationale.
- **Candidate Rule**: an observation with enough repeated or primary-source evidence to consider operationalizing.
- **Validated Rule**: a scoped, actionable rule with reproducible evidence and known exceptions.
- **Reusable Intelligence**: stable repository-specific invariants, relationships, and high-value operating knowledge.

Normal lifecycle:

```text
Case Memory -> Observation -> Candidate Rule -> Validated Rule
```

Promotion is not automatic. A single observation does not become a rule merely because it sounds plausible.

## Retrieval workflow

```text
Current task
  -> identify domain/files/errors/keywords
  -> read .ai/index.md
  -> targeted search under .ai/
  -> rank likely entries
  -> read only relevant entries
  -> inspect current code/hardware sources
  -> revalidate old knowledge against current reality
  -> implement/test/verify
```

Use `rg`, `grep`, filenames, keywords, and Git history first. Do not `cat` the entire `.ai/` tree into context.

## Writing quality gate

Persist knowledge only when it can reasonably:

- reduce a future investigation,
- prevent a repeated failure,
- change a future engineering decision,
- preserve a non-obvious reason not recoverable from code alone,
- preserve reusable evidence, or
- document an important deliberate decision.

Otherwise do not save it.

## Deduplication

Search before writing. If a close entry already exists, add new evidence, update confidence, link another case, or promote/supersede the existing record. Avoid parallel documents that state the same rule in different words.

## Confidence

- **low**: hypothesis, single weak observation, or insufficient reproduction.
- **medium**: reproduced or supported by multiple facts, but generalization is still uncertain.
- **high**: supported by independent cases and/or tests/specification/implementation, with applicability and exceptions understood.

Never assign high confidence from intuition alone.

## Evidence first

Prefer file paths, commits, PR/issues, commands, test/DRC/audit results, reproducible experiments, and primary specifications. Summarize outputs; do not paste raw logs when a concise result and source are sufficient.

## Security

Do not store secrets or unnecessary personal information. If a credential dependency matters, record only that a credential is required, never the credential value.

## Git and evolution

`.ai/` is intentionally versioned so knowledge changes are reviewable. When knowledge becomes wrong, prefer `corrected`, `superseded`, or `rejected` state with the reason and replacement rather than silently erasing useful history.

The initial implementation is Markdown + Git + local text search only. The layout leaves room for SQLite, FTS5, embeddings, vector/hybrid retrieval, or a knowledge graph later, but none should be added until measured retrieval needs justify them.

See `.ai/index.md` first. Directory indexes define the compact record formats.
