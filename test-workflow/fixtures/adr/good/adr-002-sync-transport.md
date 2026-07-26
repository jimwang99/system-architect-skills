---
status: superseded
created: 2026-07-18
decided: 2026-07-19
superseded-by: adr-003-async-transport.md
---

# Synchronous transport

## Context

Services call each other directly.

## Decision

Use synchronous HTTP between services.

## Alternatives Considered

- **Message queue** — rejected because operational cost seemed high at the time.

## Consequences

Simple call graphs; availability couples services.
