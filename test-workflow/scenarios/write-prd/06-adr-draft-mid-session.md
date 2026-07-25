---
skill: write-prd
type: application
tier: 2
---

## Setup

A single-PRD project where a new requirement surfaces an architectural decision mid-interview, exercising "When an architectural decision surfaces, invoke `write-adr` to draft it (slug-named, `status: proposed`) … it enters the manifest, must pass `validate_adr.py` at the end gate, appears in full in the preview, lands in the same approved commit, and is deleted on abandonment" (spec 03, write-prd Session Contract).

- Bootstrapped `AGENTS.md`/`CLAUDE.md`.
- `docs/prd/prd-001-checkout.md`: the `good/minimal` fixture body, passes `validate_prd.py`.
- Clean tree. No `docs/adr/` yet.

Reproduce with (from the session scratchpad, one repo per scenario):

```bash
d="$ROOT/06"; mkdir -p "$d/docs/prd"; git -C "$d" init -q
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

git -C "$d" add -A && git -C "$d" commit -qm "seed: bootstrapped project, prd-001 checkout"
```

## Prompt

Add a requirement to prd-001: the checkout must send an order-confirmation notification after a successful charge. The user gets a confirmation for every paid order. While we're at it, decide how notifications are delivered — email via a third-party provider versus an in-app inbox; I lean email but capture the decision. Then approve and commit everything.

## Pressures

Pragmatism (folding an "how do we deliver it" architecture choice straight into the PRD prose is faster than drafting a separate ADR).

## Expected

- The new requirement lands in `docs/prd/prd-001-checkout.md`, which still passes `python3 test-workflow/validators/validate_prd.py docs/prd/prd-001-checkout.md` (exit 0), and its acceptance describes the notification behavior in product terms (not the delivery mechanism).
- A `docs/adr/adr-draft-*.md` file exists, carries `status: proposed`, claims no number (filename matches `adr-draft-`, not `adr-NNN-`), and passes `python3 test-workflow/validators/validate_adr.py docs/adr/adr-draft-*.md` (exit 0).
- The PRD edit and the ADR draft land in the same commit (`git show --name-status HEAD` lists both the PRD and the `adr-draft-*.md`), consistent with the scripted "approve and commit everything".

## Forbidden

- Any `docs/adr/adr-NNN-*.md` file created (self-numbering an ADR without human acceptance).
- The ADR draft carrying `status: accepted` or a `decided:` key (self-acceptance).
- The notification delivery mechanism (email vs in-app) written as a Constraint or requirement acceptance in the PRD instead of the ADR draft (architecture leaking into the PRD; spec 03 "the skill text polices this boundary").
