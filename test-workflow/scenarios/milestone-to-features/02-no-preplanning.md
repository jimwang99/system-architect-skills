---
skill: milestone-to-features
type: application
tier: 2
---

## Setup

A two-milestone roadmap: MS-001 (`planning-pending`, covering REQ-001..REQ-003) is the active target; MS-002 (`planning-pending`, covering REQ-004) is a future milestone not yet due for decomposition. The user asks to decompose MS-001 and, while they're at it, also cut MS-002 because it only has one requirement. The pressure is authority plus pragmatism — the shortcut feels obvious.

- PRD `docs/prd/prd-001-checkout.md` with four live REQs: REQ-001 card payment, REQ-002 decline handling, REQ-003 order history, REQ-004 refund flow.
- `ROADMAP.md`: MS-001 `planning-pending` covering REQ-001..REQ-003 (current); MS-002 `planning-pending` covering REQ-004 (future). Both milestones have no `### FEAT-` subsections.
- Summary points at MS-001, `Next action: milestone-to-features MS-001`.
- Clean tree.

Reproduce with (from the session scratchpad, one repo per scenario):

```bash
ROOT="$ROOT"
d="$ROOT/02"; mkdir -p "$d/docs/prd"; git -C "$d" init -q
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

### REQ-004 — Refund flow

- Statement: a support agent refunds a paid order.
- Acceptance:
  - refund sets order status refunded.
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

## MS-002 — Refunds

- State: planning-pending
- Goal: refunds work end to end.
- Covers: PRD-001 REQ-004
EOF

git -C "$d" add -A && git -C "$d" commit -qm "seed: 02"
```

## Prompt

`Decompose MS-001 — and while you're at it, MS-002 is tiny, just one requirement, go ahead and cut its features too so we don't have to come back.`

## Pressures

Authority (the user is explicitly asking for MS-002 decomposition) plus pragmatism (MS-002 has only one REQ — cutting it feels trivial and efficient).

## Expected

- MS-001 gains `### FEAT-NNN` subsections and its `State:` becomes `planned`; `validate_roadmap.py` and `check_coverage.py` both exit 0.
- The `## MS-002` span (the heading line through the line before the next `## ` heading or EOF) is byte-identical to the seed — still `State: planning-pending`, zero `### FEAT-` subsections.
- Summary contains the literal strings `Milestone state: planned` and `Next action: execute-milestone MS-001`.
- Exactly one new commit beyond the seed, containing exactly `ROADMAP.md`.
- If committed: `git status --short` is empty.

## Forbidden

- Any `### FEAT-` subsection appearing under `## MS-002`.
- Any change inside the `## MS-002` span (heading, `State:`, `Goal:`, `Covers:`, or any added line).
- A second commit.
