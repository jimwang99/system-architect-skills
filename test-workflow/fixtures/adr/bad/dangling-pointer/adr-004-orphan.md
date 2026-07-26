---
status: accepted
created: 2026-07-22
decided: 2026-07-23
supersedes: adr-009-missing.md
---

# Orphan

## Context

Synchronous coupling from adr-002 caused cascading outages.

## Decision

Move inter-service calls to an async queue.

## Alternatives Considered

- **Retry budgets on sync calls** — rejected because it treats the symptom, not the coupling.

## Consequences

Availability decouples; eventual consistency enters the domain.
