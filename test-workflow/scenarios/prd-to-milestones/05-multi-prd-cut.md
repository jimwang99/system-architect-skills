---
skill: prd-to-milestones
type: application
tier: 2
---

## Setup

A project with two committed PRDs and no ROADMAP — the first-cut milestone planning case at multi-PRD scale. Five live REQs across two PRDs must all be covered exactly once. No additional pressures beyond scale (coverage completeness across both PRDs).

- Bootstrapped `AGENTS.md` / `CLAUDE.md`.
- Two valid PRDs: `docs/prd/prd-001-checkout.md` (REQ-001 card payment, REQ-002 refunds, REQ-003 order history) and `docs/prd/prd-002-search.md` (REQ-001 keyword search, REQ-002 search filters).
- No `ROADMAP.md`.
- Clean tree.

Reproduce with (from the session scratchpad, one repo per scenario):

```bash
d="$ROOT/05"; mkdir -p "$d/docs/prd"; git -C "$d" init -q
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

cat > "$d/docs/prd/prd-002-search.md" <<'EOF'
# Search

## Purpose

Let shoppers find products by keyword and filter the results.

## Users

All shoppers (signed-in and anonymous) on web and mobile.

## Non-goals

No semantic or AI-powered search. No cross-catalogue federation.

## Constraints

Query latency p95 under 300 ms at current catalogue size.

## Success criteria

Search-to-click rate is measurable per release.

## Requirements

### REQ-001 — Keyword search

- Statement: A shopper types a keyword and receives a ranked list of matching products.
- Acceptance:
  - Results appear within 300 ms at p95 under normal load.
  - Searching for an exact product name returns that product in the first page.

### REQ-002 — Search filters

- Statement: A shopper narrows results by category, price range, or rating.
- Acceptance:
  - Filters apply without a full page reload.
  - Selecting multiple filters AND-combines them.
EOF

git -C "$d" add -A && git -C "$d" commit -qm "seed: bootstrapped project, prd-001-checkout REQ-001..REQ-003, prd-002-search REQ-001..REQ-002, no ROADMAP"
```

## Prompt

Plan milestones covering everything we have.

## Pressures

None beyond scale — the test is whether coverage completeness holds across two PRDs.

## Expected

- `ROADMAP.md` exists in the repo root.
- `python3 prd-to-milestones/scripts/validate_roadmap.py ROADMAP.md` exits 0.
- `python3 prd-to-milestones/scripts/check_coverage.py ROADMAP.md` exits 0 (all five live REQs — PRD-001 REQ-001/002/003 and PRD-002 REQ-001/002 — cited exactly once across milestones).
- At least two milestones, each with a `Goal:` that is non-empty and non-placeholder per `validate_roadmap`'s placeholder check (exit 0 already implies it).
- Exactly one new commit beyond the seed, containing exactly `ROADMAP.md`; OR the session presented a preview and stopped for human approval with nothing committed yet.
- The summary's `Current milestone:` points at `MS-001` (or `none` if no commit yet); `Active feature:` is `none`; `Next action:` is non-placeholder.

## Forbidden

- Any live REQ (PRD-001 REQ-001/002/003; PRD-002 REQ-001/002) absent from every milestone's `Covers:` (an uncited REQ).
- Any REQ cited in more than one milestone's `Covers:` (a double-cited REQ).
- Any `### FEAT-` subsection anywhere in `ROADMAP.md`.
