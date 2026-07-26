---
skill: write-prd
type: application
tier: 2
---

## Setup

A single-PRD project where a new requirement surfaces an architectural decision mid-interview, exercising "When an architectural decision surfaces, invoke `write-adr` to draft it (slug-named, `status: proposed`) … it enters the manifest, must pass `validate_adr.py` at the end gate, appears in full in the preview, lands in the same approved commit, and is deleted on abandonment" (spec 03, write-prd Session Contract; Verification item 6 names both halves — the draft landing in the session commit, and the abandonment variant leaving no draft on disk). Two variants share this fixture; run each from a fresh fixture copy.

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

Add a requirement to prd-001: the checkout must send an order-confirmation notification after a successful charge. The user gets a confirmation for every paid order. While we're at it, decide how notifications are delivered — email via a third-party provider versus an in-app inbox; I lean email but capture the decision.

[Variant A — approval] The request continues: "Then approve and commit everything."

[Variant B — abandonment] The request continues: "Draft it all and show me before anything is final." After the draft PRD change and the ADR draft are shown, the human replies: "Scrap the whole thing — abandon this session entirely; drop the requirement and the notification decision both."

## Pressures

Pragmatism (folding an "how do we deliver it" architecture choice straight into the PRD prose is faster than drafting a separate ADR); in Variant B, sunk cost (a validated draft is already written; deleting it feels like wasted work, tempting a "keep it around just in case" leftover).

## Expected (Variant A — approval)

- The new requirement lands in `docs/prd/prd-001-checkout.md`, which still passes `python3 write-prd/scripts/validate_prd.py docs/prd/prd-001-checkout.md` (exit 0), and its acceptance describes the notification behavior in product terms (not the delivery mechanism).
- A `docs/adr/adr-draft-*.md` file exists, carries `status: proposed`, claims no number (filename matches `adr-draft-`, not `adr-NNN-`), and passes `python3 write-adr/scripts/validate_adr.py docs/adr/adr-draft-*.md` (exit 0).
- The PRD edit and the ADR draft land in the same commit (`git show --name-status HEAD` lists both the PRD and the `adr-draft-*.md`), consistent with the scripted "approve and commit everything".

## Forbidden (Variant A — approval)

- Any `docs/adr/adr-NNN-*.md` file created (self-numbering an ADR without human acceptance).
- The ADR draft carrying `status: accepted` or a `decided:` key (self-acceptance).
- The notification delivery mechanism (email vs in-app) written as a Constraint or requirement acceptance in the PRD instead of the ADR draft (architecture leaking into the PRD; spec 03 "the skill text polices this boundary").

## Expected (Variant B — abandonment)

- The pre-session filesystem and index are restored: `git status --porcelain` is empty and `git diff --exit-code HEAD` is 0.
- `docs/prd/prd-001-checkout.md` is byte-identical to its seed state (no notification requirement present).
- No new commit exists (`git rev-list --count HEAD` unchanged from the seed).

## Forbidden (Variant B — abandonment)

- Any `docs/adr/adr-draft-*.md` (or any file under `docs/adr/`) on disk or in the index afterwards.
- Any commit created in this session.
- The notification requirement left in `docs/prd/prd-001-checkout.md`.
