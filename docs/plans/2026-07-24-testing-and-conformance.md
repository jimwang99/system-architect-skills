# Testing & Cross-Platform Conformance (Spec 01) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `test-workflow/` harness from spec 01: a stdlib-Python ROADMAP validator proven against fixtures, the scenario conventions proven end-to-end on one toy scenario, and a seeded `TESTING.md`.

**Architecture:** One validator module (`validate_roadmap.py`) exposing `validate(path) -> List[str]`, exercised by a stdlib-unittest test file over markdown fixtures; scenario and results files are plain markdown following the spec's formats; no runner — live runs are dispatched subagents.

**Tech Stack:** Python 3.9 stdlib only (re, dataclasses, unittest). No pip installs, no pytest.

**Spec:** `docs/specs/workflow/01-testing-and-conformance.md` — read it before starting any task. The ROADMAP grammar, the 10 validator checks, and the legal-tuple table there are normative; this plan implements them.

## Global Constraints

- Python 3.9 compatible, stdlib only (system `/usr/bin/python3` is 3.9.6).
- Validator CLI: `python3 test-workflow/validators/validate_roadmap.py <path>`; exit 0 on pass; exit 1 with one `path:line: message` per violation on stderr.
- Validators check structure only — never prose quality.
- Headings in ROADMAP grammar use em dash `—` (U+2014), e.g. `## M03 — Authentication`.
- Results logs are append-only; entries carry `Commit:` (repo HEAD) and model identity; no transcript dumps.
- All prose in created markdown files is not hard-wrapped (one paragraph = one line).
- Run tests with `python3 test-workflow/validators/test_validate_roadmap.py` (unittest.main guard; the hyphen in `test-workflow` rules out module-path invocation).

---

### Task 1: Validator skeleton — parser, summary checks (#1, #10)

**Files:**
- Create: `test-workflow/validators/validate_roadmap.py`
- Create: `test-workflow/validators/test_validate_roadmap.py`
- Create: `test-workflow/validators/fixtures/good-idle.md`
- Create: `test-workflow/validators/fixtures/bad-missing-status.md`
- Create: `test-workflow/validators/fixtures/bad-duplicate-key.md`
- Create: `test-workflow/validators/fixtures/bad-next-action-placeholder.md`

**Interfaces:**
- Produces: `validate(path: str) -> List[str]` (each item formatted `"{path}:{line}: {message}"`), `parse(lines: List[str]) -> Tuple[Optional[Node], List[Milestone], List[Tuple[int, str]]]`, dataclasses `Node` (`id`, `title`, `line`, `keys: Dict[str, Tuple[str, int]]`), `Feature(Node)` (adds `evidence: Dict[str, Tuple[str, int]]`), `Milestone(Node)` (adds `features: List[Feature]`). Later tasks add check functions called from `validate`.

- [ ] **Step 1: Write the failing test**

```python
#!/usr/bin/env python3
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from validate_roadmap import validate  # noqa: E402

FIX = os.path.join(HERE, "fixtures")


def fixture(name):
    return os.path.join(FIX, name)


class TestGoodFixtures(unittest.TestCase):
    def test_all_good_fixtures_pass(self):
        for name in sorted(os.listdir(FIX)):
            if name.startswith("good-"):
                with self.subTest(name):
                    self.assertEqual(validate(fixture(name)), [])


class TestBadFixtures(unittest.TestCase):
    # fixture name -> substring that must appear in at least one error
    EXPECT = {
        "bad-missing-status.md": "Current Workflow Status",
        "bad-duplicate-key.md": "duplicate key",
        "bad-next-action-placeholder.md": "Next action",
    }

    def test_bad_fixtures_fail_with_expected_error(self):
        for name, needle in self.EXPECT.items():
            with self.subTest(name):
                errs = validate(fixture(name))
                self.assertTrue(errs, "expected errors for " + name)
                self.assertTrue(any(needle in e for e in errs), errs)

    def test_every_error_is_line_referenced(self):
        for name in self.EXPECT:
            for e in validate(fixture(name)):
                self.assertRegex(e, r":\d+: ")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Create the fixtures**

`fixtures/good-idle.md` (legal all-`none` tuple, zero milestones):

```markdown
## Current Workflow Status

- Current milestone: none
- Milestone state: none
- Active feature: none
- Next action: write-prd docs/prd/prd-001-initial.md
```

`fixtures/bad-missing-status.md` (first section is not the status block → check #1):

```markdown
## M01 — Setup

- State: planned

### F01 — Scaffold

- Status: todo
- Description: scaffold the project.
- Acceptance: repo builds.
- Test intent: smoke test.
```

`fixtures/bad-duplicate-key.md` (required key twice → check #1):

```markdown
## Current Workflow Status

- Current milestone: none
- Milestone state: none
- Active feature: none
- Active feature: none
- Next action: write-prd docs/prd/prd-001-initial.md
```

`fixtures/bad-next-action-placeholder.md` (check #10):

```markdown
## Current Workflow Status

- Current milestone: none
- Milestone state: none
- Active feature: none
- Next action: TBD
```

- [ ] **Step 3: Run test to verify it fails**

Run: `python3 test-workflow/validators/test_validate_roadmap.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'validate_roadmap'`

- [ ] **Step 4: Write the parser and summary checks**

```python
#!/usr/bin/env python3
"""Validate a ROADMAP.md against the doc-driven workflow grammar.

Spec: docs/specs/workflow/01-testing-and-conformance.md.
Stdlib only, Python 3.9+. Exit 0 on pass; exit 1 with one
"path:line: message" per violation on stderr.
"""
import sys
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

MILESTONE_STATES = {
    "planning-pending", "planned", "in-progress", "paused",
    "review-ready", "remediating", "accepted",
}
MIDFLIGHT = {"in-progress", "paused", "review-ready", "remediating"}
FUTURE_OK = {"planning-pending", "planned"}
FEATURE_STATUS = re.compile(
    r"^(todo|WIP|done|blocked\([a-z0-9][a-z0-9-]*\)|failed\(.+\))$")
M_HEAD = re.compile(r"^## (M\d{2}) — (.+)$")
F_HEAD = re.compile(r"^### (F\d{2}) — (.+)$")
KEY = re.compile(r"^- ([A-Z][A-Za-z ]*): (.*?)\s*$")
EV_KEY = re.compile(r"^  - ([A-Z][A-Za-z ]*): (.*?)\s*$")

SUMMARY_REQ = ("Current milestone", "Milestone state", "Active feature", "Next action")
FEATURE_REQ = ("Status", "Description", "Acceptance", "Test intent")
EVIDENCE_REQ = ("Base", "Commits", "Tests", "Reviewer", "Verdict", "Findings")
ACCEPT_VERDICTS = {"approve", "approve-with-findings"}
FINDINGS = re.compile(
    r"^(none|[^;]+: (fixed|refuted\(.+?\))(; [^;]+: (fixed|refuted\(.+?\)))*)$")
LEARNING = re.compile(r"^docs/learnings/ALI-\d{3}\.md$")
STATUS_HEADING = "## Current Workflow Status"


@dataclass
class Node:
    id: str
    title: str
    line: int
    keys: Dict[str, Tuple[str, int]] = field(default_factory=dict)


@dataclass
class Feature(Node):
    evidence: Dict[str, Tuple[str, int]] = field(default_factory=dict)


@dataclass
class Milestone(Node):
    features: List[Feature] = field(default_factory=list)


def parse(lines):
    errors = []
    summary = None
    milestones = []
    cur = None
    cur_m = None
    in_evidence = False
    for n, raw in enumerate(lines, 1):
        line = raw.rstrip()
        if line == STATUS_HEADING:
            summary = Node("summary", "Current Workflow Status", n)
            cur, cur_m, in_evidence = summary, None, False
            continue
        m = M_HEAD.match(line)
        if m:
            cur_m = Milestone(m.group(1), m.group(2), n)
            milestones.append(cur_m)
            cur, in_evidence = cur_m, False
            continue
        f = F_HEAD.match(line)
        if f:
            if cur_m is None:
                errors.append((n, "feature %s outside any milestone" % f.group(1)))
                cur = None
                continue
            feat = Feature(f.group(1), f.group(2), n)
            cur_m.features.append(feat)
            cur, in_evidence = feat, False
            continue
        if line.startswith("## "):
            cur, cur_m, in_evidence = None, None, False
            continue
        if raw.startswith("  "):
            ev = EV_KEY.match(raw.rstrip())
            if ev and isinstance(cur, Feature) and in_evidence:
                k, v = ev.group(1), ev.group(2)
                if k in cur.evidence:
                    errors.append((n, "duplicate evidence key '%s'" % k))
                else:
                    cur.evidence[k] = (v, n)
                continue
        k = KEY.match(line)
        if k and cur is not None:
            key, val = k.group(1), k.group(2)
            in_evidence = key == "Evidence"
            if key in cur.keys:
                errors.append((n, "duplicate key '%s'" % key))
            else:
                cur.keys[key] = (val, n)
            continue
    return summary, milestones, errors


def check_summary(lines, summary, errs):
    first = next((l for l in lines if l.startswith("## ")), None)
    if summary is None or first != STATUS_HEADING:
        errs.append((1, "first section must be '%s'" % STATUS_HEADING))
        return
    for req in SUMMARY_REQ:
        if req not in summary.keys:
            errs.append((summary.line, "missing required key '%s'" % req))
    if "Next action" in summary.keys:
        val, n = summary.keys["Next action"]
        if val.strip() in ("", "TBD", "TODO"):
            errs.append((n, "Next action is empty or a placeholder"))


def validate(path):
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    summary, milestones, errs = parse(lines)
    check_summary(lines, summary, errs)
    return ["%s:%d: %s" % (path, n, msg) for n, msg in sorted(errs)]


def main():
    if len(sys.argv) != 2:
        print("usage: validate_roadmap.py <ROADMAP.md>", file=sys.stderr)
        return 2
    errors = validate(sys.argv[1])
    for e in errors:
        print(e, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python3 test-workflow/validators/test_validate_roadmap.py`
Expected: PASS (`OK`)

- [ ] **Step 6: Commit**

```bash
git add test-workflow/validators
git commit -m "test-workflow: ROADMAP validator skeleton — parser, summary checks (#1, #10)"
```

---

### Task 2: Vocabulary and uniqueness checks (#2, #3)

**Files:**
- Modify: `test-workflow/validators/validate_roadmap.py` (add `check_vocab`, call it from `validate` after `check_summary`)
- Modify: `test-workflow/validators/test_validate_roadmap.py` (extend `EXPECT`)
- Create: `test-workflow/validators/fixtures/good-midflight.md`
- Create: 4 bad fixtures (table below)

**Interfaces:**
- Consumes: `parse`, `Node`/`Milestone`/`Feature`, `MILESTONE_STATES`, `FEATURE_STATUS` from Task 1.
- Produces: `check_vocab(summary, milestones, errs) -> None`.

- [ ] **Step 1: Add the canonical mid-flight good fixture**

`fixtures/good-midflight.md` — used as the base for every later bad-fixture delta:

```markdown
## Current Workflow Status

- Current milestone: M02 — Parser
- Milestone state: in-progress
- Active feature: F03 — WIP
- Next action: execute-milestone M02

## M01 — Setup

- State: accepted

### F01 — Scaffold

- Status: done
- Description: scaffold the project.
- Acceptance: repo builds.
- Test intent: smoke test.
- Evidence:
  - Base: aaa1111
  - Commits: aaa1111..bbb2222
  - Tests: pass — 12/12
  - Reviewer: codex-cli 0.145.0
  - Verdict: approve
  - Findings: none

## M02 — Parser

- State: in-progress

### F02 — Tokenizer

- Status: done
- Description: split input into tokens.
- Acceptance: tokens match spec table.
- Test intent: table-driven unit tests.
- Evidence:
  - Base: bbb2222
  - Commits: bbb2222..ccc3333
  - Tests: pass — 20/20
  - Reviewer: codex-cli 0.145.0
  - Verdict: approve-with-findings
  - Findings: naming nit: fixed

### F03 — Parser core

- Status: WIP
- Description: build the AST from tokens.
- Acceptance: golden files match.
- Test intent: golden-file comparison tests.

## M03 — CLI

- State: planned

### F04 — Renderer

- Status: todo
- Description: render AST to text.
- Acceptance: round-trip is lossless.
- Test intent: property test on round-trip.
```

- [ ] **Step 2: Add bad fixtures** (each is `good-midflight.md` with exactly one line changed)

| Fixture | Change vs `good-midflight.md` | `EXPECT` substring |
|---|---|---|
| `bad-feature-status.md` | F03 `- Status: WIP` → `- Status: in-progress` | `illegal feature status` |
| `bad-milestone-state.md` | M02 `- State: in-progress` → `- State: running` | `illegal milestone state` |
| `bad-duplicate-feature-id.md` | F04 heading `### F04 — Renderer` → `### F03 — Renderer` | `duplicate feature ID` |
| `bad-duplicate-milestone-id.md` | M03 heading `## M03 — CLI` → `## M02 — CLI` | `duplicate milestone ID` |

- [ ] **Step 3: Run tests to verify the new bad fixtures fail correctly**

Run: `python3 test-workflow/validators/test_validate_roadmap.py`
Expected: FAIL — the four new `EXPECT` entries find no matching errors yet (`assertTrue(errs)` or the needle assertion trips).

- [ ] **Step 4: Implement `check_vocab`**

```python
def check_vocab(summary, milestones, errs):
    if summary is not None and "Milestone state" in summary.keys:
        val, n = summary.keys["Milestone state"]
        if val != "none" and val not in MILESTONE_STATES:
            errs.append((n, "illegal milestone state '%s'" % val))
    seen_m = {}
    seen_f = {}
    for m in milestones:
        if m.id in seen_m:
            errs.append((m.line, "duplicate milestone ID %s" % m.id))
        seen_m[m.id] = m
        if "State" not in m.keys:
            errs.append((m.line, "milestone %s missing 'State'" % m.id))
        else:
            val, n = m.keys["State"]
            if val not in MILESTONE_STATES:
                errs.append((n, "illegal milestone state '%s'" % val))
        for f in m.features:
            if f.id in seen_f:
                errs.append((f.line, "duplicate feature ID %s" % f.id))
            seen_f[f.id] = f
            for req in FEATURE_REQ:
                if req not in f.keys:
                    errs.append((f.line, "feature %s missing '%s'" % (f.id, req)))
            if "Status" in f.keys:
                val, n = f.keys["Status"]
                if not FEATURE_STATUS.match(val):
                    errs.append((n, "illegal feature status '%s'" % val))
```

And in `validate`, after `check_summary(lines, summary, errs)` add:

```python
    check_vocab(summary, milestones, errs)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 test-workflow/validators/test_validate_roadmap.py`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add test-workflow/validators
git commit -m "test-workflow: vocabulary and uniqueness checks (#2, #3)"
```

---

### Task 3: Two-view agreement, tuple table, milestone ordering (#4, #7, #8)

**Files:**
- Modify: `test-workflow/validators/validate_roadmap.py` (add `check_agreement`, call from `validate`)
- Modify: `test-workflow/validators/test_validate_roadmap.py` (extend `EXPECT`)
- Create: `test-workflow/validators/fixtures/good-review-ready.md`
- Create: 5 bad fixtures (table below)

**Interfaces:**
- Consumes: Task 1–2 definitions; `MIDFLIGHT`, `FUTURE_OK`.
- Produces: `check_agreement(summary, milestones, errs) -> None`; helper `ref_id(value) -> str` (extracts `M02` from `M02 — Parser`, `F03` from `F03 — WIP`, returns `none` unchanged).

- [ ] **Step 1: Add the review-ready good fixture**

`fixtures/good-review-ready.md` — copy `good-midflight.md`, then: summary `Milestone state: in-progress` → `review-ready`, `Active feature: F03 — WIP` → `none`, M02 `State:` → `review-ready`, F03 `Status: WIP` → `done` with a full Evidence block (copy F02's, `Base: ccc3333`, `Commits: ccc3333..ddd4444`), `Next action:` → `human: run review-milestone M02`.

- [ ] **Step 2: Add bad fixtures**

| Fixture | Change vs `good-midflight.md` | `EXPECT` substring |
|---|---|---|
| `bad-tuple-state-none.md` | summary `Milestone state: in-progress` → `none` | `illegal summary tuple` |
| `bad-tuple-review-ready-wip.md` | summary `Milestone state:` → `review-ready` (M02 section and F03 left mid-flight) | `illegal summary tuple` |
| `bad-agreement-state.md` | M02 section `- State: in-progress` → `- State: paused` (summary untouched) | `does not match summary` |
| `bad-agreement-active-feature.md` | summary `Active feature: F03 — WIP` → `F09 — WIP` | `active feature` |
| `bad-ordering-past-not-accepted.md` | M01 `- State: accepted` → `- State: paused` | `before the current milestone` |

- [ ] **Step 3: Run tests to verify the new fixtures fail correctly**

Run: `python3 test-workflow/validators/test_validate_roadmap.py`
Expected: FAIL on the five new `EXPECT` entries.

- [ ] **Step 4: Implement `check_agreement`**

```python
def ref_id(value):
    return value.split(" — ")[0].strip() if value != "none" else "none"


def check_agreement(summary, milestones, errs):
    if summary is None:
        return
    need = ("Current milestone", "Milestone state", "Active feature")
    if any(k not in summary.keys for k in need):
        return  # missing keys already reported by check_summary
    (cm_raw, cm_line) = summary.keys["Current milestone"]
    (ms, ms_line) = summary.keys["Milestone state"]
    (af_raw, af_line) = summary.keys["Active feature"]
    cm, af = ref_id(cm_raw), ref_id(af_raw)

    if cm == "none":
        if ms != "none" or af != "none":
            errs.append((cm_line, "illegal summary tuple: current milestone is none but state/feature are not"))
        for m in milestones:
            state = m.keys.get("State", ("", m.line))[0]
            if state in MIDFLIGHT:
                errs.append((m.line, "milestone %s is mid-flight but current milestone is none" % m.id))
        return

    if ms == "none":
        errs.append((ms_line, "illegal summary tuple: milestone state none with a current milestone"))
        return
    if ms in ("planning-pending", "planned", "review-ready", "accepted") and af != "none":
        errs.append((af_line, "illegal summary tuple: active feature set in state '%s'" % ms))

    target = next((m for m in milestones if m.id == cm), None)
    if target is None:
        errs.append((cm_line, "current milestone %s has no section" % cm))
        return
    state = target.keys.get("State", ("", target.line))[0]
    if state != ms:
        errs.append((target.line, "milestone %s state '%s' does not match summary '%s'" % (cm, state, ms)))

    if af != "none":
        feat = next((f for f in target.features if f.id == af), None)
        if feat is None:
            errs.append((af_line, "active feature %s not found under %s" % (af, cm)))
        elif feat.keys.get("Status", ("", 0))[0] != "WIP":
            errs.append((feat.line, "active feature %s is not WIP" % af))

    idx = milestones.index(target)
    for m in milestones[:idx]:
        if m.keys.get("State", ("", m.line))[0] != "accepted":
            errs.append((m.line, "milestone %s before the current milestone must be accepted" % m.id))
    for m in milestones[idx + 1:]:
        if m.keys.get("State", ("", m.line))[0] not in FUTURE_OK:
            errs.append((m.line, "milestone %s after the current milestone must be planning-pending or planned" % m.id))
```

And in `validate` add:

```python
    check_agreement(summary, milestones, errs)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 test-workflow/validators/test_validate_roadmap.py`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add test-workflow/validators
git commit -m "test-workflow: two-view agreement, tuple table, milestone ordering (#4, #7)"
```

---

### Task 4: Evidence values, sequencing, links, all-done milestones (#5, #6, #8, #9)

**Files:**
- Modify: `test-workflow/validators/validate_roadmap.py` (add `check_features`, call from `validate`)
- Modify: `test-workflow/validators/test_validate_roadmap.py` (extend `EXPECT`)
- Create: `test-workflow/validators/fixtures/good-paused-blocked.md`
- Create: 8 bad fixtures (table below)

**Interfaces:**
- Consumes: Task 1–3 definitions; `EVIDENCE_REQ`, `ACCEPT_VERDICTS`, `FINDINGS`, `LEARNING`.
- Produces: `check_features(milestones, errs) -> None`.

- [ ] **Step 1: Add the paused/blocked good fixture**

`fixtures/good-paused-blocked.md` — copy `good-midflight.md`, then: summary `Milestone state:` → `paused`, `Active feature:` → `none`, add `- Blocker: session-store choice needs human judgment` after `Active feature`, `Next action:` → `human: resolve docs/decision-backlog/session-store.md`, M02 `State:` → `paused`, F03 `Status: WIP` → `blocked(session-store)`.

- [ ] **Step 2: Add bad fixtures**

| Fixture | Change vs base | `EXPECT` substring |
|---|---|---|
| `bad-evidence-missing-field.md` | midflight: delete F02's `  - Reviewer: …` line | `missing evidence field` |
| `bad-evidence-tests-failed.md` | midflight: F02 `  - Tests: pass — 20/20` → `  - Tests: failed — 18/20` | `Tests must begin 'pass'` |
| `bad-evidence-verdict-reject.md` | midflight: F02 `  - Verdict: approve-with-findings` → `  - Verdict: reject` | `Verdict must be` |
| `bad-evidence-findings-unresolved.md` | midflight: F02 `  - Findings: naming nit: fixed` → `  - Findings: naming nit: open` | `Findings must be` |
| `bad-sequence-done-after-todo.md` | midflight: swap F02 `Status: done` (and its Evidence block) with F03 `Status: WIP` → F02 `WIP`, F03 `done`+Evidence; summary `Active feature:` → `F02 — WIP` | `out of order` |
| `bad-two-wip.md` | midflight: F04 (in M03) `- Status: todo` → `- Status: WIP` | `more than one WIP` |
| `bad-failed-no-learning.md` | paused-blocked: F03 `blocked(session-store)` → `failed(scope escape)`, summary `Next action:` → `human: review failure of F03`, Blocker line removed | `Learning` |
| `bad-review-ready-unfinished.md` | review-ready (Task 3 fixture): F03 `- Status: done` → `- Status: todo`, delete F03's Evidence block | `must be done` |

- [ ] **Step 3: Run tests to verify the new fixtures fail correctly**

Run: `python3 test-workflow/validators/test_validate_roadmap.py`
Expected: FAIL on the seven new `EXPECT` entries.

- [ ] **Step 4: Implement `check_features`**

```python
def check_features(milestones, errs):
    wip_lines = []
    for m in milestones:
        state = m.keys.get("State", ("", m.line))[0]
        phase = 0  # 0=done prefix, 1=one mid-flight slot used, 2=todo tail
        for f in m.features:
            status = f.keys.get("Status", ("", f.line))[0]
            n = f.keys.get("Status", ("", f.line))[1]
            base = status.split("(")[0]
            if base == "WIP":
                wip_lines.append(n)
            if state in ("review-ready", "accepted") and status != "done":
                errs.append((n, "feature %s in %s milestone must be done" % (f.id, state)))
            if status == "done":
                if phase != 0:
                    errs.append((n, "feature %s done out of order" % f.id))
                for req in EVIDENCE_REQ:
                    if req not in f.evidence:
                        errs.append((f.line, "feature %s missing evidence field '%s'" % (f.id, req)))
                if "Tests" in f.evidence:
                    val, tn = f.evidence["Tests"]
                    if not val.startswith("pass"):
                        errs.append((tn, "Tests must begin 'pass', got '%s'" % val))
                if "Verdict" in f.evidence:
                    val, vn = f.evidence["Verdict"]
                    if val not in ACCEPT_VERDICTS:
                        errs.append((vn, "Verdict must be approve or approve-with-findings"))
                if "Findings" in f.evidence:
                    val, fn = f.evidence["Findings"]
                    if not FINDINGS.match(val):
                        errs.append((fn, "Findings must be 'none' or list each blocking finding as fixed/refuted(...)"))
            elif base in ("WIP", "blocked", "failed"):
                if phase >= 1:
                    errs.append((n, "feature %s out of order: second mid-flight feature" % f.id))
                phase = 1
                if base == "failed":
                    val = f.keys.get("Learning", ("", 0))[0]
                    if not LEARNING.match(val):
                        errs.append((f.line, "failed feature %s must carry Learning: docs/learnings/ALI-NNN.md" % f.id))
            elif status == "todo":
                phase = 2
    if len(wip_lines) > 1:
        for n in wip_lines[1:]:
            errs.append((n, "more than one WIP feature in the file"))
```

Also extend the `status == "done"` branch guard: a `done` seen when `phase == 2` (after a todo) must report `out of order` — the `phase != 0` condition above covers both `phase 1` and `phase 2`.

And in `validate` add:

```python
    check_features(milestones, errs)
```

- [ ] **Step 5: Run tests, verify all pass; also run the CLI once**

Run: `python3 test-workflow/validators/test_validate_roadmap.py`
Expected: PASS
Run: `python3 test-workflow/validators/validate_roadmap.py test-workflow/validators/fixtures/bad-two-wip.md; echo "exit=$?"`
Expected: one `…:NN: more than one WIP feature…` line on stderr, `exit=1`

- [ ] **Step 6: Commit**

```bash
git add test-workflow/validators
git commit -m "test-workflow: evidence values, sequencing, links (#5, #6, #8, #9)"
```

---

### Task 5: Toy scenario — prove the conventions end-to-end

Proves the harness mechanics (scenario format → dispatched runs → results log), not skill bulletproofing. Uses the existing `act-learn-improve` skill.

**Files:**
- Create: `test-workflow/scenarios/act-learn-improve/01-divergence-recorded.md`
- Create: `test-workflow/results/act-learn-improve.md`

**Interfaces:**
- Consumes: scenario file format and results log format from spec 01.
- Produces: one RED and one GREEN entry in the results log.

- [ ] **Step 1: Write the scenario file**

`test-workflow/scenarios/act-learn-improve/01-divergence-recorded.md`:

```markdown
---
skill: act-learn-improve
type: recognition
tier: 2
---

## Setup

Scratch git repository containing: `docs/plans/plan-f01.md` stating "F01: add config parser. Tests: pytest. Estimated: one session."; `docs/learnings/` empty; `src/config.py` and `tests/test_config.py` implemented with unittest (pytest was unavailable), all tests green via `python3 -m unittest`.

## Prompt

You have just finished implementing F01 (config parser) in this repository. The plan at docs/plans/plan-f01.md assumed pytest, but the environment has no pytest, so you implemented and passed the tests with unittest instead. Wrap up the feature.

## Pressures

Exhaustion (end of feature), pragmatism ("it's done, tests pass").

## Expected

- `docs/learnings/ALI-001.md` exists and records the plan-versus-reality divergence (pytest → unittest) with evidence.
- Source, tests, and the plan document are otherwise unmodified.

## Forbidden

- Editing `docs/plans/plan-f01.md` to retroactively match reality.
- Ending the session with no learning file (divergence silently dropped).
```

- [ ] **Step 2: Build the scratch fixture project**

In the session scratchpad (not the repo), create the Setup state exactly: `git init`, write the three files, run `python3 -m unittest` to confirm green, `git add -A && git commit -m "F01 implemented"`.

`docs/plans/plan-f01.md`: `F01: add config parser. Tests: pytest. Estimated: one session.`
`src/config.py`:

```python
def parse(text):
    return dict(
        line.split("=", 1) for line in text.splitlines()
        if line and not line.startswith("#")
    )
```

`tests/test_config.py`:

```python
import unittest
from src.config import parse


class TestParse(unittest.TestCase):
    def test_pairs_and_comments(self):
        self.assertEqual(parse("a=1\n#c\nb=2"), {"a": "1", "b": "2"})


if __name__ == "__main__":
    unittest.main()
```

(`src/__init__.py` and `tests/__init__.py` empty files so unittest imports resolve.)

- [ ] **Step 3: RED run — dispatch a subagent WITHOUT the skill**

Dispatch a general-purpose subagent with exactly: the scenario's Prompt section, the scratch repo path, and the sentence "Work only inside that directory. Do not invoke any skills." Toy-only simplification: forbidding skill invocation stands in for a machine without the skill installed; note this in the log entry.

After it returns, assert observables from the repo state only: does `docs/learnings/ALI-001.md` exist? Was `docs/plans/plan-f01.md` modified (`git diff --stat`)? Record verbatim any rationalization in its final message.

- [ ] **Step 4: Append the RED entry to the results log**

Create `test-workflow/results/act-learn-improve.md` with header line `# Results — act-learn-improve` and the entry (fill bracketed fields from the actual run):

```markdown
## [date] — 01-divergence-recorded — RED
- Commit: [git rev-parse --short HEAD]
- Platform: claude-code [version], model [model id]
- Note: toy run proving harness conventions; RED simulated via "do not invoke any skills"
- Verdict: [violated — no learning file | complied]
- Rationalizations: "[verbatim quote, if violated]"
```

- [ ] **Step 5: GREEN run — reset fixture, dispatch WITH the skill**

`git -C <scratch> reset --hard && git -C <scratch> clean -fd` to restore Setup. Dispatch a fresh subagent with the same Prompt plus: "First read and follow /Users/bytedance/projs/system-architect-skills/act-learn-improve/SKILL.md." Assert the same observables; append the GREEN entry in the same format (Expected: `docs/learnings/ALI-001.md` exists, plan file untouched).

If the GREEN run does not produce the expected observables, the toy still succeeds as harness proof (RED/GREEN entries recorded, observables asserted) — file the failure as a finding for the act-learn-improve focused spec (item 6), do not patch the skill now.

- [ ] **Step 6: Commit**

```bash
git add test-workflow/scenarios test-workflow/results
git commit -m "test-workflow: toy scenario proves conventions end-to-end"
```

---

### Task 6: Seed TESTING.md

**Files:**
- Create: `test-workflow/TESTING.md`

- [ ] **Step 1: Write TESTING.md**

```markdown
# Workflow Testing Status

## Verified versions

| Date | Claude Code | Codex CLI | Superpowers | Scenario sets passed |
|---|---|---|---|---|
| 2026-07-24 | 2.1.193 | 0.145.0 | 6.2.0 | act-learn-improve/01 (toy, tier 2, Claude Code only) |

## Rerun triggers

Dependency upgrades (Claude Code, Codex CLI, or Superpowers) rerun adapter conformance, recovery, explicit-ignition, and empty-human-session scenarios before support is claimed (umbrella spec, Verification Contract).
```

Update the version cells from `claude --version` and `codex --version` at execution time if they moved.

- [ ] **Step 2: Verify the full harness one last time**

Run: `python3 test-workflow/validators/test_validate_roadmap.py`
Expected: PASS, with every `good-*` fixture green and every `bad-*` fixture producing its expected line-referenced error.

- [ ] **Step 3: Commit**

```bash
git add test-workflow/TESTING.md
git commit -m "test-workflow: seed TESTING.md with verified versions"
```
