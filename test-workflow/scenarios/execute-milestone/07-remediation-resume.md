---
skill: execute-milestone
type: application
tier: 2
---

## Setup

MS-001 is `remediating` after a review that dispositioned one integration finding as `fix-feature(FEAT-002)`. MS-001 originally covered only REQ-001 (greet); FEAT-001 is `done` with full evidence. FEAT-002 was appended by the remediate step to fix the farewell integration concern. `docs/reviews/milestone-001.md` carries all six sweep sections and `- Verdict: remediate`. The test suite covers both greet (passing) and farewell (failing — not yet implemented). The skill must resume the milestone and run FEAT-002 through the fix-feature loop.

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

# MS-001 covers only REQ-001; MS-002 (planning-pending) covers REQ-002
cat > "$TARGET/ROADMAP.md" <<'EOF'
## Current Workflow Status

- Current milestone: MS-001 — Greeter
- Milestone state: planned
- Active feature: none
- Next action: execute-milestone MS-001

## MS-001 — Greeter

- State: planned
- Goal: ship greet() returning "hello".
- Covers: PRD-001 REQ-001

### FEAT-001 — Implement greet()

- Status: todo
- Description: Implement greet() in src/app.py.
- Acceptance: PRD-001 REQ-001
- Test intent: unit test asserting greet() returns "hello"

## MS-002 — Farewell

- State: planning-pending
- Goal: ship farewell() returning "bye".
- Covers: PRD-001 REQ-002
EOF

git -C "$TARGET" add -A && git -C "$TARGET" commit -qm "seed: initial state"

git -C "$TARGET" checkout -qb milestone/MS-001

# ignition: planned -> in-progress
cat > "$TARGET/ROADMAP.md" <<'EOF'
## Current Workflow Status

- Current milestone: MS-001 — Greeter
- Milestone state: in-progress
- Active feature: none
- Next action: execute-milestone MS-001

## MS-001 — Greeter

- State: in-progress
- Goal: ship greet() returning "hello".
- Covers: PRD-001 REQ-001

### FEAT-001 — Implement greet()

- Status: todo
- Description: Implement greet() in src/app.py.
- Acceptance: PRD-001 REQ-001
- Test intent: unit test asserting greet() returns "hello"

## MS-002 — Farewell

- State: planning-pending
- Goal: ship farewell() returning "bye".
- Covers: PRD-001 REQ-002
EOF

git -C "$TARGET" add ROADMAP.md && git -C "$TARGET" commit -qm "ignition: MS-001 planned -> in-progress"
IGNITION_SHA=$(git -C "$TARGET" rev-parse HEAD)

# claim: FEAT-001 todo -> WIP
cat > "$TARGET/ROADMAP.md" <<'EOF'
## Current Workflow Status

- Current milestone: MS-001 — Greeter
- Milestone state: in-progress
- Active feature: FEAT-001 — Implement greet()
- Next action: execute-milestone MS-001

## MS-001 — Greeter

- State: in-progress
- Goal: ship greet() returning "hello".
- Covers: PRD-001 REQ-001

### FEAT-001 — Implement greet()

- Status: WIP
- Description: Implement greet() in src/app.py.
- Acceptance: PRD-001 REQ-001
- Test intent: unit test asserting greet() returns "hello"

## MS-002 — Farewell

- State: planning-pending
- Goal: ship farewell() returning "bye".
- Covers: PRD-001 REQ-002
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

# impl commit (greet() already in src/app.py; tests 1/1 for greet pass — farewell import error skipped in this run)
git -C "$TARGET" commit -q --allow-empty -m "impl: greet() returns hello — tests pass 1/1"
IMPL_SHA=$(git -C "$TARGET" rev-parse HEAD)

cat > "$TARGET/docs/reviews/milestone-001-feat-001.json" <<'EOF'
{"verdict": "approve", "findings": []}
EOF

BASE_SHA="$IGNITION_SHA"
HEAD_SHA="$IMPL_SHA"

cat > "$TARGET/ROADMAP.md" <<EOF
## Current Workflow Status

- Current milestone: MS-001 — Greeter
- Milestone state: in-progress
- Active feature: none
- Next action: execute-milestone MS-001

## MS-001 — Greeter

- State: in-progress
- Goal: ship greet() returning "hello".
- Covers: PRD-001 REQ-001

### FEAT-001 — Implement greet()

- Status: done
- Description: Implement greet() in src/app.py.
- Acceptance: PRD-001 REQ-001
- Test intent: unit test asserting greet() returns "hello"
- Evidence:
  - Base: ${BASE_SHA}
  - Commits: ${BASE_SHA}..${HEAD_SHA}
  - Tests: pass — 1/1
  - Reviewer: workflow-review stub
  - Verdict: approve
  - Findings: none

## MS-002 — Farewell

- State: planning-pending
- Goal: ship farewell() returning "bye".
- Covers: PRD-001 REQ-002
EOF

git -C "$TARGET" add ROADMAP.md docs/reviews/milestone-001-feat-001.json
git -C "$TARGET" commit -qm "metadata: FEAT-001 WIP -> done, evidence"

# review-ready commit — FEAT-001 is the only feature; MS-001 review-ready is valid
cat > "$TARGET/ROADMAP.md" <<EOF
## Current Workflow Status

- Current milestone: MS-001 — Greeter
- Milestone state: review-ready
- Active feature: none
- Next action: review-milestone MS-001

## MS-001 — Greeter

- State: review-ready
- Goal: ship greet() returning "hello".
- Covers: PRD-001 REQ-001

### FEAT-001 — Implement greet()

- Status: done
- Description: Implement greet() in src/app.py.
- Acceptance: PRD-001 REQ-001
- Test intent: unit test asserting greet() returns "hello"
- Evidence:
  - Base: ${BASE_SHA}
  - Commits: ${BASE_SHA}..${HEAD_SHA}
  - Tests: pass — 1/1
  - Reviewer: workflow-review stub
  - Verdict: approve
  - Findings: none

## MS-002 — Farewell

- State: planning-pending
- Goal: ship farewell() returning "bye".
- Covers: PRD-001 REQ-002
EOF

git -C "$TARGET" add ROADMAP.md && git -C "$TARGET" commit -qm "review-ready: MS-001 in-progress -> review-ready"

# Review record: all 6 sweeps, integration finding -> remediate
cat > "$TARGET/docs/reviews/milestone-001.md" <<'EOF'
# Review: MS-001 — Greeter

## Sweep: learnings

- Disposition: no ALI drafts linked to this milestone.

## Sweep: adr-audit

- Disposition: no draft ADRs created during execution.

## Sweep: backlog-triage

- Disposition: no open backlog entries scoped to this milestone.

## Sweep: integration-review

- F1: test_app.py imports farewell() which is absent from src/app.py; the test suite fails at import time.
- Disposition: fix-feature(FEAT-002)

## Sweep: three-c

- Disposition: completeness — FEAT-001 done with evidence; farewell integration deferred to FEAT-002. Correctness and coherence verified for FEAT-001.

## Sweep: demo

- Disposition: demo pass — greet() returns "hello", pass.

## Verdict

- Verdict: remediate
- Date: 2026-07-26
EOF

git -C "$TARGET" add docs/reviews/milestone-001.md && git -C "$TARGET" commit -qm "review: all sweeps complete, verdict remediate"

# Append fix feature to MS-001 and transition to remediating
cat > "$TARGET/ROADMAP.md" <<EOF
## Current Workflow Status

- Current milestone: MS-001 — Greeter
- Milestone state: remediating
- Active feature: none
- Next action: execute-milestone MS-001

## MS-001 — Greeter

- State: remediating
- Goal: ship greet() returning "hello".
- Covers: PRD-001 REQ-001

### FEAT-001 — Implement greet()

- Status: done
- Description: Implement greet() in src/app.py.
- Acceptance: PRD-001 REQ-001
- Test intent: unit test asserting greet() returns "hello"
- Evidence:
  - Base: ${BASE_SHA}
  - Commits: ${BASE_SHA}..${HEAD_SHA}
  - Tests: pass — 1/1
  - Reviewer: workflow-review stub
  - Verdict: approve
  - Findings: none

### FEAT-002 — Fix: implement farewell()

- Status: todo
- Description: Implement farewell() in src/app.py returning "bye"; fixes test-suite import failure found in integration sweep.
- Acceptance: PRD-001 REQ-002
- Test intent: unit test asserting farewell() returns "bye"

## MS-002 — Farewell

- State: planning-pending
- Goal: ship farewell() returning "bye".
- Covers: PRD-001 REQ-002
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
- Both `python3 $TOOLS/validate_roadmap.py ROADMAP.md` and `python3 $TOOLS/check_coverage.py ROADMAP.md` exit 0 on every transition commit on `milestone/MS-001` (walk the branch, check each).

## Forbidden

- Refusal or stop on eligibility grounds (`remediating` is not in the eligible-state list pre-fix).
- Any `planned → in-progress` ignition commit (re-ignition is forbidden; the milestone was already ignited).
- Any second review pass appended to `docs/reviews/milestone-001.md` by this skill.
- Any commit to `main`.
- Transition commit where ROADMAP fails either validator.
