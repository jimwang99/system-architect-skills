---
status: rejected
created: 2026-07-19
decided: 2026-07-20
---

# GraphQL public API

## Context

Clients requested flexible queries.

## Decision

Expose a GraphQL endpoint alongside REST.

## Alternatives Considered

- **REST with sparse fieldsets** — rejected because clients still needed joins.

## Consequences

Recorded as rejected: schema governance cost outweighed client flexibility.
