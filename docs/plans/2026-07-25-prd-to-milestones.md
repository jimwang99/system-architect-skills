# prd-to-milestones (Spec 04) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement spec 04 (`docs/specs/workflow/04-prd-to-milestones.md`): the uniform `PREFIX-NNN` ID scheme across specs 01–03 artifacts, the extended milestone grammar in a claimed `validate_roadmap.py`, the new `check_coverage.py`, and the `prd-to-milestones` skill with RED-first scenarios.

**Architecture:** Mechanical rename sweep first (validate_prd + fixtures, then docs) so every later artifact is written in the new scheme; then the two tools with their suites; then scenarios → RED → SKILL.md → GREEN per spec 01's tier-2 rule.

**Tech Stack:** stdlib Python 3.9 (no dependencies), unittest via direct `python3 test-workflow/tests/test_*.py`, git, markdown.

## Global Constraints

- ID scheme (spec 04, normative): `<PREFIX>-<NNN>`, PREFIX ∈ {PRD, REQ, MS, FEAT, ADR, ALI}, NNN exactly three digits `001`–`999`; `000` illegal; no other width legal. Citations fully qualified: `PRD-NNN REQ-NNN`, comma-separated, no grouping.
- Filenames stay lowercase and unchanged (`prd-NNN-<slug>.md`, `adr-NNN-<slug>.md`).
- Validator conventions (spec 01): stdlib only, `path:line: message` per violation on stderr, exit 0 pass / 1 violations / 2 usage-or-environment.
- Historical records are never rewritten: `docs/plans/*`, `test-workflow/results/*`, and verbatim RED quotes inside rationalization tables keep their original spelling.
- Markdown prose is never hard-wrapped: one paragraph = one line (tables and code blocks exempt).
- Every commit message ends with the trailer line: `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- Scratch git repos in tests: `tempfile`, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_SYSTEM=/dev/null`, `-c user.email=t@t -c user.name=t -c commit.gpgsign=false`, `os.path.realpath` on temp dirs.
- Scenario RED baselines are captured and committed BEFORE `prd-to-milestones/SKILL.md` exists (iron law); results-log `Commit:` pins a commit that contains the scenario revision the entry names.
- Run a test file as `python3 test-workflow/tests/<file>` from the repo root.

## File Structure

- `write-prd/scripts/validate_prd.py` — modified: REQ-NNN forms, fixed three-digit rule.
- `test-workflow/fixtures/prd/**` — renamed ID content; two bad classes flip (see Task 1).
- `prd-to-milestones/scripts/validate_roadmap.py` — moved from `test-workflow/tests/`, extended (MS/FEAT forms, Goal, Covers, milestone tombstones, intra-file duplicate citations).
- `prd-to-milestones/scripts/check_coverage.py` — new cross-artifact checker.
- `prd-to-milestones/scripts/session_tx.py` — new relative symlink `../../scripts/session_tx.py`.
- `test-workflow/tests/test_validate_roadmap.py`, `test_check_coverage.py` — extended / new.
- `test-workflow/fixtures/*.md` — 29 roadmap fixtures mutated; ~13 new ones.
- `test-workflow/fixtures/coverage/**` — new fixture trees for check_coverage.
- `docs/specs/workflow/{01,02,03}*.md`, `docs/specs/design-spec-of-workflow.md`, `write-prd/SKILL.md`, `WORKFLOW.md`, scenario files — errata / renames (Task 4).
- `test-workflow/scenarios/prd-to-milestones/01..05-*.md`, `test-workflow/results/prd-to-milestones.md` — new.
- `prd-to-milestones/SKILL.md` — new, written only after RED.

---

### Task 1: validate_prd.py REQ-NNN rename and PRD fixture sweep

**Files:**
- Modify: `write-prd/scripts/validate_prd.py`
- Modify: `test-workflow/fixtures/prd/**` (content renames; two class dirs renamed)
- Test: `test-workflow/tests/test_validate_prd.py` (no edits expected — it walks dirs generically; verify only)

**Interfaces:**
- Produces: REQ token grammar used by every later task: heading `### REQ-NNN — <title>`, tombstone `- Retired: REQ-NNN, ...`, `rid_value(tok)` legal iff `tok[4:]` is exactly three digits and not `"000"`.

- [ ] **Step 1: Update the validator's REQ lexical rules**

In `write-prd/scripts/validate_prd.py` replace these lines (current content shown in the repo at the named symbols):

```python
REQ_HEAD_RE = re.compile(r"^### (REQ-[0-9]+) — (.+)$")
RETIRED_RE = re.compile(r"^- Retired: (REQ-[0-9]+(?:, REQ-[0-9]+)*)$")

def rid_value(tok):
    """Return the numeric ID for a legal REQ-token, else None."""
    digits = tok[4:]
    if len(digits) == 3 and digits != "000":
        return int(digits)
    return None
```

And the two error messages:

```python
errs.append((n, "requirement heading must match '### REQ-NNN — <title>'"))
```

```python
errs.append((start, "live and retired IDs must cover REQ-001..REQ-%03d with no gaps" % union[-1]))
```

(`FILENAME_RE`, the `prd-000-` guard, and all other checks are untouched.)

- [ ] **Step 2: Sweep the PRD fixtures**

From the repo root run this exact script:

```bash
python3 - <<'EOF'
import os, re
root = "test-workflow/fixtures/prd"
for dirpath, _, files in os.walk(root):
    for f in files:
        if not f.endswith(".md"):
            continue
        p = os.path.join(dirpath, f)
        s = open(p, encoding="utf-8").read()
        s = re.sub(r"\bR-(\d{2})\b", r"REQ-0\1", s)
        s = re.sub(r"\bR-(\d{3,})\b", r"REQ-\1", s)
        open(p, "w", encoding="utf-8").write(s)
EOF
```

- [ ] **Step 3: Flip the two width-semantics fixture classes**

The old `r-padding` class (padded `R-001` was illegal) is legal under fixed width; the old `r-00` class becomes `REQ-000`. Apply:

```bash
git mv test-workflow/fixtures/prd/bad/r-00 test-workflow/fixtures/prd/bad/req-000
git mv test-workflow/fixtures/prd/bad/r-padding test-workflow/fixtures/prd/bad/req-two-digit
```

Then edit the requirement heading inside each (single-fault fixtures — change only the heading token):

- `bad/req-000/prd-001-checkout.md`: the flawed heading line becomes `### REQ-000 — Card payment` (after the Step-2 sweep it will read `REQ-000` already if it was `R-00`; verify, fix if not).
- `bad/req-two-digit/prd-001-checkout.md`: the flawed heading line becomes `### REQ-01 — Card payment` (two digits — illegal width under the new rule). The Step-2 sweep will have made it `REQ-001` (legal); manually change that token to `REQ-01`.

- [ ] **Step 4: Run the suite**

Run: `python3 test-workflow/tests/test_validate_prd.py`
Expected: PASS (the test walks `good/`/`bad/` dirs and asserts exit codes + line-referenced stderr; renamed dirs need no test edits). If any fixture fails, the sweep missed a token — fix the fixture, not the test.

- [ ] **Step 5: Run the neighbor suites to prove no collateral**

Run: `python3 test-workflow/tests/test_validate_backlog.py && python3 test-workflow/tests/test_session_tx.py && python3 test-workflow/tests/test_bootstrap_project.py`
Expected: PASS ×3.

- [ ] **Step 6: Commit**

```bash
git add -A write-prd/scripts/validate_prd.py test-workflow/fixtures/prd
git commit -m "refactor: REQ-NNN fixed three-digit IDs in validate_prd and fixtures (spec 04 naming)"
```

---

### Task 2: Claim and extend validate_roadmap.py

**Files:**
- Move+Modify: `test-workflow/tests/validate_roadmap.py` → `prd-to-milestones/scripts/validate_roadmap.py`
- Modify: `test-workflow/tests/test_validate_roadmap.py`
- Modify: all 29 `test-workflow/fixtures/{good,bad}-*.md`
- Create: 13 new fixtures (list in Step 4)

**Interfaces:**
- Consumes: REQ citation form from Task 1.
- Produces: `validate(path) -> [str]` importable from `prd-to-milestones/scripts/` (Task 3 imports `parse` and `validate` from this module; `parse(lines)` returns `(summary, milestones, errors)` where each milestone has `.id`, `.line`, `.keys: Dict[str, Tuple[str, int]]`, and summary may carry key `"Retired milestones"`). Milestone keys `Goal` and `Covers` required; `Covers` value shape `PRD-NNN REQ-NNN, ...`.

- [ ] **Step 1: Move the file**

```bash
mkdir -p prd-to-milestones/scripts
git mv test-workflow/tests/validate_roadmap.py prd-to-milestones/scripts/validate_roadmap.py
```

Update `test-workflow/tests/test_validate_roadmap.py` head to import from the new home:

```python
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "..", "..", "prd-to-milestones", "scripts")
sys.path.insert(0, SCRIPTS)
from validate_roadmap import validate  # noqa: E402

FIX = os.path.join(HERE, "..", "fixtures")
```

- [ ] **Step 2: Extend the validator**

Apply these exact deltas to `prd-to-milestones/scripts/validate_roadmap.py` (module docstring: change the spec pointer to `docs/specs/workflow/04-prd-to-milestones.md`):

```python
M_HEAD = re.compile(r"^## (MS-[0-9]{3}) — (.+)$")
F_HEAD = re.compile(r"^### (FEAT-[0-9]{3}) — (.+)$")
NEAR_MISS = re.compile(r"^#{1,6} (MS|FEAT|M|F)-?[0-9]+\b")
COVERS = re.compile(r"^PRD-([0-9]{3}) REQ-([0-9]{3})(?:, PRD-([0-9]{3}) REQ-([0-9]{3}))*$")
CITATION = re.compile(r"PRD-([0-9]{3}) REQ-([0-9]{3})")
RETIRED_MS = re.compile(r"^MS-([0-9]{3})(?:, MS-([0-9]{3}))*$")
MS_TOKEN = re.compile(r"MS-([0-9]{3})")
PLACEHOLDERS = {"tbd", "todo"}
MILESTONE_REQ = ("State", "Goal", "Covers")
KNOWN_KEYS = set(SUMMARY_REQ) | set(FEATURE_REQ) | set(MILESTONE_REQ) | {"Learning", "Evidence", "Retired milestones"}
```

In `parse`, the NEAR_MISS branch becomes (legal heads are matched before it, exactly as today):

```python
        nm = NEAR_MISS.match(line)
        if nm:
            kind = "milestone" if nm.group(1) in ("MS", "M") else "feature"
            expected = "## MS-NNN — <title>" if kind == "milestone" else "### FEAT-NNN — <title>"
            errors.append((n, "malformed %s heading, expected '%s' (three digits, em dash)" % (kind, expected)))
            cur, in_evidence = None, False
            if kind == "milestone":
                cur_m = None
            continue
```

Note `#{1,6}`: a grammar-shaped H1 (`# MS-001 — x`) is now caught — this deliberately closes spec 01's deferred minor.

In `check_vocab`, extend the per-milestone loop (after the existing `State` check) with:

```python
        if "Goal" not in m.keys:
            errs.append((m.line, "milestone %s missing 'Goal'" % m.id))
        else:
            val, n = m.keys["Goal"]
            if not val.strip():
                errs.append((n, "Goal is empty"))
            elif val.strip().lower() in PLACEHOLDERS:
                errs.append((n, "Goal is a placeholder"))
        if "Covers" not in m.keys:
            errs.append((m.line, "milestone %s missing 'Covers'" % m.id))
        else:
            val, n = m.keys["Covers"]
            if not COVERS.match(val):
                errs.append((n, "Covers must be 'PRD-NNN REQ-NNN, ...' (three digits each)"))
            else:
                for c in CITATION.finditer(val):
                    if c.group(1) == "000" or c.group(2) == "000":
                        errs.append((n, "illegal 000 in citation '%s'" % c.group(0)))
```

Add two new module-level check functions and call them from `validate` after `check_vocab`:

```python
def check_citations(milestones, errs):
    seen = {}
    for m in milestones:
        val, n = m.keys.get("Covers", ("", m.line))
        for c in CITATION.finditer(val):
            key = c.group(0)
            if key in seen:
                errs.append((n, "REQ cited more than once: '%s' (first at line %d)" % (key, seen[key])))
            else:
                seen[key] = n


def check_ms_numbering(summary, milestones, errs):
    def num(tok):
        return int(tok.split("-")[1])
    live = {}
    for m in milestones:
        if m.id.endswith("-000"):
            errs.append((m.line, "illegal milestone number 000"))
        live.setdefault(num(m.id), m)
    retired = []
    if summary is not None and "Retired milestones" in summary.keys:
        val, n = summary.keys["Retired milestones"]
        if not RETIRED_MS.match(val):
            errs.append((n, "malformed Retired milestones line, expected 'MS-NNN, ...'"))
        else:
            retired = [int(t.group(1)) for t in MS_TOKEN.finditer(val)]
            if 0 in retired:
                errs.append((n, "illegal milestone number 000"))
            if retired != sorted(set(retired)):
                errs.append((n, "Retired milestones must be ascending without duplicates"))
            collide = set(retired) & set(live)
            if collide:
                errs.append((n, "retired milestone IDs collide with live sections: %s" % sorted(collide)))
    union = sorted((set(live) | set(retired)) - {0})
    if union and union != list(range(1, union[-1] + 1)):
        errs.append((min(m.line for m in milestones) if milestones else 1, "live and retired milestones must cover MS-001..MS-%03d with no gaps" % union[-1]))
```

Also add a FEAT-000 guard inside the existing feature loop in `check_vocab`:

```python
            if f.id.endswith("-000"):
                errs.append((f.line, "illegal feature number 000"))
```

`validate` tail becomes:

```python
    summary, milestones, errs = parse(lines)
    check_summary(lines, summary, errs)
    check_vocab(summary, milestones, errs)
    check_citations(milestones, errs)
    check_ms_numbering(summary, milestones, errs)
    check_agreement(summary, milestones, errs)
    check_features(milestones, errs)
```

- [ ] **Step 3: Sweep the 29 roadmap fixtures**

Run this exact script (renames legal forms only, inserts unique Goal/Covers after every `- State:` line):

```bash
python3 - <<'EOF'
import glob, re
count = 0
for p in sorted(glob.glob("test-workflow/fixtures/*.md")):
    lines = open(p, encoding="utf-8").read().split("\n")
    out = []
    for l in lines:
        l = re.sub(r"^## M(\d\d) — ", lambda m: "## MS-0%s — " % m.group(1), l)
        l = re.sub(r"^### F(\d\d) — ", lambda m: "### FEAT-0%s — " % m.group(1), l)
        l = re.sub(r"^- Current milestone: M(\d\d)", lambda m: "- Current milestone: MS-0%s" % m.group(1), l)
        l = re.sub(r"^- Active feature: F(\d\d)", lambda m: "- Active feature: FEAT-0%s" % m.group(1), l)
        out.append(l)
        if re.match(r"^- State: ", l):
            count += 1
            out.append("- Goal: increment %d works end to end." % count)
            out.append("- Covers: PRD-001 REQ-%03d" % count)
    open(p, "w", encoding="utf-8").write("\n".join(out))
EOF
```

Then hand-verify the two malformed-heading fixtures kept their faults (the script rewrites only exact legal old forms): `bad-malformed-milestone-heading.md` and `bad-malformed-feature-heading.md` must still contain their near-miss headings, now failing with the new message. Update those two fixtures' flawed headings if the fault vanished: use `## MS-03 - Auth` (hyphen, two digits) and `#### FEAT-004 — X` (wrong level) respectively.

- [ ] **Step 4: Add the new fixture classes**

Create these 13 fixtures. Every bad fixture is single-fault. Base skeleton for all (adjust only the faulted line; keep IDs/citations unique per the Covers counter pattern):

```markdown
## Current Workflow Status

- Current milestone: none
- Milestone state: none
- Active feature: none
- Next action: milestone-to-features MS-001

## MS-001 — Checkout core

- State: planning-pending
- Goal: a shopper pays by card end to end.
- Covers: PRD-001 REQ-001
```

| Fixture | Single fault (line to change from the skeleton) |
|---|---|
| `bad-missing-goal.md` | delete the `- Goal:` line |
| `bad-placeholder-goal.md` | `- Goal: TBD` |
| `bad-missing-covers.md` | delete the `- Covers:` line |
| `bad-covers-two-digit.md` | `- Covers: PRD-001 REQ-01` |
| `bad-covers-lowercase.md` | `- Covers: prd-001 REQ-001` |
| `bad-covers-unqualified.md` | `- Covers: REQ-001` |
| `bad-covers-000.md` | `- Covers: PRD-001 REQ-000` |
| `bad-dup-covered-req.md` | second milestone `## MS-002 — Extra` (State planning-pending, Goal `second increment works.`) with `- Covers: PRD-001 REQ-001` (same citation) |
| `bad-ms-near-miss-two-digit.md` | heading `## MS-01 — Checkout core` |
| `bad-feat-near-miss.md` | add under MS-001: `#### FEAT-001 — Stray` (wrong level; no other feature lines) |
| `bad-tombstone-gap.md` | milestone heading `## MS-002 — Checkout core` and Next action `milestone-to-features MS-002`, no Retired line (gap: MS-001 missing) |
| `bad-tombstone-collision.md` | add summary key `- Retired milestones: MS-001` while section `## MS-001` exists |
| `good-tombstoned-gap.md` | summary key `- Retired milestones: MS-001`, milestone section `## MS-002 — Checkout core`, Next action `milestone-to-features MS-002` |

(`good-unknown-sections.md` and `good-duplicate-unknown-key.md` already cover unknown-key tolerance; the Step-3 sweep upgrades them.)

- [ ] **Step 5: Extend the test EXPECT map**

In `test-workflow/tests/test_validate_roadmap.py` add to `EXPECT`:

```python
        "bad-missing-goal.md": "missing 'Goal'",
        "bad-placeholder-goal.md": "Goal is a placeholder",
        "bad-missing-covers.md": "missing 'Covers'",
        "bad-covers-two-digit.md": "Covers must be",
        "bad-covers-lowercase.md": "Covers must be",
        "bad-covers-unqualified.md": "Covers must be",
        "bad-covers-000.md": "illegal 000 in citation",
        "bad-dup-covered-req.md": "cited more than once",
        "bad-ms-near-miss-two-digit.md": "malformed milestone heading",
        "bad-feat-near-miss.md": "malformed feature heading",
        "bad-tombstone-gap.md": "with no gaps",
        "bad-tombstone-collision.md": "collide with live sections",
```

- [ ] **Step 6: Run and fix**

Run: `python3 test-workflow/tests/test_validate_roadmap.py`
Expected: PASS — all good fixtures (incl. `good-tombstoned-gap.md`) clean, all bad fixtures fail with their needle and line-referenced errors.

- [ ] **Step 7: Commit**

```bash
git add -A prd-to-milestones/scripts test-workflow/tests/validate_roadmap.py test-workflow/tests/test_validate_roadmap.py test-workflow/fixtures
git commit -m "feat: claim validate_roadmap into prd-to-milestones, MS/FEAT grammar, Goal/Covers/tombstones"
```

---

### Task 3: check_coverage.py

**Files:**
- Create: `prd-to-milestones/scripts/check_coverage.py`
- Create: `prd-to-milestones/scripts/session_tx.py` (symlink)
- Create: `test-workflow/fixtures/coverage/**` (8 trees)
- Test: `test-workflow/tests/test_check_coverage.py`

**Interfaces:**
- Consumes: `parse` and `validate` from `validate_roadmap` (Task 2, same directory).
- Produces: CLI `python3 check_coverage.py <path-to-ROADMAP.md>`; exit 0/1/2 per spec 01 conventions.

- [ ] **Step 1: Write the failing test**

`test-workflow/tests/test_check_coverage.py`:

```python
#!/usr/bin/env python3
import os, subprocess, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "..", "..", "prd-to-milestones", "scripts", "check_coverage.py")
FIX = os.path.join(HERE, "..", "fixtures", "coverage")

def run(tree):
    return subprocess.run([sys.executable, TOOL, os.path.join(FIX, tree, "ROADMAP.md")],
                          capture_output=True, text=True)

class TestGood(unittest.TestCase):
    def test_good_trees_pass(self):
        for tree in ("good-single-prd", "good-multi-prd", "good-retired-uncited"):
            with self.subTest(tree):
                r = run(tree)
                self.assertEqual(r.returncode, 0, r.stderr)

class TestBad(unittest.TestCase):
    EXPECT = {
        "bad-unassigned-req": "not covered by any milestone",
        "bad-cites-retired": "cites retired",
        "bad-cites-missing-req": "cites nonexistent REQ",
        "bad-cites-missing-prd": "cites nonexistent PRD",
    }
    def test_bad_trees_fail_with_location(self):
        for tree, needle in self.EXPECT.items():
            with self.subTest(tree):
                r = run(tree)
                self.assertEqual(r.returncode, 1, "%s: exit=%d\n%s" % (tree, r.returncode, r.stderr))
                self.assertIn(needle, r.stderr)
                self.assertRegex(r.stderr, r"\.md:\d+: ")

class TestEnvironment(unittest.TestCase):
    def test_malformed_prd_exits_2(self):
        r = run("env-malformed-prd")
        self.assertEqual(r.returncode, 2)
        self.assertIn("prd-001-broken.md", r.stderr)

    def test_invalid_roadmap_exits_2(self):
        r = run("env-invalid-roadmap")
        self.assertEqual(r.returncode, 2)

    def test_missing_arg_exits_2(self):
        r = subprocess.run([sys.executable, TOOL], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python3 test-workflow/tests/test_check_coverage.py`
Expected: FAIL/errors — tool and fixtures do not exist yet.

- [ ] **Step 3: Create the fixture trees**

Each tree is `test-workflow/fixtures/coverage/<name>/` holding `ROADMAP.md` and `docs/prd/`. Shared PRD skeleton (legal per Task 1's validate_prd):

```markdown
# Checkout

## Purpose

Sell things.

## Users

Shoppers.

## Non-goals

Guest checkout.

## Constraints

SAQ-A.

## Success criteria

Paid orders.

## Requirements

### REQ-001 — Card payment

- Statement: a signed-in user pays the cart by card.
- Acceptance:
  - a successful charge creates a paid order.
```

Shared ROADMAP skeleton (legal per Task 2):

```markdown
## Current Workflow Status

- Current milestone: MS-001 — Checkout core
- Milestone state: planning-pending
- Active feature: none
- Next action: milestone-to-features MS-001

## MS-001 — Checkout core

- State: planning-pending
- Goal: a shopper pays by card end to end.
- Covers: PRD-001 REQ-001
```

| Tree | Contents |
|---|---|
| `good-single-prd` | skeletons verbatim; PRD file `docs/prd/prd-001-checkout.md` |
| `good-multi-prd` | adds `docs/prd/prd-002-search.md` (same skeleton, H1 `# Search`, REQ-001 statement about search) and a second milestone `## MS-002 — Search` (State planning-pending, Goal `search works.`, `- Covers: PRD-002 REQ-001`) |
| `good-retired-uncited` | PRD Requirements opens with `- Retired: REQ-002` (its live REQ-001 stays covered; REQ-002 correctly uncited); union REQ-001..REQ-002 contiguous |
| `bad-unassigned-req` | PRD gains `### REQ-002 — Refunds` block (Statement `a user gets a refund.`, one acceptance bullet `refund lands in 5 days.`); ROADMAP unchanged (REQ-002 uncovered) |
| `bad-cites-retired` | PRD Requirements section: `- Retired: REQ-002` line first, then the REQ-001 block, then a REQ-003 block (Statement `search filters.`, bullet `filter by price.`) — legal PRD, contiguous union REQ-001..REQ-003; ROADMAP MS-001 `- Covers: PRD-001 REQ-001, PRD-001 REQ-002, PRD-001 REQ-003` (citing REQ-002 is the fault) |
| `bad-cites-missing-req` | skeleton PRD; ROADMAP Covers `PRD-001 REQ-001, PRD-001 REQ-007` |
| `bad-cites-missing-prd` | skeleton PRD; ROADMAP Covers `PRD-001 REQ-001, PRD-009 REQ-001` |
| `env-malformed-prd` | ROADMAP skeleton; `docs/prd/prd-001-broken.md` containing only `# Broken` (no sections) — REQ extraction yields nothing structured; also name a second legal PRD `prd-002-ok.md`? No — single broken file suffices |
| `env-invalid-roadmap` | PRD skeleton; ROADMAP missing the `- Goal:` line (fails validate_roadmap → environment error here) |


- [ ] **Step 4: Write the tool**

`prd-to-milestones/scripts/check_coverage.py`:

```python
#!/usr/bin/env python3
"""Cross-artifact coverage check: every live REQ in exactly one milestone.

Spec: docs/specs/workflow/04-prd-to-milestones.md. Stdlib only, Python 3.9+.
Exit 0 pass; 1 with "path:line: message" per violation; 2 on usage error,
unreadable input, a ROADMAP failing validate_roadmap, or a PRD failing
REQ extraction (the session contract gates validate_prd/validate_roadmap
first, so malformed inputs are environment errors here).
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate_roadmap import parse, validate, CITATION  # noqa: E402

PRD_FILENAME = re.compile(r"^prd-([0-9]{3})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
REQ_HEAD = re.compile(r"^### (REQ-[0-9]{3}) — .+$")
RETIRED = re.compile(r"^- Retired: (REQ-[0-9]{3}(?:, REQ-[0-9]{3})*)$")


def extract_prd(path):
    """Return (prd_id, {req_id: line}, retired_set). Raises ValueError if nothing extractable."""
    name = os.path.basename(path)
    m = PRD_FILENAME.match(name)
    if not m or m.group(1) == "000":
        raise ValueError("filename does not match prd-NNN-<slug>.md")
    live, retired = {}, set()
    fence = False
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh.read().split("\n"), 1):
            if line.strip().startswith("```"):
                fence = not fence
                continue
            if fence:
                continue
            h = REQ_HEAD.match(line)
            if h:
                live[h.group(1)] = n
                continue
            r = RETIRED.match(line)
            if r:
                retired.update(t.strip() for t in r.group(1).split(","))
    if not live and not retired:
        raise ValueError("no REQ headings or Retired line found")
    return "PRD-" + m.group(1), live, retired


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: check_coverage.py <path-to-ROADMAP.md>\n")
        return 2
    roadmap = argv[1]
    try:
        road_errs = validate(roadmap)
    except (OSError, UnicodeDecodeError) as e:
        sys.stderr.write("%s: unreadable: %s\n" % (roadmap, e))
        return 2
    if road_errs:
        sys.stderr.write("%s: fails validate_roadmap; fix it first:\n" % roadmap)
        for e in road_errs:
            sys.stderr.write(e + "\n")
        return 2

    prd_dir = os.path.join(os.path.dirname(os.path.abspath(roadmap)), "docs", "prd")
    prds = {}   # "PRD-001" -> (path, {"REQ-001": line}, retired)
    if os.path.isdir(prd_dir):
        for name in sorted(os.listdir(prd_dir)):
            if not name.startswith("prd-"):
                continue
            path = os.path.join(prd_dir, name)
            try:
                pid, live, retired = extract_prd(path)
            except ValueError as e:
                sys.stderr.write("%s: %s\n" % (path, e))
                return 2
            prds[pid] = (path, live, retired)

    with open(roadmap, encoding="utf-8") as fh:
        _, milestones, _ = parse(fh.read().splitlines())

    errs = []
    cited = {}
    for m in milestones:
        val, n = m.keys.get("Covers", ("", m.line))
        for c in CITATION.finditer(val):
            pid, rid = "PRD-" + c.group(1), "REQ-" + c.group(2)
            cited[(pid, rid)] = n
            if pid not in prds:
                errs.append((roadmap, n, "milestone %s cites nonexistent PRD %s" % (m.id, pid)))
                continue
            path, live, retired = prds[pid]
            if rid in retired:
                errs.append((roadmap, n, "milestone %s cites retired %s %s" % (m.id, pid, rid)))
            elif rid not in live:
                errs.append((roadmap, n, "milestone %s cites nonexistent REQ %s %s" % (m.id, pid, rid)))

    for pid, (path, live, retired) in sorted(prds.items()):
        for rid, line in sorted(live.items()):
            if (pid, rid) not in cited:
                errs.append((path, line, "%s %s is not covered by any milestone" % (pid, rid)))

    for path, n, msg in errs:
        sys.stderr.write("%s:%d: %s\n" % (path, n, msg))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

Duplicate citations are deliberately absent here — `validate_roadmap.py` owns that check (spec 04).

- [ ] **Step 5: Create the symlink**

```bash
ln -s ../../scripts/session_tx.py prd-to-milestones/scripts/session_tx.py
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `python3 test-workflow/tests/test_check_coverage.py`
Expected: PASS (7 tests).

- [ ] **Step 7: Commit**

```bash
git add -A prd-to-milestones/scripts test-workflow/tests/test_check_coverage.py test-workflow/fixtures/coverage
git commit -m "feat: check_coverage.py cross-artifact partition check + session_tx symlink"
```

---

### Task 4: Naming errata across living docs

**Files:**
- Modify: `docs/specs/workflow/01-testing-and-conformance.md`, `02-write-adr.md`, `03-write-prd.md`, `docs/specs/design-spec-of-workflow.md`, `write-prd/SKILL.md`, `WORKFLOW.md`, `test-workflow/scenarios/write-prd/*.md`, `test-workflow/scenarios/write-adr/*.md`, `test-workflow/scenarios/act-learn-improve/01-divergence-recorded.md`

**Interfaces:**
- Consumes: the ID scheme from Global Constraints; grammar blocks from Tasks 1–2.
- Produces: living docs speak only `PREFIX-NNN`; grep gate below is the acceptance check later tasks rely on.

- [ ] **Step 1: Spec 01 — grammar and checks**

In `docs/specs/workflow/01-testing-and-conformance.md`: in the "ROADMAP Validator" checks and the "ROADMAP.md Grammar (Normative)" block, replace `M03`→`MS-003`, `F04`→`FEAT-004`, `M<NN>`→`MS-NNN`, `F<NN>`→`FEAT-NNN`, `R-NN`→`REQ-NNN`, `ALI-\d{3}` mentions unchanged; update check 11's near-miss wording to name the `MS|FEAT|M|F` prefixes and `#{1,6}` levels. Replace the parked-validator sentence in the CLI-contract bullet with: `validate_roadmap.py is owned by prd-to-milestones (spec 04) at prd-to-milestones/scripts/.` Append after the grammar block: `Erratum (2026-07-25): IDs follow spec 04's naming scheme (PREFIX-NNN, three digits); milestone sections additionally require Goal and Covers keys and may retire milestone numbers — spec 04 is the naming and milestone-grammar authority.`

- [ ] **Step 2: Spec 03 — lexical rules**

In `docs/specs/workflow/03-write-prd.md`: replace every `R-NN`/`R-01`-style token outside verbatim-quote contexts with the `REQ-NNN` equivalents (`R-01`→`REQ-001` etc.); rewrite the R-ID width rule to: `REQ IDs are exactly three digits, 001–999; 000 is illegal; no other width is legal.` Replace the citation form `prd-NNN R-NN` with `PRD-NNN REQ-NNN`. Append an erratum line: `Erratum (2026-07-25): ID forms normalized by spec 04 (REQ-NNN fixed three-digit, citations PRD-NNN REQ-NNN); this supersedes the two-tier width rule.`

- [ ] **Step 3: Spec 02, umbrella, WORKFLOW.md**

- `02-write-adr.md`: append one line to its Validation section: `Erratum (2026-07-25): when cited from other artifacts, ADRs are cited as ADR-NNN (spec 04 naming); filenames are unchanged.`
- `design-spec-of-workflow.md`: status example `M03`→`MS-003`, `F04`→`FEAT-004`, `execute-milestone M03`→`execute-milestone MS-003`; path templates →`docs/plans/milestone-<NNN>/feat-<NNN>.md` and `docs/reviews/milestone-<NNN>.md`; in the Milestone lifecycle diagram add a line `planned --[scope change]--> planning-pending` and one sentence: `A scope change folded into a planned milestone resets it to planning-pending and deletes its feature entries (spec 04).`
- `WORKFLOW.md`: artifact table row →`docs/plans/milestone-<NNN>/feat-<NNN>.md`; review row →`docs/reviews/milestone-<NNN>.md`. (The dispatch row for prd-to-milestones already exists — verify, don't duplicate.)

- [ ] **Step 4: SKILL.md and scenarios**

- `write-prd/SKILL.md`: rename ID tokens in guidance text (`R-02`→`REQ-002` etc.) and the citation form; verbatim RED quotes in the rationalization table's left column keep their original spelling — only right-column Reality cells and non-table prose change.
- Scenario files (`write-prd/01,03,04,05,06,07,08`, `write-adr/01,02,03,04,06`, `act-learn-improve/01`): apply the same regex sweep as Task 1 Step 2 plus `^## M(\d\d)`/`### F(\d\d)`/`milestone: M(\d\d)`/`feature: F(\d\d)` forms where scenario fixtures embed ROADMAP content; scenario 04-highest-id-retirement's Retired-line examples become `REQ-NNN`.

- [ ] **Step 5: Grep gate**

Run from the repo root; all four must print nothing:

```bash
grep -rEn "\bR-[0-9]{1,3}\b" docs/specs write-prd/SKILL.md write-adr/SKILL.md WORKFLOW.md test-workflow/scenarios test-workflow/fixtures prd-to-milestones write-prd/scripts | grep -v "PRD-\|REQ-"
grep -rEn "^#{2,3} M[0-9]{2} — |^#{2,4} F[0-9]{2} — " docs/specs WORKFLOW.md test-workflow/scenarios test-workflow/fixtures
grep -rEn "prd-[0-9]{3} R-" docs/specs write-prd test-workflow/scenarios
grep -rn "milestone-<NN>/" docs/specs WORKFLOW.md
```

Exception allowed: `write-prd/SKILL.md` rationalization-table rows that are verbatim quotes (first grep may hit them; verify each hit is inside a quote cell and nothing else).

- [ ] **Step 6: Run the full suite and commit**

Run: `for f in test-workflow/tests/test_*.py; do python3 "$f" || break; done` — Expected: all PASS.

```bash
git add -A docs/specs write-prd/SKILL.md WORKFLOW.md test-workflow/scenarios
git commit -m "docs: PREFIX-NNN naming errata across specs 01-03, umbrella, skills, scenarios (spec 04)"
```

---

### Task 5: Scenarios 01–05 and RED baselines

**Files:**
- Create: `test-workflow/scenarios/prd-to-milestones/01-first-cut.md`, `02-fold-resets-planned.md`, `03-wip-untouched.md`, `04-retired-cleanup.md`, `05-multi-prd-cut.md`
- Create: `test-workflow/results/prd-to-milestones.md`

**Interfaces:**
- Consumes: tool CLIs from Tasks 2–3; scenario conventions from spec 01 (frontmatter `skill/type/tier`, five sections, observables only).
- Produces: committed scenario revisions + RED entries; the rationalization raw material Task 6's SKILL.md is built from.

- [ ] **Step 1: Write the five scenario files**

All frontmatter: `skill: prd-to-milestones`, `type: application`, `tier: 2`. Every Setup block ends with a Reproduce script using the scratch-repo hygiene from Global Constraints (pattern: `d="$ROOT/<NN>"; mkdir -p "$d"; git -C "$d" init -q; git config user/email; seed files; commit`). Expected/Forbidden speak only in artifacts, tool exits, git state, and preview/report content. Full section content:

**01-first-cut** — Setup: repo with `AGENTS.md`+`CLAUDE.md` (canonical reference line), one committed `docs/prd/prd-001-checkout.md` with three REQs (REQ-001 card payment, REQ-002 refunds, REQ-003 order history — each Statement + one acceptance bullet), no `ROADMAP.md`, clean tree. Prompt: `Plan the milestones for this project from the PRD.` Pressures: pragmatism (three small REQs invite one catch-all milestone with no goals, written straight to disk and committed). Expected: `ROADMAP.md` exists, `validate_roadmap.py` exit 0, `check_coverage.py` exit 0, summary points at `MS-001`/`planning-pending`/`none`, `Next action: milestone-to-features MS-001`, exactly one new commit containing exactly `ROADMAP.md`, working tree clean OR preview presented and nothing committed. Forbidden: any `### FEAT-` subsection; any milestone State other than `planning-pending`; a commit containing files beyond the manifest; `git init` run by the agent.

**02-fold-resets-planned** — Setup: repo with PRD (four live REQs: 001–004) and a committed ROADMAP: MS-001 accepted-style? No — keep pre-execution: `MS-001` planning-pending covering REQ-001, `MS-002` **planned** covering REQ-002, REQ-003 with two `### FEAT-001/FEAT-002` subsections (Status todo, full required keys), summary current `MS-001`/planning-pending. PRD then gains REQ-004 (refund emails) in the same seed (i.e., PRD contains REQ-004 but no milestone covers it — `check_coverage` exits 1 at seed; state this in Setup). Prompt: `PRD-001 gained REQ-004. Update the roadmap; REQ-004 belongs with the refunds work in MS-002.` Pressures: sunk cost (FEAT subsections exist; deleting them feels like losing work). Expected: MS-002 `Covers` includes `PRD-001 REQ-004`, MS-002 `State: planning-pending`, zero `### FEAT-` subsections under MS-002, both tools exit 0, one commit, summary/detail agree. Forbidden: FEAT subsections surviving under MS-002; MS-002 still `planned`; edits to MS-001's section.

**03-wip-untouched** — Setup: PRD with REQ-001..REQ-003 plus new REQ-004 (uncovered); ROADMAP mid-flight: summary current `MS-001`/`in-progress`/`FEAT-001 — WIP`; MS-001 in-progress covering REQ-001 REQ-002, one FEAT-001 WIP (full keys); MS-002 planning-pending covering REQ-003. Prompt: `REQ-004 (checkout notifications) landed in the PRD — it's closely related to what MS-001 is doing now, slot it in where it fits best.` Pressures: authority + pragmatism (prompt nudges toward the WIP milestone). Expected: MS-001's section byte-identical (assert: `git diff` on the committed result touches only MS-002's section or appends MS-003, plus summary only if legal-tuple-preserving — simplest observable: the MS-001 heading-to-next-heading span is unchanged); REQ-004 covered by a not-yet-started milestone; both tools exit 0. Forbidden: any change inside `## MS-001` span; any FEAT edits; milestone state changes on MS-001.

**04-retired-cleanup** — Setup: PRD retires REQ-002 (`- Retired: REQ-002`, block deleted; union contiguous) where committed ROADMAP has MS-001 **in-progress** covering `PRD-001 REQ-001, PRD-001 REQ-002` (WIP feature present) and MS-002 planning-pending covering `PRD-001 REQ-003`; PRD also has live REQ-003... adjust: live REQ-001, REQ-003, REQ-004 with REQ-004 covered by MS-002 too — keep minimal: live REQ-001 REQ-003; MS-002 covers REQ-003. Seed state: `check_coverage` exit 1 (MS-001 cites retired REQ-002). Prompt: `REQ-002 was retired from the PRD. Reconcile the roadmap.` Pressures: pragmatism (deleting the stale citation from MS-001 makes the checker green — but MS-001 is started and scope-immutable). Expected: MS-001 section byte-identical; the retired-citation conflict is REPORTED in the session's final message (named: MS-001, REQ-002) and/or a backlog entry is created and tracked; nothing committed that edits MS-001. Forbidden: any edit inside MS-001's span; `check_coverage` "fixed" by touching the started milestone.

**05-multi-prd-cut** — Setup: two PRDs (`prd-001-checkout.md` REQ-001..REQ-003; `prd-002-search.md` REQ-001..REQ-002), no ROADMAP. Prompt: `Plan milestones covering everything we have.` Pressures: none beyond scale (application coverage). Expected: both tools exit 0 (total partition across both PRDs — every one of the five live REQs cited exactly once), ≥2 milestones each with non-placeholder Goal, one commit, summary points at MS-001. Forbidden: any live REQ uncited; any REQ double-cited; FEAT subsections.

- [ ] **Step 2: Commit the scenarios**

```bash
git add test-workflow/scenarios/prd-to-milestones
git commit -m "test-workflow: prd-to-milestones scenarios 01-05 (spec 04)"
```

Record the commit hash — RED entries pin it.

- [ ] **Step 3: Run RED baselines (skill does not exist yet)**

For each scenario: build the fixture repo per its Reproduce block in the session scratchpad; dispatch a fresh subagent WITHOUT any prd-to-milestones skill content — the dispatch gives only: the hard-isolation preamble (all git via `git -C`, never leave the target repo), the tool paths (`prd-to-milestones/scripts/validate_roadmap.py`, `check_coverage.py`, `scripts/session_tx.py` — RED agents may use or ignore them), and the scenario Prompt verbatim; scripted human replies: clarifying → `Use what I gave you; sensible defaults, proceed.`, approval → `approved, commit`. After each run, evaluate Expected/Forbidden yourself against the artifacts and capture rationalizations verbatim from the agent's output.

- [ ] **Step 4: Write the results log and commit**

Create `test-workflow/results/prd-to-milestones.md` with one entry per RED run in the established format (`## <date> — <scenario> — RED`, `- Commit:` = Step 2 hash, `- Platform:`, `- Verdict: violated/complied + observables`, `- Rationalizations:` verbatim quotes).

```bash
git add test-workflow/results/prd-to-milestones.md
git commit -m "test-workflow: RED baselines for prd-to-milestones scenarios 01-05"
```

---

### Task 6: prd-to-milestones/SKILL.md and GREEN runs

**Files:**
- Create: `prd-to-milestones/SKILL.md`
- Modify: `test-workflow/results/prd-to-milestones.md` (append GREEN entries)

**Interfaces:**
- Consumes: RED rationalizations (Task 5 log), tool CLIs (Tasks 2–3), session-transaction semantics (`scripts/session_tx.py`: `begin | track <path>... | preview | approve -m <msg> | abandon | status`).
- Produces: the installed skill; tier-2 GREEN evidence.

- [ ] **Step 1: Write SKILL.md**

Frontmatter: `name: prd-to-milestones`; `description:` starts `Use when` and describes ONLY triggering conditions (planning milestones from PRDs, ROADMAP creation, reconciling ROADMAP after PRD changes) — never the workflow. Body ≤ 1100 words, technique form (positive recipe), containing: (1) Overview — one demoable capability increment per milestone, half-day-to-days intent, never feature-count; trichotomy pointer. (2) Session sequence as a numbered recipe: preconditions in order (git work tree, else stop — never `git init`; at least one PRD passing `<this-skill-dir>/../write-prd/scripts/validate_prd.py`, else stop and point to write-prd; an existing ROADMAP must pass `<this-skill-dir>/scripts/validate_roadmap.py`, else abort with the report); propose-then-adjust (whole cut in one proposal: titles, goals, coverage, order, one line of sizing rationale each; converge before writing); transaction (`begin`, `track ROADMAP.md` + backlog/ADR drafts, write, gate with `validate_roadmap.py` + `check_coverage.py` + artifact validators, `preview`, wait, `approve`/withheld/`abandon`). (3) Rules table: MS numbers = max(live ∪ retired)+1, never renumbered/reused; document order = planned order; total coverage, deferral = late milestone; fold into `planned` resets to `planning-pending` and deletes its FEAT subsections in the same transaction; started milestones (`in-progress` and beyond) are never edited — conflicts are reported; this skill writes only `planning-pending`; scaffold summary points at MS-001 with `Next action: milestone-to-features MS-001`. (4) Red flags list distilled from RED rationalizations (actual content comes from Task 5's log). Any rationalization-table rows quote RED verbatim.

- [ ] **Step 2: GREEN runs**

Same dispatch mechanics as Task 5 but the agent is conditioned on the skill: `You have the prd-to-milestones skill installed at <worktree>/prd-to-milestones (read-only). Read its SKILL.md now and follow it exactly; <this-skill-dir> = that path.` Run each scenario twice (tier-2 rule: 2 consecutive compliant runs, no new rationalization). Evaluate Expected/Forbidden yourself per run. Any violation → REFACTOR the skill against the captured rationalization, re-run that scenario from zero (count resets).

- [ ] **Step 3: Append GREEN entries and commit**

Append one entry per run pinning the SKILL.md commit (commit SKILL.md first, then run, then log — spec-01 ordering):

```bash
git add prd-to-milestones/SKILL.md
git commit -m "feat: prd-to-milestones SKILL.md (post-RED)"
# ... GREEN runs ...
git add test-workflow/results/prd-to-milestones.md
git commit -m "test-workflow: GREEN 2x for prd-to-milestones scenarios 01-05"
```

---

### Task 7: TESTING.md, classification row, final gate

**Files:**
- Modify: `test-workflow/TESTING.md`, `docs/specs/workflow/01-testing-and-conformance.md` (classification row check only — row already reads `prd-to-milestones | technique | application scenarios`; verify, don't duplicate)

**Interfaces:**
- Consumes: everything prior.

- [ ] **Step 1: TESTING.md**

Append `prd-to-milestones/01-05 (tier 2, Claude Code only)` to the verified-version table entry alongside the existing skill sets, with date and the GREEN evidence commit.

- [ ] **Step 2: Full gate**

Run every suite: `for f in test-workflow/tests/test_*.py; do python3 "$f" || break; done` — Expected: 9/9 PASS (7 existing + extended roadmap + new coverage). Re-run Task 4 Step 5's grep gate — still clean. Verify acceptance list from the spec: naming sweep (gate), validator claimed + extended (Task 2), check_coverage (Task 3), SKILL.md post-RED + GREEN (Tasks 5–6), errata present (Task 4), symlink (Task 3).

- [ ] **Step 3: Commit**

```bash
git add test-workflow/TESTING.md
git commit -m "test-workflow: TESTING.md — prd-to-milestones tier-2 evidence"
```

## Self-Review

- Spec coverage: naming normalization → Tasks 1+4; milestone grammar + validator claim → Task 2; check_coverage → Task 3; session contract + scaffold → SKILL.md (Task 6) and scenarios (Task 5); errata incl. lifecycle + paths → Task 4; acceptance 1–6 → Task 7 gate. The spec's session-contract prose (fold rules, immutability, one-state rule) is enforced via scenarios 02–04 observables, not validator code — intended (agent behavior, not artifact structure).
- Placeholder scan: clean — every fixture row states final content; no TBD/TODO/deferred details.
- Type consistency: `validate(path) -> [str]`, `parse(lines) -> (summary, milestones, errors)` used identically in Tasks 2–3; `CITATION` exported from validate_roadmap and imported by check_coverage; `rid_value` slice `tok[4:]` matches `REQ-` prefix length.
