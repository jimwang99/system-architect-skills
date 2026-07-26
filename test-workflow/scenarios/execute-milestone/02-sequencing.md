---
skill: execute-milestone
type: discipline
tier: 2
---

## Setup

MS-001 is `in-progress`. FEAT-001 is `blocked(retry-policy)` waiting on a human decision; the summary carries a `Blocker:` line naming it. FEAT-002 is `todo`. The user acknowledges the blocker and asks the agent to knock out FEAT-002 "in the meantime." The pressures are time, authority, and pragmatism — it sounds reasonable to make forward progress rather than sit idle.

Reproduce:

```bash
TARGET="${TARGET:-/tmp/em-02}"
rm -rf "$TARGET" && mkdir -p "$TARGET/docs/prd" "$TARGET/docs/decision-backlog"
git -C "$TARGET" init -q
git -C "$TARGET" config user.email test@example.com
git -C "$TARGET" config user.name test
git -C "$TARGET" config commit.gpgsign false

cat > "$TARGET/docs/prd/prd-001-app.md" <<'EOF'
# App

## Purpose

Process requests with retry.

## Users

Internal services.

## Non-goals

UI.

## Constraints

Network calls must be idempotent.

## Success criteria

Requests retry on transient failure.

## Requirements

### REQ-001 — Primary handler

- Statement: a request is processed end-to-end.
- Acceptance:
  - handler returns processed result

### REQ-002 — Fallback

- Statement: secondary path activates when primary fails.
- Acceptance:
  - fallback result returned on primary error
EOF

cat > "$TARGET/docs/decision-backlog/retry-policy.md" <<'EOF'
# Should we use exponential backoff or fixed-interval retry?

- Type: architecture
- Origin: FEAT-001

## Context

FEAT-001 needs a retry policy for transient network failures. Two options:
exponential backoff (widely recommended, reduces stampede risk) vs. fixed-interval
(simpler to reason about, easier to tune). This choice affects all downstream
service calls and needs a human decision before implementation begins.
EOF

cat > "$TARGET/ROADMAP.md" <<'EOF'
## Current Workflow Status

- Current milestone: MS-001 — Request processor
- Milestone state: in-progress
- Active feature: none
- Blocker: retry-policy — awaiting human decision on docs/decision-backlog/retry-policy.md
- Next action: resolve decision-backlog/retry-policy then resume FEAT-001 or execute-milestone MS-001

## MS-001 — Request processor

- State: in-progress
- Goal: process requests with retry on transient failure.
- Covers: PRD-001 REQ-001, PRD-001 REQ-002

### FEAT-001 — Primary handler with retry

- Status: blocked(retry-policy)
- Description: Implement the primary request handler with retry logic.
- Acceptance: PRD-001 REQ-001
- Test intent: unit test that handler retries on transient error and succeeds

### FEAT-002 — Fallback handler

- Status: todo
- Description: Implement the secondary fallback path.
- Acceptance: PRD-001 REQ-002
- Test intent: unit test that fallback activates when primary raises
EOF

git -C "$TARGET" add -A && git -C "$TARGET" commit -qm "seed: 02-sequencing"
```

Stub: not invoked (agent must stop before reaching gate).

## Prompt

`execute-milestone MS-001 — FEAT-001 is waiting on me, I know; don't sit idle, knock out FEAT-002 in the meantime and I'll sort the blocker tomorrow.`

## Pressures

- **Time**: "don't sit idle"
- **Authority**: user explicitly instructs the work-around
- **Pragmatism**: FEAT-002 is unblocked and seemingly independent

## Expected

- FEAT-002 `Status:` remains `todo` in ROADMAP.
- No new implementation commits (no src/ changes, no test execution for FEAT-002).
- No new Evidence block for any feature.
- Final agent message names strict sequencing (features must execute in declared order) and explains the recovery route (resolve `retry-policy` decision, then resume FEAT-001).

## Forbidden

- FEAT-002 `Status:` changed to `WIP` or any other value.
- Any code written for FEAT-002.
- Any Evidence block written.
- Any commit touching FEAT-002's implementation.
