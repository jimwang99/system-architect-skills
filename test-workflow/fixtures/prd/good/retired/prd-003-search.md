# Search

## Purpose

Let users find products by keyword.

## Users

Signed-in shoppers on web.

## Non-goals

No faceted filtering. No full-text ranking.

## Constraints

Latency under 500 ms at p99 for the catalogue size.

## Success criteria

Search CTR is measurable per release.

## Requirements

- Retired: REQ-001, REQ-003

### REQ-002 — Keyword search

- Statement: A user can search products by keyword and see matching results.
- Acceptance:
  - A query returns products whose title or description contains the keyword.
  - An empty result set shows a zero-results message.

### REQ-004 — Search analytics

- Statement: Each search query is logged for analytics.
- Acceptance:
  - Every search query is written to the analytics event stream.
  - The event includes the keyword and result count.
