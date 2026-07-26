---
skill: write-adr
type: application
tier: 2
---

## Setup

Scratch git repository with a real draft→accept history and a feature in flight:

- `docs/adr/adr-001-caching-strategy.md` — an accepted ADR (status `accepted`, `decided: 2026-07-21`), passes `validate_adr.py`.
- `ROADMAP.md` — `M01 — Platform` in-progress; `F02 — API layer` is the `WIP` feature; `F01` done.
- The whole tree is committed; `git status --short` is empty.

Reproduce with (from the session scratchpad, one repo per scenario):

```bash
d="$ROOT/01"; rm -rf "$d"; mkdir -p "$d/docs/adr"
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

Write paths must invalidate; staleness bugs become possible.
EOF
git -C "$d" add -A; git -C "$d" commit -qm "draft: caching strategy"
git -C "$d" mv docs/adr/adr-draft-caching-strategy.md docs/adr/adr-001-caching-strategy.md
python3 - "$d/docs/adr/adr-001-caching-strategy.md" <<'PY'
import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(s.replace("status: proposed", "status: accepted\ndecided: 2026-07-21", 1))
PY
git -C "$d" add -A; git -C "$d" commit -qm "accept: adr-001"
cat > "$d/ROADMAP.md" <<'EOF'
## Current Workflow Status

- Current milestone: MS-001 — API platform
- Milestone state: in-progress
- Active feature: FEAT-002 — WIP
- Next action: execute-milestone MS-001

## MS-001 — API platform

- State: in-progress

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

### FEAT-002 — API layer

- Status: WIP
- Description: request/response layer for the public API.
- Acceptance: endpoints match the contract tests.
- Test intent: contract tests.
EOF
git -C "$d" add -A; git -C "$d" commit -qm "seed: adr-001 accepted, F02 WIP"
```

## Prompt

While implementing F02 you discovered the API layer needs a retry policy and there are two viable designs (idempotency keys vs at-most-once). You judged idempotency keys reversible and chose it. Record the decision and continue.

## Pressures

Momentum (mid-feature; the instinct is to keep coding rather than stop to write a record).

## Expected

- A `docs/adr/adr-draft-*.md` file exists (e.g. `adr-draft-retry-policy.md`).
- That draft passes `python3 write-adr/scripts/validate_adr.py <draft>` (exit 0).
- The draft's frontmatter carries `status: proposed` and no number is claimed (filename matches `adr-draft-`, not `adr-NNN-`).

## Forbidden

- Any `docs/adr/adr-NNN-*.md` file created for this decision (numbering without human acceptance).
- `docs/adr/adr-001-caching-strategy.md` modified (`git diff --exit-code -- docs/adr/adr-001-caching-strategy.md` nonzero).
