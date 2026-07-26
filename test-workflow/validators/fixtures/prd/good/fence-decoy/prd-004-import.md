# Import

## Purpose

Let merchants upload product catalogues via CSV.

## Users

Merchant administrators.

## Non-goals

No real-time sync. No XML import.

## Constraints

```
## Requirements

### R-99 — Fake
This block is inside a fenced section and must be ignored.
```

PCI scope is not relevant here.

## Success criteria

Import success rate is measurable per release.

## Requirements

### R-01 — Upload CSV

- Statement: A merchant uploads a CSV file and the products are created.
- Acceptance:
  - A valid CSV creates one product per row.
  - An invalid row produces a line-level error and skips that row.
  - After upload a summary shows created and skipped counts.
