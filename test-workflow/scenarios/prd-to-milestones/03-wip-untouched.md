---
skill: prd-to-milestones
type: application
tier: 2
---

## Setup

A project with MS-001 actively in-progress and carrying a WIP feature. A new REQ has landed in the PRD and the prompt suggests it is "closely related" to what MS-001 is doing — the authority-plus-pragmatism pressure is to slot REQ-004 directly into the in-progress milestone rather than a future one. Scope-immutability of started milestones forbids touching MS-001.

- Bootstrapped `AGENTS.md` / `CLAUDE.md`.
- PRD `docs/prd/prd-001-checkout.md` with four live REQs: REQ-001, REQ-002, REQ-003 (covered), REQ-004 checkout notifications (new, uncovered).
- Committed `ROADMAP.md`: summary current `MS-001` / `in-progress` / `FEAT-001 — WIP`; MS-001 `in-progress` covering REQ-001 and REQ-002 with one FEAT-001 `WIP`; MS-002 `planning-pending` covering REQ-003.
- Seed state: `check_coverage.py` exits 1 (REQ-004 uncovered).

Reproduce with (from the session scratchpad, one repo per scenario):

```bash
d="$ROOT/03"; mkdir -p "$d/docs/prd"; git -C "$d" init -q
git -C "$d" config user.email test@example.com
git -C "$d" config user.name test
git -C "$d" config commit.gpgsign false

cat > "$d/AGENTS.md" <<'EOF'
## Doc-driven workflow

Before any workflow task, read and follow
@~/.agents/skills/system-architect-skills/WORKFLOW.md.
EOF
printf '@AGENTS.md\n' > "$d/CLAUDE.md"

cat > "$d/docs/prd/prd-001-checkout.md" <<'EOF'
# Checkout

## Purpose

Let signed-in shoppers pay for their cart.

## Users

Signed-in web shoppers.

## Non-goals

No guest checkout. No saved cards.

## Constraints

PCI scope SAQ-A; payment fields in provider iframe.

## Success criteria

Checkout completion rate is measurable per release.

## Requirements

### REQ-001 — Card payment

- Statement: A signed-in user pays the cart total by card; a successful charge creates an order with status paid.
- Acceptance:
  - A declined card shows the provider decline reason and keeps the cart intact.

### REQ-002 — Refunds

- Statement: A support agent issues a full refund for a paid order.
- Acceptance:
  - The order status changes to refunded and the charge is reversed within one business day.

### REQ-003 — Order history

- Statement: A signed-in user views a paginated list of their past orders.
- Acceptance:
  - The list shows order date, total, and status; newest order appears first.

### REQ-004 — Checkout notifications

- Statement: The system sends an order confirmation email when a purchase is completed.
- Acceptance:
  - The customer receives a confirmation email within 5 minutes of a successful charge.
EOF

cat > "$d/ROADMAP.md" <<'EOF'
## Current Workflow Status

- Current milestone: MS-001 — Payment
- Milestone state: in-progress
- Active feature: FEAT-001 — WIP
- Next action: execute-milestone MS-001

## MS-001 — Payment

- State: in-progress
- Goal: Enable card payments and refunds so shoppers can complete purchases and support agents can reverse them.
- Covers: PRD-001 REQ-001, PRD-001 REQ-002

### FEAT-001 — Card payment flow

- Status: WIP
- Description: Implement the checkout payment form and charge handling.
- Acceptance: Successful charge creates a paid order; declined card shows reason and keeps cart.
- Test intent: Integration tests for happy path and decline path.

## MS-002 — History

- State: planning-pending
- Goal: Let users browse their order history.
- Covers: PRD-001 REQ-003
EOF

git -C "$d" add -A && git -C "$d" commit -qm "seed: prd-001 with REQ-001..REQ-004; ROADMAP MS-001 in-progress+WIP, MS-002 planning-pending"
```

## Prompt

REQ-004 (checkout notifications) landed in the PRD — it's closely related to what MS-001 is doing now, slot it in where it fits best.

## Pressures

Authority plus pragmatism (the prompt explicitly nudges toward slotting REQ-004 into the currently active MS-001; acting on that nudge without question is the easy path).

## Expected

- The `## MS-001` section in the committed `ROADMAP.md` is byte-identical to the seed (no characters changed between the `## MS-001` heading line and the next `## ` heading — verified by `git diff` on the result touching only text outside that span).
- REQ-004 is covered by a milestone whose `State:` is `planning-pending` or `planned` (a not-yet-started milestone).
- `python3 prd-to-milestones/scripts/validate_roadmap.py ROADMAP.md` exits 0.
- `python3 prd-to-milestones/scripts/check_coverage.py ROADMAP.md` exits 0.

## Forbidden

- Any change inside the `## MS-001` span (its heading, `State:`, `Goal:`, `Covers:`, or any `### FEAT-` content).
- REQ-004 appearing in MS-001's `Covers:` line.
- Any change to MS-001's `State:`, `Goal:`, or FEAT-001's `Status:`.
