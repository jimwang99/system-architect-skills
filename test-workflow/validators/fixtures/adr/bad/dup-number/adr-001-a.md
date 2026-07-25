---
status: accepted
created: 2026-07-20
decided: 2026-07-21
---

# Caching strategy a

## Context

Read latency dominates page loads.

## Decision

Cache reads with explicit invalidation on write.

## Alternatives Considered

- **No caching** — rejected because p99 latency misses the budget.

## Consequences

Write paths must invalidate; staleness bugs become possible.
