---
status: proposed
created: 2026-07-25
---

# Structured log format

## Context

Services emit free-text logs that cannot be queried.

## Decision

## Alternatives Considered

- **Keep free-text logs** — rejected because queries require fragile regexes.

## Consequences

All services need a logging shim; dashboards become queryable.
