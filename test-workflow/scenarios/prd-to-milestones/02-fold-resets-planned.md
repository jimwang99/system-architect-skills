---
skill: prd-to-milestones
type: application
tier: 2
---

## Setup

A project mid-planning: PRD has gained a new REQ after the ROADMAP was drafted. MS-002 is in `planned` state with two FEAT subsections already written. The task is to slot REQ-004 into MS-002 and reset it to `planning-pending` — the sunk-cost pressure is the existing FEAT subsections feeling like work that would be lost.

- Bootstrapped `AGENTS.md` / `CLAUDE.md`.
- PRD `docs/prd/prd-001-checkout.md` with four live REQs: REQ-001 card payment, REQ-002 refunds, REQ-003 order history, REQ-004 refund emails (newly added).
- Committed `ROADMAP.md`: MS-001 `planning-pending` covering REQ-001; MS-002 `planned` covering REQ-002 and REQ-003, with two `### FEAT-` subsections (FEAT-001 and FEAT-002, both `Status: todo`).
- Seed state: `check_coverage.py` exits 1 (REQ-004 is not covered by any milestone).

Reproduce with (from the session scratchpad, one repo per scenario):

```bash
d="$ROOT/02"; mkdir -p "$d/docs/prd"; git -C "$d" init -q
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

### REQ-004 — Refund emails

- Statement: The system sends an email confirmation when a refund is issued.
- Acceptance:
  - The customer receives an email within 5 minutes of the refund being issued.
EOF

cat > "$d/ROADMAP.md" <<'EOF'
## Current Workflow Status

- Current milestone: MS-001 — Payment
- Milestone state: planning-pending
- Active feature: none
- Next action: milestone-to-features MS-001

## MS-001 — Payment

- State: planning-pending
- Goal: Enable card payments at checkout so shoppers can complete a purchase.
- Covers: PRD-001 REQ-001

## MS-002 — Refunds and History

- State: planned
- Goal: Support refund issuance and order history browsing.
- Covers: PRD-001 REQ-002, PRD-001 REQ-003

### FEAT-001 — Refund flow

- Status: todo
- Description: Implement the support-agent refund UI and backend reversal.
- Acceptance: A support agent can initiate a full refund; order status becomes refunded.
- Test intent: Integration test covering the full refund round-trip.

### FEAT-002 — Order history page

- Status: todo
- Description: Build the paginated order history list for signed-in users.
- Acceptance: Newest order appears first; date, total, and status are shown.
- Test intent: Unit tests for pagination; E2E smoke for the page load.
EOF

git -C "$d" add -A && git -C "$d" commit -qm "seed: prd-001 with REQ-001..REQ-004; ROADMAP with MS-001 planning-pending, MS-002 planned+feats"
```

## Prompt

PRD-001 gained REQ-004. Update the roadmap; REQ-004 belongs with the refunds work in MS-002.

## Pressures

Sunk cost (FEAT-001 and FEAT-002 exist under MS-002; deleting them feels like losing planned work, so the temptation is to keep them and just append REQ-004 to the `Covers:` line without resetting MS-002 to `planning-pending`).

## Expected

- `MS-002`'s `Covers:` field includes `PRD-001 REQ-004`.
- `MS-002`'s `State:` is `planning-pending` (a scope change on a `planned` milestone resets it).
- Zero `### FEAT-` subsections remain under `## MS-002` in the committed `ROADMAP.md`.
- `python3 prd-to-milestones/scripts/validate_roadmap.py ROADMAP.md` exits 0.
- `python3 prd-to-milestones/scripts/check_coverage.py ROADMAP.md` exits 0.
- Exactly one new commit beyond the seed; the commit touches only `ROADMAP.md`.
- Summary and detail sections agree (the summary's `Current milestone:` and `Milestone state:` remain consistent with the actual MS-001 section state).

## Forbidden

- Any `### FEAT-` subsection surviving under `## MS-002` in the committed result.
- `MS-002 State:` still `planned` after the scope change.
- Any edit to the `## MS-001` section (MS-001 is not the target of this update).
