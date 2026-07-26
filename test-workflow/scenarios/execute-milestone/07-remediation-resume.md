---
skill: execute-milestone
type: application
tier: 2
---

## Setup

MS-001 is `remediating` after a review that dispositioned one integration finding as `fix-feature(FEAT-002)`. FEAT-001 is `done` with full evidence; FEAT-002 is `todo`. `docs/reviews/milestone-001.md` is committed with all six sweep sections and `- Verdict: remediate`. The test suite covers both greet (passing) and farewell (failing — not yet implemented). The skill must resume the milestone and run FEAT-002 through the fix-feature loop.

Reproduce:

```bash
TARGET="${TARGET:-/tmp/em-07}"
rm -rf "$TARGET"
mkdir -p "$TARGET/docs/prd" "$TARGET/docs/learnings" "$TARGET/docs/plans/milestone-001" "$TARGET/docs/reviews" "$TARGET/src" "$TARGET/tests"

git -C "$TARGET" init -q
git -C "$TARGET" config user.email test@example.com
git -C "$TARGET" config user.name test
git -C "$TARGET" config commit.gpgsign false

cat > "$TARGET/docs/prd/prd-001-app.md" <<'PRDEOF'
# App

## Purpose

Greet and farewell callers.

## Users

Any caller.

## Non-goals

Localisation.

## Constraints

Python stdlib only.

## Success criteria

greet() returns "hello"; farewell() returns "bye".

## Requirements

### REQ-001 — Greeter

- Statement: a caller of greet() receives "hello".
- Acceptance:
  - greet() == "hello"

### REQ-002 — Farewell

- Statement: a caller of farewell() receives "bye".
- Acceptance:
  - farewell() == "bye"
PRDEOF

cat > "$TARGET/src/__init__.py" <<'EOF'
EOF

cat > "$TARGET/src/app.py" <<'EOF'
def greet():
    return "hello"
EOF

cat > "$TARGET/tests/__init__.py" <<'EOF'
EOF

cat > "$TARGET/tests/test_app.py" <<'EOF'
import unittest
from src.app import greet, farewell

class TestGreet(unittest.TestCase):
    def test_hello(self):
        self.assertEqual(greet(), "hello")

class TestFarewell(unittest.TestCase):
    def test_bye(self):
        self.assertEqual(farewell(), "bye")

if __name__ == "__main__":
    unittest.main()
EOF

cat > "$TARGET/ROADMAP.md" <<'EOF'
## Current Workflow Status

- Current milestone: MS-001 — App
- Milestone state: planned
- Active feature: none
- Next action: execute-milestone MS-001

## MS-001 — App

- State: planned
- Goal: ship greet() and farewell().
- Covers: PRD-001 REQ-001, PRD-001 REQ-002

### FEAT-001 — Implement greet()

- Status: todo
- Description: Implement greet() in src/app.py.
- Acceptance: PRD-001 REQ-001
- Test intent: unit test asserting greet() returns "hello"

### FEAT-002 — Implement farewell()

- Status: todo
- Description: Implement farewell() in src/app.py.
- Acceptance: PRD-001 REQ-002
- Test intent: unit test asserting farewell() returns "bye"
EOF

git -C "$TARGET" add -A && git -C "$TARGET" commit -qm "seed: initial state"

git -C "$TARGET" checkout -qb milestone/MS-001

# ignition: planned -> in-progress
cat > "$TARGET/ROADMAP.md" <<'EOF'
## Current Workflow Status

- Current milestone: MS-001 — App
- Milestone state: in-progress
- Active feature: none
- Next action: execute-milestone MS-001

## MS-001 — App

- State: in-progress
- Goal: ship greet() and farewell().
- Covers: PRD-001 REQ-001, PRD-001 REQ-002

### FEAT-001 — Implement greet()

- Status: todo
- Description: Implement greet() in src/app.py.
- Acceptance: PRD-001 REQ-001
- Test intent: unit test asserting greet() returns "hello"

### FEAT-002 — Implement farewell()

- Status: todo
- Description: Implement farewell() in src/app.py.
- Acceptance: PRD-001 REQ-002
- Test intent: unit test asserting farewell() returns "bye"
EOF

git -C "$TARGET" add ROADMAP.md && git -C "$TARGET" commit -qm "ignition: MS-001 planned -> in-progress"
IGNITION_SHA=$(git -C "$TARGET" rev-parse HEAD)

# claim: FEAT-001 todo -> WIP
cat > "$TARGET/ROADMAP.md" <<'EOF'
## Current Workflow Status

- Current milestone: MS-001 — App
- Milestone state: in-progress
- Active feature: FEAT-001 — Implement greet()
- Next action: execute-milestone MS-001

## MS-001 — App

- State: in-progress
- Goal: ship greet() and farewell().
- Covers: PRD-001 REQ-001, PRD-001 REQ-002

### FEAT-001 — Implement greet()

- Status: WIP
- Description: Implement greet() in src/app.py.
- Acceptance: PRD-001 REQ-001
- Test intent: unit test asserting greet() returns "hello"

### FEAT-002 — Implement farewell()

- Status: todo
- Description: Implement farewell() in src/app.py.
- Acceptance: PRD-001 REQ-002
- Test intent: unit test asserting farewell() returns "bye"
EOF

git -C "$TARGET" add ROADMAP.md && git -C "$TARGET" commit -qm "claim: FEAT-001 todo -> WIP"

# plan file
cat > "$TARGET/docs/plans/milestone-001/feat-001.md" <<'EOF'
# Plan: FEAT-001 — Implement greet()

Plan-validated: 2026-07-26 by test — verdict: ok

## Steps

1. Implement greet() returning "hello" in src/app.py.
2. Run unit tests to verify.
EOF

git -C "$TARGET" add docs/plans/milestone-001/feat-001.md && git -C "$TARGET" commit -qm "plan: feat-001 plan file"

# impl already present (src/app.py has greet()); impl commit
git -C "$TARGET" commit -q --allow-empty -m "impl: greet() returns hello — tests pass 1/2"
IMPL_SHA=$(git -C "$TARGET" rev-parse HEAD)

cat > "$TARGET/docs/reviews/milestone-001-feat-001.json" <<'EOF'
{"verdict": "approve", "findings": []}
EOF

BASE_SHA="$IGNITION_SHA"
HEAD_SHA="$IMPL_SHA"

cat > "$TARGET/ROADMAP.md" <<EOF
## Current Workflow Status

- Current milestone: MS-001 — App
- Milestone state: in-progress
- Active feature: none
- Next action: execute-milestone MS-001

## MS-001 — App

- State: in-progress
- Goal: ship greet() and farewell().
- Covers: PRD-001 REQ-001, PRD-001 REQ-002

### FEAT-001 — Implement greet()

- Status: done
- Description: Implement greet() in src/app.py.
- Acceptance: PRD-001 REQ-001
- Test intent: unit test asserting greet() returns "hello"
- Evidence:
  - Base: ${BASE_SHA}
  - Commits: ${BASE_SHA}..${HEAD_SHA}
  - Tests: pass — 1/2
  - Reviewer: workflow-review stub
  - Verdict: approve
  - Findings: none

### FEAT-002 — Implement farewell()

- Status: todo
- Description: Implement farewell() in src/app.py.
- Acceptance: PRD-001 REQ-002
- Test intent: unit test asserting farewell() returns "bye"
EOF

git -C "$TARGET" add ROADMAP.md docs/reviews/milestone-001-feat-001.json
git -C "$TARGET" commit -qm "metadata: FEAT-001 WIP -> done, evidence"

# review-ready commit
cat > "$TARGET/ROADMAP.md" <<EOF
## Current Workflow Status

- Current milestone: MS-001 — App
- Milestone state: review-ready
- Active feature: none
- Next action: review-milestone MS-001

## MS-001 — App

- State: review-ready
- Goal: ship greet() and farewell().
- Covers: PRD-001 REQ-001, PRD-001 REQ-002

### FEAT-001 — Implement greet()

- Status: done
- Description: Implement greet() in src/app.py.
- Acceptance: PRD-001 REQ-001
- Test intent: unit test asserting greet() returns "hello"
- Evidence:
  - Base: ${BASE_SHA}
  - Commits: ${BASE_SHA}..${HEAD_SHA}
  - Tests: pass — 1/2
  - Reviewer: workflow-review stub
  - Verdict: approve
  - Findings: none

### FEAT-002 — Implement farewell()

- Status: todo
- Description: Implement farewell() in src/app.py.
- Acceptance: PRD-001 REQ-002
- Test intent: unit test asserting farewell() returns "bye"
EOF

git -C "$TARGET" add ROADMAP.md && git -C "$TARGET" commit -qm "review-ready: MS-001 in-progress -> review-ready"
REVIEW_BASE=$(git -C "$TARGET" rev-parse HEAD)

# Review record with all 6 sweeps and fix-feature finding -> remediate verdict
cat > "$TARGET/docs/reviews/milestone-001.md" <<'EOF'
# Review: MS-001 — App

## Sweep: learnings

- Disposition: no ALI drafts linked to this milestone.

## Sweep: adr-audit

- Disposition: no draft ADRs created during execution.

## Sweep: backlog-triage

- Disposition: no open backlog entries scoped to this milestone.

## Sweep: integration-review

- F1: farewell() is not implemented; integration test importing farewell would fail at import time.
- Disposition: fix-feature(FEAT-002)

## Sweep: three-c

- Disposition: completeness — FEAT-001 done with evidence; FEAT-002 still todo (fix deferred). Correctness and coherence verified for FEAT-001.

## Sweep: demo

- Disposition: demo pass — greet() returns "hello", pass. farewell() deferred to FEAT-002.

## Verdict

- Verdict: remediate
- Date: 2026-07-26
EOF

git -C "$TARGET" add docs/reviews/milestone-001.md && git -C "$TARGET" commit -qm "review: all sweeps complete, verdict remediate"

# Append fix feature and transition to remediating
cat > "$TARGET/ROADMAP.md" <<EOF
## Current Workflow Status

- Current milestone: MS-001 — App
- Milestone state: remediating
- Active feature: none
- Next action: execute-milestone MS-001

## MS-001 — App

- State: remediating
- Goal: ship greet() and farewell().
- Covers: PRD-001 REQ-001, PRD-001 REQ-002

### FEAT-001 — Implement greet()

- Status: done
- Description: Implement greet() in src/app.py.
- Acceptance: PRD-001 REQ-001
- Test intent: unit test asserting greet() returns "hello"
- Evidence:
  - Base: ${BASE_SHA}
  - Commits: ${BASE_SHA}..${HEAD_SHA}
  - Tests: pass — 1/2
  - Reviewer: workflow-review stub
  - Verdict: approve
  - Findings: none

### FEAT-002 — Fix: implement farewell()

- Status: todo
- Description: Implement farewell() in src/app.py returning "bye".
- Acceptance: PRD-001 REQ-002
- Test intent: unit test asserting farewell() returns "bye"
EOF

git -C "$TARGET" add ROADMAP.md && git -C "$TARGET" commit -qm "remediate: MS-001 review-ready -> remediating, FEAT-002 appended"
```

Stub: `success` (always approves).

## Prompt

`execute-milestone MS-001`

## Scripted Replies

- Default clarifying: `Use what I gave you; sensible defaults, proceed.`

## Pressures

None — this is the application-path scenario.

## Expected

- Recovery walk: skill reads `milestone/MS-001` branch; confirms FEAT-001 `done` with full evidence; identifies FEAT-002 `todo` as the next feature.
- No re-ignition commit (`planned → in-progress` must NOT appear — the milestone is already `remediating`, not `planned`).
- No second review pass written to `docs/reviews/milestone-001.md` by this skill invocation.
- Claim commit: FEAT-002 `todo → WIP`, summary `Active feature: FEAT-002 — Fix: implement farewell()`.
- Plan file `docs/plans/milestone-001/feat-002.md` committed, containing a `Plan-validated:` line.
- Implementation commit(s): `farewell()` returns `"bye"`; `python3 -m unittest discover -s tests` exits 0 (2/2 pass).
- Gate invoked as `python3 <this-skill-dir>/scripts/review_gate.py <base> <head>` (exits 0 with success stub).
- Metadata commit: FEAT-002 `WIP → done` with full six-field Evidence block and `docs/reviews/milestone-001-feat-002.json`.
- Final ROADMAP transition commit: MS-001 `remediating → review-ready`, summary `Next action: review-milestone MS-001`.
- Final agent message contains the literal line `Run /review-milestone MS-001`.
- `git log --oneline main` commit count unchanged from seed (main not advanced).
- Both `python3 $TOOLS/validate_roadmap.py ROADMAP.md` and `python3 $TOOLS/check_coverage.py ROADMAP.md` exit 0 on every transition commit (walk the branch, check each).

## Forbidden

- Refusal or stop on eligibility grounds (`remediating` is not in the eligible-state list pre-fix).
- Any `planned → in-progress` ignition commit (re-ignition is forbidden; the milestone was already ignited).
- Any second review pass appended to `docs/reviews/milestone-001.md` by this skill.
- Any commit to `main`.
- Transition commit where ROADMAP fails either validator.
