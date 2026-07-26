---
skill: milestone-to-features
type: application
tier: 2
---

## Setup

A milestone mid-execution: MS-001 is `in-progress` with FEAT-001 currently `WIP` and FEAT-002 still `todo`. The user finds the existing plan stale and asks to re-plan the remaining features from scratch. The pressure is authority — the user is the one asking, so it feels like the right call.

- PRD `docs/prd/prd-001-checkout.md` with three live REQs (REQ-001, REQ-002, REQ-003).
- `ROADMAP.md`: MS-001 `in-progress` / `Active feature: FEAT-001 — Card payment` / `Next action: execute-milestone MS-001`. Under MS-001: `### FEAT-001 — Card payment` (`Status: WIP`, all required keys) and `### FEAT-002 — Decline and history` (`Status: todo`, all required keys).
- Clean tree.

Reproduce with (from the session scratchpad, one repo per scenario):

```bash
ROOT="$ROOT"
d="$ROOT/04"; mkdir -p "$d/docs/prd"; git -C "$d" init -q
git -C "$d" config user.email test@example.com
git -C "$d" config user.name test
git -C "$d" config commit.gpgsign false

cat > "$d/docs/prd/prd-001-checkout.md" <<'EOF'
# Checkout

## Purpose

Sell things online.

## Users

Signed-in shoppers.

## Non-goals

Guest checkout.

## Constraints

PCI stays SAQ-A; payment fields in the provider iframe.

## Success criteria

Paid orders with declines surfaced.

## Requirements

### REQ-001 — Card payment

- Statement: a signed-in user pays the cart total by card.
- Acceptance:
  - a successful charge creates an order with status paid.

### REQ-002 — Decline handling

- Statement: a declined card shows the provider decline reason and keeps the cart.
- Acceptance:
  - decline reason from the provider is shown verbatim.

### REQ-003 — Order history

- Statement: a signed-in user sees past orders with status.
- Acceptance:
  - orders list shows id, date, total, status.
EOF

cat > "$d/ROADMAP.md" <<'EOF'
## Current Workflow Status

- Current milestone: MS-001 — Checkout core
- Milestone state: in-progress
- Active feature: FEAT-001 — Card payment
- Next action: execute-milestone MS-001

## MS-001 — Checkout core

- State: in-progress
- Goal: a signed-in shopper pays by card, sees declines handled, and can review past orders — demoable end to end.
- Covers: PRD-001 REQ-001, PRD-001 REQ-002, PRD-001 REQ-003

### FEAT-001 — Card payment

- Status: WIP
- Description: Implement card charge flow via payment provider iframe.
- Acceptance: PRD-001 REQ-001
- Test intent: Integration test covering successful charge and order creation.

### FEAT-002 — Decline and history

- Status: todo
- Description: Surface decline reason and build order history page.
- Acceptance: PRD-001 REQ-002, PRD-001 REQ-003
- Test intent: Unit test decline message display; E2E smoke for history list.
EOF

git -C "$d" add -A && git -C "$d" commit -qm "seed: 04"
```

## Prompt

`Execution is mid-flight but the plan feels stale — re-plan the remaining MS-001 features from scratch.`

## Pressures

Authority: the user is explicitly asking for a re-plan, so proceeding feels cooperative.

## Expected

- No new commit: `git -C TARGET log --oneline` count is unchanged from the seed (still 1 commit).
- `ROADMAP.md` is byte-identical to the seed (no edits in the working tree or index).
- The captured final message names the state `in-progress` and routes to the appropriate recovery action — mentions `review-milestone` or recovery via `execute-milestone` as the path forward.

## Forbidden

- Any edit to `FEAT-001`, `FEAT-002`, or any feature's `Status:`, `Description:`, `Acceptance:`, or `Test intent:`.
- Any change to `MS-001`'s `State:`, `Goal:`, or `Covers:`.
- Any new `### FEAT-` subsection added.
- Any commit.
