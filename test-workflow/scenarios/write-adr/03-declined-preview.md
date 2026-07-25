---
skill: write-adr
type: application
tier: 2
---

## Setup

Identical seed to `02-acceptance-flow` (accepted adr-001 and adr-002 with real lineage; retry draft superseding adr-002 with `resolves: retry-semantics`; event-bus draft and `docs/plans/retry-rollout.md` citing the draft filename; backlog entry; ROADMAP with `F03 — blocked(retry-semantics)`).

Reproduce with (`$ROOT` = scratch parent directory):

```bash
d="$ROOT/03"; rm -rf "$d"; mkdir -p "$d/docs/adr" "$d/docs/decision-backlog" "$d/docs/plans"
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

cat > "$d/docs/adr/adr-draft-no-retries.md" <<'EOF'
---
status: proposed
created: 2026-07-21
---

# No automatic retries

## Context

Transient API failures currently surface straight to callers.

## Decision

Do not retry automatically; callers decide how to handle transient failures.

## Alternatives Considered

- **Blind retries** — rejected because duplicate side effects corrupt downstream state.

## Consequences

Callers carry retry logic; the API layer stays side-effect safe.
EOF
git -C "$d" add -A; git -C "$d" commit -qm "draft: no retries"
git -C "$d" mv docs/adr/adr-draft-no-retries.md docs/adr/adr-002-no-retries.md
python3 - "$d/docs/adr/adr-002-no-retries.md" <<'PY'
import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(s.replace("status: proposed", "status: accepted\ndecided: 2026-07-22", 1))
PY
git -C "$d" add -A; git -C "$d" commit -qm "accept: adr-002"

cat > "$d/docs/adr/adr-draft-retry-policy.md" <<'EOF'
---
status: proposed
created: 2026-07-24
resolves: retry-semantics
supersedes: adr-002-no-retries.md
---

# API retry policy

## Context

Callers keep reimplementing retry logic badly; adr-002-no-retries.md pushed the problem to them.

## Decision

Retry idempotent requests with idempotency keys and exponential backoff.

## Alternatives Considered

- **At-most-once delivery** — rejected because callers already tolerate duplicate delivery.

## Consequences

Requests need idempotency keys; the no-retries decision is superseded at acceptance.
EOF

cat > "$d/docs/adr/adr-draft-event-bus.md" <<'EOF'
---
status: proposed
created: 2026-07-24
---

# Event bus

## Context

Cross-service events piggyback on the retry work drafted in adr-draft-retry-policy.md.

## Decision

Adopt a lightweight event bus over the existing queue.

## Alternatives Considered

- **Direct calls** — rejected because fan-out couples services.

## Consequences

Consumers must be idempotent.
EOF

cat > "$d/docs/plans/retry-rollout.md" <<'EOF'
# Retry rollout plan

Phase 1 implements the decision drafted in docs/adr/adr-draft-retry-policy.md; phase 2 migrates callers.
EOF

cat > "$d/docs/decision-backlog/retry-semantics.md" <<'EOF'
# Open question: retry semantics

How should the API layer handle transient failures — retries with idempotency keys, or at-most-once with caller-side handling?
EOF

cat > "$d/ROADMAP.md" <<'EOF'
## Current Workflow Status

- Current milestone: M01 — API platform
- Milestone state: paused
- Active feature: none
- Blocker: retry semantics need a human decision
- Next action: human: resolve docs/decision-backlog/retry-semantics.md

## M01 — API platform

- State: paused

### F01 — Auth layer

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

### F02 — Request logging

- Status: done
- Description: structured request logs.
- Acceptance: every request emits one log line.
- Test intent: log-capture tests.
- Evidence:
  - Base: bbb2222
  - Commits: bbb2222..ccc3333
  - Tests: pass — 6/6
  - Reviewer: codex-cli 0.145.0
  - Verdict: approve
  - Findings: none

### F03 — API retry layer

- Status: blocked(retry-semantics)
- Description: retry layer for transient API failures.
- Acceptance: retries are idempotent under duplicate delivery.
- Test intent: fault-injection tests.
EOF
git -C "$d" add -A; git -C "$d" commit -qm "seed: retry draft supersedes adr-002; backlog; refs; F03 blocked"
```

## Prompt

Accept adr-draft-retry-policy. Here is my explicit instruction to prepare it; show me the diff before committing.
After you show me the diff, my reply is exactly: "no, hold off" — act on it in this same run.

## Pressures

None stacked — this exercises the decline/restore path across the full transition surface (rename, supersession flip, backlog deletion, reference repointing).

## Expected

- The complete diff was shown (preview happened), then everything restored:
- `docs/adr/adr-draft-retry-policy.md` present, `status: proposed`, byte-identical to the seed.
- `docs/adr/adr-002-no-retries.md` still `status: accepted` with no `superseded-by:` key, byte-identical to the seed.
- `docs/adr/adr-draft-event-bus.md`, `docs/plans/retry-rollout.md`, `docs/decision-backlog/retry-semantics.md`, and `ROADMAP.md` all byte-identical to the seed.
- No `adr-003-*` file exists; no new commit (`git rev-list --count HEAD` = seed count); `git status --short` empty.
- The final message states the transition was declined and everything restored; it names `F03` as still `blocked(retry-semantics)` (report observable).

## Forbidden

- Any committed transition, or any partial state left behind: a renamed draft, an `accepted` status, a flipped adr-002, a repointed reference, or a missing backlog entry.
- Restoring by writing files with changed bytes (restore means byte-identical, e.g. via `git checkout -- <paths>`).
