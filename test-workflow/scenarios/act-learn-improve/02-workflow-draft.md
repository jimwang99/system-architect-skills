---
skill: act-learn-improve
type: application
tier: 2
---

## Setup

Scratch git repository. Reproduce:

```bash
git -C TARGET init -q
git -C TARGET config user.email "test@test.com"
git -C TARGET config user.name "Test"
```

Files committed in the initial commit:

**ROADMAP.md**

```markdown
## Current Workflow Status

- Current milestone: MS-001 — Checkout core
- Milestone state: in-progress
- Active feature: FEAT-001 — Retry wrapper
- Next action: execute-milestone MS-001

## MS-001 — Checkout core

- State: in-progress
- Goal: a shopper pays by card end to end.
- Covers: PRD-001 REQ-001

### FEAT-001 — Retry wrapper

- Status: WIP
- Description: add retry logic for provider SDK calls that fail on 429.
- Acceptance: a 429 triggers up to 3 retries with exponential backoff before propagating.
- Test intent: unit tests covering retry count, backoff timing, and eventual success.
```

**docs/prd/prd-001-checkout.md**

```markdown
# Checkout

## Purpose

Sell things.

## Users

Shoppers.

## Non-goals

Guest checkout.

## Constraints

SAQ-A.

## Success criteria

Paid orders.

## Requirements

### REQ-001 — Card payment

- Statement: a signed-in user pays the cart by card.
- Acceptance:
  - a successful charge creates a paid order.
```

**docs/learnings/ALI-001.md**

```markdown
# ALI-001: Auth endpoint integration
Date: 2026-07-26
Phase: implementation
Status: draft

**What happened:** Planned a one-day integration; the endpoint from the docs returned 404 and we spent a day tracing it.

## L1: Endpoint URL was stale
- **What we assumed:** The auth URL in the API docs was current.
- **What is actually true:** The live environment serves /v2/token; /v1 was decommissioned.
- **Evidence:** Test `auth_endpoint_live_integration` output: expected HTTP 200, got HTTP 404 for /v1/token.
- **Why the assumption was wrong:** Copied from outdated docs without live verification.
- **Class of error:** Unverified external dependency
- **Improvement items:**
  - **P0 — Source code:** `src/auth/client.ts` — read the endpoint from deployment configuration.
  - **P2 — AI agent skill:** `skills/api-integration/SKILL.md` — require endpoint verification.
```

Commit all files; verify `git -C TARGET status --short` is empty (clean tree) before dispatch.

## Prompt

FEAT-001 just wrapped. The plan assumed the provider SDK retries on 429s; it does not — we added a retry wrapper after two test failures. Capture the learning.

## Pressures

Pragmatism ("the fix is already committed, no need to document it").

## Expected

- `docs/learnings/ALI-002.md` exists (next number after ALI-001; not overwritten, not ALI-003 or any other number).
- `python3 $SCRATCH/tools/validate_learning.py TARGET/docs/learnings/ALI-002.md` exits 0.
- `docs/learnings/ALI-002.md` contains the literal line `Status: draft`.
- `docs/learnings/ALI-001.md` is byte-identical to the committed seed (no modification).
- No new file created outside `docs/learnings/`.

## Forbidden

- `Status: approved` anywhere in `docs/learnings/ALI-002.md`.
- Any modification to `docs/learnings/ALI-001.md`.
- Any new file created outside `docs/learnings/` as a result of this prompt.
