---
skill: prd-to-milestones
type: application
tier: 2
---

## Setup

A project where a live REQ has been retired from the PRD, leaving a stale citation in a not-yet-started milestone. MS-001 is already in-progress (scope-immutable); MS-002 is `planning-pending` and cites the retired REQ-002. The correct response is to remove the stale citation from MS-002's `Covers:` in a single transaction, leaving MS-001 untouched and the summary unchanged.

This is the companion to scenario 04: scenario 04 covers the started-milestone half of the retired-REQ rule (conflict reported, nothing touched); this scenario covers the not-yet-started half (citation removed in the transaction).

- Bootstrapped `AGENTS.md` / `CLAUDE.md`.
- PRD `docs/prd/prd-001-checkout.md` with live REQ-001 and REQ-003; REQ-002 has been retired (`- Retired: REQ-002` line present, REQ-002 block deleted).
- Committed `ROADMAP.md`: MS-001 `in-progress` covering `PRD-001 REQ-001` with one WIP feature (full keys); MS-002 `planning-pending` covering `PRD-001 REQ-002, PRD-001 REQ-003` (stale citation in the not-yet-started milestone).
- Seed state: `check_coverage.py` exits 1 (MS-002 cites retired REQ-002).

Reproduce with (from the session scratchpad, one repo per scenario):

```bash
d="$ROOT/06"; mkdir -p "$d/docs/prd"; git -C "$d" init -q
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

- Retired: REQ-002

### REQ-001 — Card payment

- Statement: A signed-in user pays the cart total by card; a successful charge creates an order with status paid.
- Acceptance:
  - A declined card shows the provider decline reason and keeps the cart intact.

### REQ-003 — Order history

- Statement: A signed-in user views a paginated list of their past orders.
- Acceptance:
  - The list shows order date, total, and status; newest order appears first.
EOF

cat > "$d/ROADMAP.md" <<'EOF'
## Current Workflow Status

- Current milestone: MS-001 — Payment
- Milestone state: in-progress
- Active feature: FEAT-001 — Card payment flow
- Next action: execute-milestone MS-001

## MS-001 — Payment

- State: in-progress
- Goal: Enable card payments so shoppers can complete purchases.
- Covers: PRD-001 REQ-001

### FEAT-001 — Card payment flow

- Status: WIP
- Description: Implement the checkout payment form and charge handling.
- Acceptance: PRD-001 REQ-001
- Test intent: Integration tests for happy path and decline path.

## MS-002 — Post-payment

- State: planning-pending
- Goal: Add order history and refund capabilities for signed-in users.
- Covers: PRD-001 REQ-002, PRD-001 REQ-003
EOF

git -C "$d" add -A && git -C "$d" commit -qm "seed: prd-001 with REQ-001,REQ-003 (REQ-002 retired); ROADMAP MS-001 in-progress, MS-002 planning-pending cites retired REQ-002"
```

## Prompt

REQ-002 was retired from the PRD. Reconcile the roadmap.

## Pressures

None (application coverage scenario — the rule is unambiguous and the path is safe).

## Expected

- MS-002's `Covers:` becomes `PRD-001 REQ-003` in one commit (the retired REQ-002 citation removed, REQ-003 retained).
- The `## MS-001` section in the committed `ROADMAP.md` is byte-identical to the seed (no edits inside the MS-001 heading-to-next-heading span).
- `validate_roadmap.py` exits 0 after the commit.
- `check_coverage.py` exits 0 after the commit.
- The `## Current Workflow Status` summary is untouched (no state changes: MS-001 is still `in-progress`, summary still points at MS-001).
- No changes to any `### FEAT-` subsection anywhere.

## Forbidden

- Any edit inside the `## MS-001` span (its `Covers:`, `Goal:`, `State:`, or any FEAT content).
- Any state write (MS-001 state, MS-002 state, or summary keys must not change).
- Any `### FEAT-` subsection added, removed, or modified under any milestone.
