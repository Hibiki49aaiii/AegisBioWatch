# Decision Memory Index

Decisions preserve deliberate engineering choices and rationale. When a decision changes, keep the old record as `superseded` and link the replacement.

Record format:

```text
# Decision title
Status: active | superseded | rejected
Date:

## Context
## Decision
## Alternatives considered
## Evidence / Rationale
## Tradeoffs
## Consequences
## Revisit when
## Related code
```

| Title | Status | Keywords | Path |
|---|---|---|---|
| Executed KiCad validation is routing acceptance authority | active | pcb, routing, kicad, drc, audit, artifact | `.ai/decisions/pcb-routing-acceptance-authority.md` |
