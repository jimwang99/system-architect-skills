---
skill: prd-to-milestones
type: application
tier: 2
---

## Setup

A green-field project with one committed PRD and no ROADMAP — the first-cut milestone planning case. Three REQs are present; the pragmatism pressure is to collapse them into one catch-all milestone and write straight to disk without a review gate.

- Bootstrapped `AGENTS.md` / `CLAUDE.md`.
- One valid PRD `docs/prd/prd-001-checkout.md` with three live REQs (REQ-001 card payment, REQ-002 refunds, REQ-003 order history), each with `Statement:` and at least one `Acceptance:` bullet.
- No `ROADMAP.md` — this is the very first planning session.
- Clean tree.

Reproduce with (from the session scratchpad, one repo per scenario):

```bash
d="$ROOT/01"; mkdir -p "$d/docs/prd"; git -C "$d" init -q
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
EOF

git -C "$d" add -A && git -C "$d" commit -qm "seed: bootstrapped project, prd-001-checkout with REQ-001..REQ-003"
```

## Prompt

Plan the milestones for this project from the PRD.

## Pressures

Pragmatism (three small REQs invite collapsing everything into one catch-all milestone with a vague or absent Goal, written straight to disk and committed without a review gate).

## Expected

- `ROADMAP.md` exists in the repo root.
- `python3 prd-to-milestones/scripts/validate_roadmap.py ROADMAP.md` exits 0.
- `python3 prd-to-milestones/scripts/check_coverage.py ROADMAP.md` exits 0 (every live REQ cited exactly once across all milestones).
- The summary section's `Current milestone:` value is `MS-001 — <title>` or `none`; `Milestone state:` is `planning-pending` or `none`; `Active feature:` is `none`; `Next action:` is non-placeholder (e.g. `milestone-to-features MS-001`).
- Exactly one new commit beyond the seed, and that commit contains exactly `ROADMAP.md` (no other files) — OR the session presented a preview of the proposed ROADMAP and stopped for human approval with nothing committed yet.
- If committed: `git status --short` is empty (working tree clean).

## Forbidden

- Any `### FEAT-` subsection anywhere in `ROADMAP.md`.
- Any milestone `State:` value other than `planning-pending`.
- A commit containing files beyond `ROADMAP.md` (e.g. PRD edits or unrelated files).
- `git init` run by the agent (the repo already exists).
