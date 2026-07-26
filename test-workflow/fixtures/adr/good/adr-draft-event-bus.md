---
status: proposed
created: 2026-07-25
supersedes: adr-001-caching-strategy.md
---

# Event bus replaces cache invalidation

## Context

Cache invalidation from adr-001 has grown unreliable across services.

## Decision

Publish entity-change events on a bus; caches subscribe and invalidate themselves.

## Alternatives Considered

- **Shorter TTLs** — rejected because staleness windows remain user-visible.
- **None of the write paths change** — rejected because it leaves the race in place.

## Consequences

Supersedes the caching strategy once accepted; adds a broker dependency.
