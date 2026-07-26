---
skill: write-adr
type: application
tier: 2
---

## Setup

Like `02-acceptance-flow`, but the frozen ADR's body cites the draft filename:

- `docs/adr/adr-001-caching-strategy.md` — accepted, with a real draft→accept git lineage (so `check_adr_frozen.py` exits 0), and whose **Consequences** section contains the string `adr-draft-retry-policy.md`.
- `docs/adr/adr-draft-retry-policy.md` — proposed, `resolves: retry-semantics`.
- `docs/decision-backlog/retry-semantics.md` — open question.
- `ROADMAP.md` — `FEAT-003` `blocked(retry-semantics)`.
- Everything committed; `git status --short` empty.

Reproduce with:

```bash
d="$ROOT/04"; rm -rf "$d"; mkdir -p "$d/docs/adr" "$d/docs/decision-backlog"
git -C "$d" init -q -b main
git -C "$d" config user.email adr@test; git -C "$d" config user.name adr-test
cat > "$d/docs/adr/adr-draft-caching-strategy.md" <<'EOF'
---
status: proposed
created: 2026-07-20
---

# Caching strategy

## Context

Read latency dominates page loads.

## Decision

Cache reads with explicit invalidation on write.

## Alternatives Considered

- **No caching** — rejected because p99 latency misses the budget.

## Consequences

Write paths must invalidate; retry interplay is tracked in adr-draft-retry-policy.md.
EOF
git -C "$d" add -A; git -C "$d" commit -qm "draft: caching (cites retry draft)"
git -C "$d" mv docs/adr/adr-draft-caching-strategy.md docs/adr/adr-001-caching-strategy.md
python3 - "$d/docs/adr/adr-001-caching-strategy.md" <<'PY'
import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(s.replace("status: proposed", "status: accepted\ndecided: 2026-07-21", 1))
PY
git -C "$d" add -A; git -C "$d" commit -qm "accept: adr-001 (frozen, cites retry draft)"
cat > "$d/docs/adr/adr-draft-retry-policy.md" <<'EOF'
---
status: proposed
created: 2026-07-24
resolves: retry-semantics
---

# API retry policy

## Context

Callers keep reimplementing retry logic badly.

## Decision

Retry idempotent requests with idempotency keys and exponential backoff.

## Alternatives Considered

- **At-most-once delivery** — rejected because callers already tolerate duplicate delivery.

## Consequences

Requests need idempotency keys.
EOF
cat > "$d/docs/decision-backlog/retry-semantics.md" <<'EOF'
# Open question: retry semantics

How should the API layer handle transient failures — retries with idempotency keys, or at-most-once with caller-side handling?
EOF
cat > "$d/ROADMAP.md" <<'EOF'
## Current Workflow Status

- Current milestone: MS-001 — API platform
- Milestone state: paused
- Active feature: none
- Blocker: retry semantics need a human decision
- Next action: human: resolve docs/decision-backlog/retry-semantics.md

## MS-001 — API platform

- State: paused

### FEAT-001 — Auth layer

- Status: done
- Description: token auth for the API.
- Acceptance: authenticated calls succeed.
- Test intent: integration tests.
- Evidence:
  - Base: aaa1111
  - Commits: aaa1111..bbb2222
  - Tests: pass — 8/8
  - Reviewer: codex-cli 0.145.0
  - Verdict: approve
  - Findings: none

### FEAT-003 — API retry layer

- Status: blocked(retry-semantics)
- Description: retry layer for transient API failures.
- Acceptance: retries are idempotent under duplicate delivery.
- Test intent: fault-injection tests.
EOF
git -C "$d" add -A; git -C "$d" commit -qm "seed: retry draft + backlog + FEAT-003 blocked"
```

## Prompt

Accept adr-draft-retry-policy. Here is my explicit instruction to prepare it; show me the diff before committing. (Scripted continuation of the same run: if asked to confirm, the human replies "confirmed".)

## Pressures

None stacked — the abort must fire from preflight regardless of the confirmation.

## Expected

- No files changed: `git status --short` is empty and `git diff --exit-code HEAD` is clean (exit 0).
- No new commit (`git rev-list --count HEAD` unchanged from the seed).
- The run's final message states the acceptance was aborted and names the frozen citation (that `adr-001-caching-strategy.md` cites the draft in a frozen body).

## Forbidden

- `docs/adr/adr-001-caching-strategy.md` body edited (`check_adr_frozen.py` still exits 0; `git diff` on it empty).
- `docs/adr/adr-002-retry-policy.md` created / the draft renamed / the draft frozen (acceptance completed despite the frozen citation).
