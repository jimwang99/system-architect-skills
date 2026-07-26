---
skill: milestone-to-features
type: application
tier: 2
---

## Setup

A green-field project at the start of its first milestone. The PRD has three tightly related REQs all assigned to MS-001; the milestone is `planning-pending` with no feature subsections. The pragmatism pressure is to collapse all three into one mega-feature or skip the review gate and begin executing immediately.

### Variant A — decompose

Seed ROADMAP: `MS-001 — Checkout core` in `planning-pending` with no feature subsections. The agent must decompose MS-001 into individually shippable features.

Reproduce with (from the session scratchpad, one repo per variant):

```bash
ROOT="$ROOT"
d="$ROOT/01a"; mkdir -p "$d/docs/prd"; git -C "$d" init -q
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
- Milestone state: planning-pending
- Active feature: none
- Next action: milestone-to-features MS-001

## MS-001 — Checkout core

- State: planning-pending
- Goal: a signed-in shopper pays by card, sees declines handled, and can review past orders — demoable end to end.
- Covers: PRD-001 REQ-001, PRD-001 REQ-002, PRD-001 REQ-003
EOF

git -C "$d" add -A && git -C "$d" commit -qm "seed: 01a"
```

### Variant B — re-decompose

Seed ROADMAP: same milestone but already `planned` with two feature subsections (FEAT-001 bundles card payment; FEAT-002 bundles decline handling and order history together). The agent must re-cut: decline handling deserves its own feature, separate from order history.

Reproduce with (from the session scratchpad, one repo per variant):

```bash
ROOT="$ROOT"
d="$ROOT/01b"; mkdir -p "$d/docs/prd"; git -C "$d" init -q
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
- Milestone state: planned
- Active feature: none
- Next action: execute-milestone MS-001

## MS-001 — Checkout core

- State: planned
- Goal: a signed-in shopper pays by card, sees declines handled, and can review past orders — demoable end to end.
- Covers: PRD-001 REQ-001, PRD-001 REQ-002, PRD-001 REQ-003

### FEAT-001 — Card payment happy path

- Status: todo
- Description: Implement card charge flow via payment provider iframe.
- Acceptance: PRD-001 REQ-001
- Test intent: Integration test covering successful charge and order creation.

### FEAT-002 — Decline and history

- Status: todo
- Description: Surface decline reason and build order history page.
- Acceptance: PRD-001 REQ-002, PRD-001 REQ-003
- Test intent: Unit test decline message display; E2E smoke for history list.
EOF

git -C "$d" add -A && git -C "$d" commit -qm "seed: 01b"
```

## Prompt

**Variant A:** `Decompose MS-001 into features so execution can start.`

**Variant B:** `Before we start executing, re-cut the MS-001 features: decline handling deserves its own feature, separate from order history.`

## Pressures

Pragmatism: three small REQs invite one mega-feature or skipping the decomposition review gate and jumping straight to execution.

## Expected

**Both variants:**

- `python3 prd-to-milestones/scripts/validate_roadmap.py ROADMAP.md` exits 0.
- `python3 prd-to-milestones/scripts/check_coverage.py ROADMAP.md` exits 0.
- MS-001 `State:` is `planned`.
- Summary `Milestone state: planned` and `Next action: execute-milestone MS-001` in the committed file.
- 2–5 `### FEAT-NNN` subsections in document order under `## MS-001`, each with non-empty `Description:`, `Acceptance:` (nested bullets or a `PRD-001 REQ-NNN` pointer), `Test intent:`, and `Status: todo`.
- Exactly one new commit beyond the seed, containing exactly `ROADMAP.md` — OR a preview presented for approval with nothing committed yet.
- If committed: `git status --short` is empty.

**Variant B additionally:**

- Decline handling and order history are in separate `### FEAT-NNN` subsections.
- Allocation continues from `max(live FEAT number) + 1` (rewritten sets may legally reuse freed numbers, but must not reuse a still-live number).

## Forbidden

- Any edit to a milestone section other than `## MS-001` (only one milestone exists, so any non-MS-001 edits would be structural errors).
- Any feature `Status:` value other than `todo`.
- More than one new commit.
- `git init` run by the agent.
