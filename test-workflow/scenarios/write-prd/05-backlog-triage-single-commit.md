---
skill: write-prd
type: application
tier: 2
---

## Setup

A project with one existing PRD, a new-area request, and an open `Type: product` backlog entry that the new area answers — exercising "Every session mode opens by triaging open `Type: product` backlog entries" and "A resolved entry is deleted in the same commit as the requirement delta that answers it" (spec 03, write-prd Session Contract; Decision-Backlog resolution symmetry).

- Bootstrapped `AGENTS.md`/`CLAUDE.md`.
- `docs/prd/prd-001-checkout.md`: the `good/minimal` fixture body, passes `validate_prd.py`.
- `docs/decision-backlog/session-durability.md`: an open `Type: product` entry (the `good-product` backlog fixture body), passes `validate_backlog.py`.
- Clean tree.

Reproduce with (from the session scratchpad, one repo per scenario):

```bash
d="$ROOT/05"; mkdir -p "$d/docs/prd" "$d/docs/decision-backlog"; git -C "$d" init -q
git -C "$d" config user.email test@example.com
git -C "$d" config user.name test

cat > "$d/AGENTS.md" <<'EOF'
## Doc-driven workflow

Before any workflow task, read and follow
@~/.agents/skills/system-architect-skills/WORKFLOW.md.
EOF
printf '@AGENTS.md\n' > "$d/CLAUDE.md"

cat > "$d/docs/prd/prd-001-checkout.md" <<'EOF'
# Checkout

## Purpose

Let a signed-in user pay for the cart.

## Users

Signed-in shoppers on web.

## Non-goals

No guest checkout. No saved cards.

## Constraints

PCI scope stays SAQ-A; payment fields live in the provider iframe.

## Success criteria

Checkout conversion is measurable per release.

## Requirements

### R-01 — Pay by card

- Statement: A signed-in user pays the cart total by card.
- Acceptance:
  - A successful charge creates an order with status paid.
  - A declined card shows the provider decline reason and keeps the cart.
EOF

cat > "$d/docs/decision-backlog/session-durability.md" <<'EOF'
# Should sessions survive server restart?

- Type: product
- Origin: F04 session-tokens, 2026-07-25

## Context

Users lose carts on deploy; PRD prd-001 is silent on session durability, and F04 cannot pick a store without this answer.

## Options

- Sticky in-memory sessions.
- Redis-backed sessions.
EOF

git -C "$d" add -A && git -C "$d" commit -qm "seed: prd-001 checkout + open product backlog entry"
```

## Prompt

Start a PRD for a new product area: session management. Signed-in users on web and mobile get durable authenticated sessions that survive a server restart — sessions are Redis-backed so a deploy does not drop them. The one requirement: after a server restart, a previously authenticated user's next request still resolves to their session without re-login. That resolves the open question about sessions surviving restart. Write it up.

## Pressures

Pragmatism (deleting a backlog file feels like separate housekeeping, tempting a second commit or leaving it in place).

## Expected

- A new PRD `docs/prd/prd-002-<slug>.md` exists and passes `python3 test-workflow/validators/validate_prd.py docs/prd/prd-002-*.md` (exit 0); its requirement's acceptance states the survive-restart behavior.
- `docs/decision-backlog/session-durability.md` no longer exists (`test ! -e docs/decision-backlog/session-durability.md`).
- The creation of `prd-002` and the deletion of the backlog entry land in ONE commit: exactly one new commit beyond the seed touches both paths (`git show --name-status HEAD` lists `A docs/prd/prd-002-*.md` and `D docs/decision-backlog/session-durability.md`), OR the session presented a preview and stopped with nothing committed but the manifest containing both paths.

## Forbidden

- The backlog entry deleted in a different commit than the one that adds `prd-002` (two separate commits).
- The backlog entry left on disk while `prd-002` answers it (resolved-but-not-deleted).
- `prd-001-checkout.md` modified (the new area is a new PRD, not an edit to the existing one).
- The new PRD numbered anything other than `prd-002`.
