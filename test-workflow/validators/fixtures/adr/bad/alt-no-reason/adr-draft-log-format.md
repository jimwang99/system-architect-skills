---
status: proposed
created: 2026-07-25
---

# Structured log format

## Context

Services emit free-text logs that cannot be queried.

## Decision

Adopt JSON-lines logs with a fixed field set.

## Alternatives Considered

- **Keep free-text logs**

## Consequences

All services need a logging shim; dashboards become queryable.
