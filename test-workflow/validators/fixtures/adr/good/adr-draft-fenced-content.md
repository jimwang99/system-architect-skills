---
status: proposed
created: 2026-07-25
---

# Fenced content

## Context

Log lines sometimes contain markdown-shaped text.

## Decision

Ship the reference parser configuration below.

```text
# not a title
## Decision
- **not an alternative** — this line is data, not a bullet.
```

## Alternatives Considered

- **Hand-rolled regex** — rejected because it breaks on nested markup.

## Consequences

```text
code-only section: the block itself is the consequence table
```
