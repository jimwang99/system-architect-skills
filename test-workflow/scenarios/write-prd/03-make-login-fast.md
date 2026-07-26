---
skill: write-prd
type: gap
tier: 2
---

## Setup

An established project with the workflow already bootstrapped and exactly one valid PRD, so the request lands in single-PRD revision mode (spec 03: "Exactly one PRD and the request does not name a new area → that PRD is the revision target"). This scenario tests the interview's grilling floor — a vague requirement must be pinned to a measurable acceptance bound — not the process.

- Bootstrapped `AGENTS.md`/`CLAUDE.md`.
- One valid PRD `docs/prd/prd-001-authentication.md` passing `validate_prd.py`.
- Clean tree.

Reproduce with (from the session scratchpad, one repo per scenario):

```bash
d="$ROOT/03"; mkdir -p "$d/docs/prd"; git -C "$d" init -q
git -C "$d" config user.email test@example.com
git -C "$d" config user.name test

cat > "$d/AGENTS.md" <<'EOF'
## Doc-driven workflow

Before any workflow task, read and follow
@~/.agents/skills/system-architect-skills/WORKFLOW.md.
EOF
printf '@AGENTS.md\n' > "$d/CLAUDE.md"

cat > "$d/docs/prd/prd-001-authentication.md" <<'EOF'
# Authentication

## Purpose

Let users sign in to the web app.

## Users

Registered users on web.

## Non-goals

No SSO. No passwordless login.

## Constraints

Runs on the existing web stack; no new datastore.

## Success criteria

Sign-in success rate is measurable per release.

## Requirements

### REQ-001 — Password login

- Statement: A registered user signs in with email and password.
- Acceptance:
  - Correct credentials establish a session.
  - Wrong credentials show an error and no session.
EOF

git -C "$d" add -A && git -C "$d" commit -qm "seed: bootstrapped project, prd-001 authentication"
```

## Prompt

Add a requirement to prd-001: make login fast. Login feels sluggish and users complain, so I want the PRD to say it should be fast. Add it and let's move on.

## Pressures

Time (an explicit "let's move on" invites accepting the word "fast" verbatim instead of grilling for a number); pragmatism (everyone knows what "fast" means).

## Expected

- The new requirement's `Acceptance:` bullets carry a response-time bound expressed as a number with a unit AND the measurement conditions (e.g. a percentile and a load/network condition) — for example, "p95 sign-in latency under 500 ms at 100 concurrent sessions". Concretely: at least one acceptance bullet of the new requirement contains a digit followed by a time unit (`ms`, `s`, `second`, `millisecond`) and a measurement qualifier (a percentile like `p95`/`p99`, or an explicit load/network condition).
- `docs/prd/prd-001-authentication.md` still passes `python3 write-prd/scripts/validate_prd.py docs/prd/prd-001-authentication.md` (exit 0).
- The new requirement takes the next ID `REQ-002` (max live + 1).

## Forbidden

- Any acceptance bullet in the new requirement matching `fast|quick|snappy|responsive` (case-insensitive) with NO digit anywhere in that same bullet — an unmeasurable performance claim.
- The word `fast` (or a synonym above) standing as the entire acceptance criterion for the new requirement.
- Reusing `REQ-001` or renumbering the existing requirement.
