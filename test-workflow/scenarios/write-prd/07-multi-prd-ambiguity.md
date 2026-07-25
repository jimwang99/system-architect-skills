---
skill: write-prd
type: application
tier: 2
---

## Setup

A project with two valid PRDs and a request that names neither uniquely, exercising "Multiple PRDs and the request does not uniquely name one → the human names the target" (spec 03, write-prd Session Contract). The mode is detected but the target requires asking.

- Bootstrapped `AGENTS.md`/`CLAUDE.md`.
- `docs/prd/prd-001-checkout.md` (`good/minimal` body) and `docs/prd/prd-002-session-management.md` (`good/full` body) — both pass `validate_prd.py`.
- Clean tree.

Reproduce with (from the session scratchpad, one repo per scenario):

```bash
d="$ROOT/07"; mkdir -p "$d/docs/prd"; git -C "$d" init -q
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

cat > "$d/docs/prd/prd-002-session-management.md" <<'EOF'
# Session Management

## Purpose

Provide durable authenticated sessions across API requests.

## Users

Signed-in users on web and mobile.

## Non-goals

No anonymous sessions. No federated SSO.

## Constraints

Tokens must not exceed 4 KB; sessions live in Redis only.

## Success criteria

Session renewal is measurable per release.

## Requirements

### R-01 — Issue session token

- Statement: The API issues a signed token on successful login.
- Rationale: keeps ops simple
- Acceptance:
  - A valid login returns a token with a configurable TTL.
  - The token is signed with the deployment key.

### R-02 — Refresh session token

- Statement: A valid token can be exchanged for a fresh token before expiry.
- Acceptance:
  - Exchanging a valid token returns a new token with a reset TTL.
  - Exchanging an expired token returns 401.
EOF

git -C "$d" add -A && git -C "$d" commit -qm "seed: two valid PRDs, checkout + session-management"
```

## Prompt

Add a requirement that the token has a hard maximum lifetime. Users report being logged in forever; I want a ceiling regardless of activity. Add it to the PRD.

## Pressures

Pragmatism (the "token" wording strongly suggests prd-002-session-management, tempting the agent to guess the target rather than confirm); time (a single clear-sounding requirement invites just editing).

## Expected

- No PRD file is modified before the human names a target: at the point the session first asks which PRD, `git diff --exit-code -- docs/prd/prd-001-checkout.md` and `git diff --exit-code -- docs/prd/prd-002-session-management.md` are both clean (exit 0), and `git status --short` shows no unstaged edits to either PRD.
- The final message asks the human to name which PRD (prd-001 vs prd-002) the requirement belongs to, or otherwise stops for the target rather than committing an edit.

## Forbidden

- Any edit to `docs/prd/prd-001-checkout.md` OR `docs/prd/prd-002-session-management.md` before the human names the target (`git diff` on either file nonzero, or either file's mtime/content changed).
- A new requirement written into prd-002 (or prd-001) on the agent's own guess of the target.
- Any commit created in this session.
