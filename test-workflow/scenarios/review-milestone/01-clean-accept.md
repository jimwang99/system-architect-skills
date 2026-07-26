---
skill: review-milestone
type: application
tier: 2
---

## Setup

MS-001 is `review-ready` on `milestone/MS-001`. FEAT-001 is `done` with a full six-field Evidence block. ALI-001 is a draft learning file. All validators pass on the branch. The stub reviewer always approves. The happy-path walks the agent through the full sweep (learnings → adr-audit → backlog-triage → integration-review → three-c → demo), writes the verdict, merges the branch, and updates main.

Reproduce:

```bash
TARGET="${TARGET:-/tmp/rm-01}"
rm -rf "$TARGET"
mkdir -p "$TARGET/docs/prd" "$TARGET/docs/learnings" "$TARGET/docs/plans/milestone-001" "$TARGET/docs/reviews" "$TARGET/src" "$TARGET/tests"

git -C "$TARGET" init -q
git -C "$TARGET" config user.email test@example.com
git -C "$TARGET" config user.name test
git -C "$TARGET" config commit.gpgsign false

cat > "$TARGET/docs/prd/prd-001-app.md" <<'PRDEOF'
# App

## Purpose

Greet callers.

## Users

Any caller.

## Non-goals

Localisation.

## Constraints

Python stdlib only.

## Success criteria

greet() returns "hello".

## Requirements

### REQ-001 — Greeter

- Statement: a caller of greet() receives "hello".
- Acceptance:
  - greet() == "hello"

### REQ-002 — Farewell

- Statement: a caller of farewell() receives "goodbye".
- Acceptance:
  - farewell() == "goodbye"
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
from src.app import greet

class TestGreet(unittest.TestCase):
    def test_hello(self):
        self.assertEqual(greet(), "hello")

if __name__ == "__main__":
    unittest.main()
EOF

cat > "$TARGET/ROADMAP.md" <<'EOF'
## Current Workflow Status

- Current milestone: MS-001 — Greeter
- Milestone state: planned
- Active feature: none
- Next action: execute-milestone MS-001

## MS-001 — Greeter

- State: planned
- Goal: ship a greet() function that returns "hello".
- Covers: PRD-001 REQ-001

### FEAT-001 — Implement greet()

- Status: todo
- Description: Implement greet() in src/app.py.
- Acceptance: PRD-001 REQ-001
- Test intent: unit test asserting greet() returns "hello"

## MS-002 — Farewell

- State: planning-pending
- Goal: ship a farewell() function that returns "goodbye".
- Covers: PRD-001 REQ-002
EOF

git -C "$TARGET" add -A && git -C "$TARGET" commit -qm "seed: initial state"

# Create milestone branch
git -C "$TARGET" checkout -qb milestone/MS-001

# Ignition commit
cat > "$TARGET/ROADMAP.md" <<'EOF'
## Current Workflow Status

- Current milestone: MS-001 — Greeter
- Milestone state: in-progress
- Active feature: none
- Next action: execute-milestone MS-001

## MS-001 — Greeter

- State: in-progress
- Goal: ship a greet() function that returns "hello".
- Covers: PRD-001 REQ-001

### FEAT-001 — Implement greet()

- Status: todo
- Description: Implement greet() in src/app.py.
- Acceptance: PRD-001 REQ-001
- Test intent: unit test asserting greet() returns "hello"

## MS-002 — Farewell

- State: planning-pending
- Goal: ship a farewell() function that returns "goodbye".
- Covers: PRD-001 REQ-002
EOF

git -C "$TARGET" add ROADMAP.md && git -C "$TARGET" commit -qm "ignition: MS-001 planned -> in-progress"
IGNITION_SHA=$(git -C "$TARGET" rev-parse HEAD)

# Claim commit
cat > "$TARGET/ROADMAP.md" <<'EOF'
## Current Workflow Status

- Current milestone: MS-001 — Greeter
- Milestone state: in-progress
- Active feature: FEAT-001 — Implement greet()
- Next action: execute-milestone MS-001

## MS-001 — Greeter

- State: in-progress
- Goal: ship a greet() function that returns "hello".
- Covers: PRD-001 REQ-001

### FEAT-001 — Implement greet()

- Status: WIP
- Description: Implement greet() in src/app.py.
- Acceptance: PRD-001 REQ-001
- Test intent: unit test asserting greet() returns "hello"

## MS-002 — Farewell

- State: planning-pending
- Goal: ship a farewell() function that returns "goodbye".
- Covers: PRD-001 REQ-002
EOF

git -C "$TARGET" add ROADMAP.md && git -C "$TARGET" commit -qm "claim: FEAT-001 todo -> WIP"

# Plan commit
cat > "$TARGET/docs/plans/milestone-001/feat-001.md" <<'EOF'
# Plan: FEAT-001 — Implement greet()

Plan-validated: 2026-07-26 by test — verdict: ok

## Steps

1. Implement greet() returning "hello" in src/app.py.
2. Run unit tests to verify.
EOF

git -C "$TARGET" add docs/plans/milestone-001/feat-001.md && git -C "$TARGET" commit -qm "plan: feat-001 plan file"

# Impl commit (greet() already in src/app.py from seed — no change needed, but re-commit to record the impl step)
git -C "$TARGET" commit -q --allow-empty -m "impl: greet() returns hello — tests pass 1/1"
IMPL_SHA=$(git -C "$TARGET" rev-parse HEAD)

# Add ALI-001 draft
cat > "$TARGET/docs/learnings/ALI-001.md" <<'EOF'
# ALI-001: Test infrastructure gap
Date: 2026-07-26
Phase: implementation
Status: draft

**What happened:** Discovered the test runner needed explicit module path configuration.

## L1: Module path not set
- **What we assumed:** Python discovers src/ automatically.
- **What is actually true:** Must run `python3 -m unittest discover -s tests` from the repo root.
- **Evidence:** Test run output: `ModuleNotFoundError: No module named 'src'` when running from tests/.
- **Why the assumption was wrong:** Default discovery does not add parent to sys.path.
- **Class of error:** Environment configuration
- **Improvement items:**
  - **P1 — AI agent skill:** `execute-milestone/SKILL.md` — document the exact test invocation form.
EOF

# Add review JSON
cat > "$TARGET/docs/reviews/milestone-001-feat-001.json" <<'EOF'
{"verdict": "approve", "findings": []}
EOF

# Metadata commit: Evidence block, flip FEAT-001 done
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
- Goal: ship a greet() function that returns "hello".
- Covers: PRD-001 REQ-001

### FEAT-001 — Implement greet()

- Status: done
- Description: Implement greet() in src/app.py.
- Acceptance: PRD-001 REQ-001
- Test intent: unit test asserting greet() returns "hello"
- Learning: docs/learnings/ALI-001.md
- Evidence:
  - Base: ${BASE_SHA}
  - Commits: ${BASE_SHA}..${HEAD_SHA}
  - Tests: pass — 1/1
  - Reviewer: workflow-review stub
  - Verdict: approve
  - Findings: none

## MS-002 — Farewell

- State: planning-pending
- Goal: ship a farewell() function that returns "goodbye".
- Covers: PRD-001 REQ-002
EOF

git -C "$TARGET" add ROADMAP.md docs/learnings/ALI-001.md docs/reviews/milestone-001-feat-001.json
git -C "$TARGET" commit -qm "metadata: FEAT-001 WIP -> done, evidence, ALI-001 draft"

# Review-ready commit
cat > "$TARGET/ROADMAP.md" <<EOF
## Current Workflow Status

- Current milestone: MS-001 — Greeter
- Milestone state: review-ready
- Active feature: none
- Next action: review-milestone MS-001

## MS-001 — Greeter

- State: review-ready
- Goal: ship a greet() function that returns "hello".
- Covers: PRD-001 REQ-001

### FEAT-001 — Implement greet()

- Status: done
- Description: Implement greet() in src/app.py.
- Acceptance: PRD-001 REQ-001
- Test intent: unit test asserting greet() returns "hello"
- Learning: docs/learnings/ALI-001.md
- Evidence:
  - Base: ${BASE_SHA}
  - Commits: ${BASE_SHA}..${HEAD_SHA}
  - Tests: pass — 1/1
  - Reviewer: workflow-review stub
  - Verdict: approve
  - Findings: none

## MS-002 — Farewell

- State: planning-pending
- Goal: ship a farewell() function that returns "goodbye".
- Covers: PRD-001 REQ-002
EOF

git -C "$TARGET" add ROADMAP.md && git -C "$TARGET" commit -qm "review-ready: MS-001 in-progress -> review-ready"
```

Stub: `success`

## Prompt

`review-milestone MS-001`

## Scripted Replies

- When agent asks about learning files / ALI-001: `Approve ALI-001.`
- When agent asks about draft ADRs: `No draft ADRs.`
- When agent asks about open backlog entries: `No open backlog entries.`
- When agent asks about three-c (completeness, correctness, coherence): `All complete, correct, coherent.`
- When agent asks for / about the demo: `Demo done — greet() returns "hello", pass.`
- When agent presents the accept verdict for confirmation: `Accept.`
- When agent asks about next milestone decomposition: `Defer decomposition.`
- Default clarifying: `Use what I gave you; sensible defaults, proceed.`

## Expected

- Record file `docs/reviews/milestone-001.md` exists on `milestone/MS-001` and passes `validate_review.py` at final state (exit 0).
- Record has all six sweep sections in order: learnings, adr-audit, backlog-triage, integration-review, three-c, demo.
- `git log -p` on the record file proves the Verdict section was added in the final (or same) commit as the last sweep section — never before any sweep section.
- `milestone/MS-001` merged --no-ff to `main` (merge commit present in `git log --oneline main`).
- `main` ROADMAP has MS-001 `State: accepted` and `Next action: milestone-to-features MS-002` (or similar naming MS-002).
- MS-002 stays `State: planning-pending` — no decomposition occurred.
- ALI-001 has `Status: approved` on `main` and passes `validate_learning.py` (exit 0).
- `validate_roadmap.py` and `check_coverage.py` both exit 0 on the accepted-state ROADMAP on main.

## Forbidden

- `## Verdict` section written to the record file before all six `## Sweep:` sections appear in the file's git history.
- Merge commit absent from `git log --oneline main`.
- ALI-001 `Status:` still `draft` on main after the accept.
- MS-002 state changed from `planning-pending`.
- `validate_review.py` exit non-zero on the final record.
