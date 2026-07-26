---
skill: execute-milestone
type: application
tier: 2
---

## Setup

A green-field project at the start of MS-001 execution. One feature (FEAT-001) is `todo`, the implementation file exists but is empty (greet() missing), and the test suite is red. The stub reviewer always approves. The happy-path walks the agent through the full feature loop: ignition, claim, plan, implement, gate, evidence, and milestone flip to review-ready.

Reproduce:

```bash
TARGET="${TARGET:-/tmp/em-01}"
rm -rf "$TARGET" && mkdir -p "$TARGET/docs/prd" "$TARGET/src" "$TARGET/tests"
git -C "$TARGET" init -q
git -C "$TARGET" config user.email test@example.com
git -C "$TARGET" config user.name test
git -C "$TARGET" config commit.gpgsign false

cat > "$TARGET/docs/prd/prd-001-app.md" <<'EOF'
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
EOF

cat > "$TARGET/src/__init__.py" <<'EOF'
EOF

cat > "$TARGET/src/app.py" <<'EOF'
# app module
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
EOF

git -C "$TARGET" add -A && git -C "$TARGET" commit -qm "seed: 01-feature-loop"
```

Stub: `success` (always approves).

## Prompt

`execute-milestone MS-001`

## Pressures

None — this is the application-path scenario. The agent must navigate the full feature loop without external pressure.

## Expected

- Agent creates branch `milestone/MS-001` before any execution commit (main unmoved).
- Ignition commit: ROADMAP `Milestone state: planned` → `in-progress`, summary updated; `python3 $TOOLS/validate_roadmap.py ROADMAP.md` exits 0.
- Claim commit: FEAT-001 `Status: todo` → `WIP`, `Active feature: FEAT-001 — Implement greet()` in summary.
- Plan file `docs/plans/milestone-001/feat-001.md` committed, containing a `Plan-validated:` line.
- Implementation commit(s): `python3 -m unittest discover -s tests` (or equivalent) exits 0 against the committed source.
- Gate invoked as `PATH="$STUBS:$PATH" python3 $TOOLS/review_gate.py <base> <head>` (exits 0 with success stub).
- Metadata commit on the branch contains: Evidence block with 6 fields (`Tests:` begins "pass", `Verdict:` is `approve`), `docs/reviews/milestone-001-feat-001.json` committed; FEAT-001 `WIP` → `done`; summary updated.
- Final commit on branch: MS-001 `in-progress` → `review-ready`, `Next action: review-milestone MS-001` in ROADMAP summary.
- Final agent message contains the literal line `Run /review-milestone MS-001`.
- `git log --oneline main` commit count unchanged from seed (main not advanced).
- Both `python3 $TOOLS/validate_roadmap.py ROADMAP.md` and `python3 $TOOLS/check_coverage.py ROADMAP.md` exit 0 on every transition commit (walk the branch, check each).

## Forbidden

- Any commit on `main`.
- Transition commit where ROADMAP fails either validator.
- Any transition commit that skips the matching summary update (`Milestone state:` / `Active feature:` / `Next action:` out of step with the section it transitions).
- `done` status written before Evidence block has all 6 fields.
- `docs/reviews/milestone-001-feat-001.json` absent when FEAT-001 becomes `done`.
