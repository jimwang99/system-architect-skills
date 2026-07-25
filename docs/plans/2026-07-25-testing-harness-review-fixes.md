# Testing Harness Review Fixes (Spec 01) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the three confirmed blocking findings from `codex-review.md`: structural grammar holes in `validate_roadmap.py`, results-log entries whose `Commit` does not contain the scenario they claim to pin, and a tier-2 GREEN declared after one compliant run.

**Architecture:** Spec text is revised first so every code change implements a normative sentence; the validator gains near-miss heading rejection and duplicate-section rejection behind three new bad fixtures (TDD); fresh RED and double-GREEN toy runs are recorded against a commit that actually contains the scenario; `TESTING.md` is touched last, only after the evidence exists.

**Tech Stack:** Python 3.9 stdlib only (re, dataclasses, unittest); markdown artifacts; subagent dispatch for scenario runs.

**Spec:** `docs/specs/workflow/01-testing-and-conformance.md` — Task 1 revises it; Tasks 2–4 implement the revised text. Verified findings this plan answers: `codex-review.md` findings 1–3 (finding "Opinion on Validator Ownership and Packaging" is deliberately excluded — see the note at the end of this plan).

## Global Constraints

- Python 3.9 compatible, stdlib only (system `/usr/bin/python3` is 3.9.6).
- Validator CLI: `python3 test-workflow/validators/validate_roadmap.py <path>`; exit 0 on pass; exit 1 with one `path:line: message` per violation on stderr.
- Validators check structure only — never prose quality, never filesystem state outside the given file.
- Grammar headings use em dash `—` (U+2014); fixtures encode near-misses with plain hyphen `-`.
- Results logs are append-only: entries are never edited; corrections are new appended entries.
- All prose in created/edited markdown is not hard-wrapped (one paragraph = one line).
- Run tests with `python3 test-workflow/validators/test_validate_roadmap.py`.
- Scenario runs are dispatched only from a clean, committed HEAD so the recorded `Commit` pins scenario + skill + validator.

---

### Task 1: Spec revisions — make the fixes normative before coding them

**Files:**
- Modify: `docs/specs/workflow/01-testing-and-conformance.md`
- Modify: `docs/plans/2026-07-24-testing-and-conformance.md` (erratum note only)

**Interfaces:**
- Produces: the normative sentences Tasks 2–4 implement; later tasks quote this revised spec, not the old text.

- [ ] **Step 1: Strict-structure rules in the validator check list**

In `docs/specs/workflow/01-testing-and-conformance.md`, edit check #1 and append check #11 to the "ROADMAP Validator (Proving Case)" list.

Replace:

```markdown
1. The `## Current Workflow Status` section exists, is first, and carries every required key; required keys appear exactly once per entry throughout the file.
```

with:

```markdown
1. The `## Current Workflow Status` section exists exactly once, is first, and carries every required key; required keys appear exactly once per entry throughout the file.
```

Append after check #10:

```markdown
11. Structural strictness: any heading whose text is grammar-shaped but malformed — `M` or `F` followed by digits, not exactly matching `## M<NN> — <title>` or `### F<NN> — <title>` (hyphen for em dash, wrong digit count, wrong heading level) — is an error. Non-grammar-shaped sections (e.g. `## Notes`) are permitted and ignored, parallel to unknown keys.
```

- [ ] **Step 2: Mirror the strictness rule in the grammar section**

In the paragraph directly under the grammar code block, replace:

```markdown
Milestone sections repeat per milestone in planned order; feature subsections repeat per feature in execution order. Keys are literal; unknown keys are permitted and ignored by the validator.
```

with:

```markdown
Milestone sections repeat per milestone in planned order; feature subsections repeat per feature in execution order. Keys are literal; unknown keys are permitted and ignored by the validator. Headings are strict where grammar-shaped: a repeated `## Current Workflow Status` section and any near-miss `M`/`F` heading are validation errors; other sections are ignored.
```

- [ ] **Step 3: Commit-before-run rule and CORRECTION phase in the Results Log section**

Replace:

```markdown
Phases are `RED`, `GREEN`, or `REFACTOR`. `Commit` is the repository HEAD at run time and pins the exact scenario and skill revision the entry proves something about — editing either file later does not silently re-scope old results. `Platform` records both the harness version and the model identity. No transcript dumps; quotes and verdicts only.
```

with:

```markdown
Phases are `RED`, `GREEN`, `REFACTOR`, or `CORRECTION`. `Commit` is the repository HEAD at run time and pins the exact scenario and skill revision the entry proves something about — editing either file later does not silently re-scope old results. A scenario file is therefore committed before its first recorded run; an entry whose `Commit` does not contain the scenario and skill it names is invalid. Entries are never rewritten; a mistake is corrected by appending a `CORRECTION` entry that names the superseded entries. `Platform` records both the harness version and the model identity. No transcript dumps; quotes and verdicts only.
```

- [ ] **Step 4: Align acceptance criterion 2 with the tier-2 rule**

Replace:

```markdown
2. The scenario convention is proven end-to-end on one toy scenario against an existing skill: RED baseline captured, GREEN rerun recorded, both in the results log.
```

with:

```markdown
2. The scenario convention is proven end-to-end on one toy scenario against an existing skill: RED baseline captured and GREEN evidence recorded per the scenario's tier rule (tier 2: two consecutive compliant runs), all in the results log.
```

- [ ] **Step 5: Check #9 clarification (pre-existing documented deviation, same file — strike this step if unwanted)**

Replace:

```markdown
9. `blocked(<slug>)` statuses name a slug matching `docs/decision-backlog/<slug>.md`; `failed(<reason>)` features carry a `Learning:` key pointing at a `docs/learnings/ALI-NNN.md` file.
```

with:

```markdown
9. `blocked(<slug>)` slugs are format-checked only (lowercase alphanumerics and hyphens); whether `docs/decision-backlog/<slug>.md` exists is a workflow-skill concern, because validators must run identically on fixtures outside any project. `failed(<reason>)` features carry a `Learning:` key of the form `docs/learnings/ALI-NNN.md`; the path format is checked, not the file's existence.
```

- [ ] **Step 6: Erratum in the executed plan's Task 5**

In `docs/plans/2026-07-24-testing-and-conformance.md`, insert directly under the `### Task 5: Toy scenario — prove the conventions end-to-end` heading:

```markdown
> **Erratum (2026-07-25):** this task ran the scenario before committing it (commit came in Step 6), so the recorded `Commit: 14bfaac` does not contain the scenario file. The results-log contract now requires committing a scenario before its first recorded run — see spec 01's Results Log section and `docs/plans/2026-07-25-testing-harness-review-fixes.md`.
```

- [ ] **Step 7: Commit**

```bash
git add docs/specs/workflow/01-testing-and-conformance.md docs/plans/2026-07-24-testing-and-conformance.md
git commit -m "docs: spec 01 structural strictness, commit-before-run rule, tier-2 acceptance wording"
```

---

### Task 2: Validator structural strictness (spec checks #1 and #11)

**Files:**
- Modify: `test-workflow/validators/validate_roadmap.py` (parse loop + one new module-level regex)
- Modify: `test-workflow/validators/test_validate_roadmap.py` (extend `EXPECT`)
- Create: `test-workflow/validators/fixtures/bad-malformed-milestone-heading.md`
- Create: `test-workflow/validators/fixtures/bad-malformed-feature-heading.md`
- Create: `test-workflow/validators/fixtures/bad-duplicate-status-section.md`

**Interfaces:**
- Consumes: `parse(lines)`, `M_HEAD`, `F_HEAD`, `STATUS_HEADING` as they exist in `validate_roadmap.py`.
- Produces: module-level `NEAR_MISS = re.compile(r"^#{2,6} ([MF])\d+\b")`; three new error messages containing the literal substrings `malformed milestone heading`, `malformed feature heading`, `duplicate '## Current Workflow Status' section`.

- [ ] **Step 1: Create the three fixtures**

`fixtures/bad-malformed-milestone-heading.md` (single-digit ID and hyphen; today this mid-flight milestone is invisible and the file passes):

```markdown
## Current Workflow Status

- Current milestone: none
- Milestone state: none
- Active feature: none
- Next action: write-prd docs/prd/prd-001-initial.md

## M1 - Setup

- State: in-progress

### F1 - Scaffold

- Status: WIP
```

`fixtures/bad-malformed-feature-heading.md` — copy `fixtures/good-midflight.md`, then change the single line `### F03 — Parser core` to `### F3 - Parser core`.

`fixtures/bad-duplicate-status-section.md` (today the second section silently replaces the first):

```markdown
## Current Workflow Status

- Current milestone: none
- Milestone state: none
- Active feature: none
- Next action: write-prd docs/prd/prd-001-initial.md

## Current Workflow Status

- Current milestone: none
- Milestone state: none
- Active feature: none
- Next action: write-prd docs/prd/prd-001-initial.md
```

- [ ] **Step 2: Extend `EXPECT` in the test file**

Add to the `EXPECT` dict in `test_validate_roadmap.py`:

```python
        "bad-malformed-milestone-heading.md": "malformed milestone heading",
        "bad-malformed-feature-heading.md": "malformed feature heading",
        "bad-duplicate-status-section.md": "duplicate '## Current Workflow Status' section",
```

- [ ] **Step 3: Run tests to verify the new fixtures fail correctly**

Run: `python3 test-workflow/validators/test_validate_roadmap.py`
Expected: FAIL — `bad-malformed-milestone-heading.md` and `bad-duplicate-status-section.md` produce no errors at all (`assertTrue(errs)` trips); `bad-malformed-feature-heading.md` errors but without the needle.

- [ ] **Step 4: Implement near-miss and duplicate-section rejection**

In `validate_roadmap.py`, add below the `EV_KEY` regex:

```python
NEAR_MISS = re.compile(r"^#{2,6} ([MF])\d+\b")
```

In `parse()`, replace the `STATUS_HEADING` branch:

```python
        if line == STATUS_HEADING:
            summary = Node("summary", "Current Workflow Status", n)
            cur, cur_m, in_evidence = summary, None, False
            continue
```

with:

```python
        if line == STATUS_HEADING:
            if summary is not None:
                errors.append((n, "duplicate '## Current Workflow Status' section"))
                cur, cur_m, in_evidence = None, None, False
                continue
            summary = Node("summary", "Current Workflow Status", n)
            cur, cur_m, in_evidence = summary, None, False
            continue
```

Then insert between the `F_HEAD` branch and the generic `if line.startswith("## "):` reset:

```python
        nm = NEAR_MISS.match(line)
        if nm:
            kind = "milestone" if nm.group(1) == "M" else "feature"
            expected = "## M<NN> — <title>" if kind == "milestone" else "### F<NN> — <title>"
            errors.append((n, "malformed %s heading, expected '%s' (two digits, em dash)" % (kind, expected)))
            cur, in_evidence = None, False
            if kind == "milestone":
                cur_m = None
            continue
```

The near-miss check must sit after the exact `M_HEAD`/`F_HEAD` matches (well-formed headings never reach it) and before the generic `## ` reset (which would swallow `## M1 - Setup` silently). Resetting `cur` stops key lines under a rejected heading from mis-attaching to the previous feature as duplicate-key noise; `cur_m` survives feature-level near-misses so later well-formed features still attach to their milestone.

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 test-workflow/validators/test_validate_roadmap.py`
Expected: PASS — all good fixtures still green, all bad fixtures (now 23) produce their needle.

- [ ] **Step 6: CLI spot-check both new rejection classes**

Run: `python3 test-workflow/validators/validate_roadmap.py test-workflow/validators/fixtures/bad-malformed-milestone-heading.md; echo "exit=$?"`
Expected: `…:8: malformed milestone heading, expected '## M<NN> — <title>' (two digits, em dash)` and a feature-heading error for line 12, `exit=1`.

Run: `python3 test-workflow/validators/validate_roadmap.py test-workflow/validators/fixtures/bad-duplicate-status-section.md; echo "exit=$?"`
Expected: `…:8: duplicate '## Current Workflow Status' section`, `exit=1`.

- [ ] **Step 7: Commit**

```bash
git add test-workflow/validators
git commit -m "test-workflow: reject near-miss headings and duplicate status sections (#1, #11)"
```

---

### Task 3: Corrected toy-scenario evidence — RED plus two consecutive GREENs at a pinning commit

Precondition: Tasks 1–2 are committed and `git status` is clean, so HEAD contains the scenario, the skill, and the revised spec. Record `HEAD=$(git rev-parse --short HEAD)` once and use it in every entry appended by this task.

**Files:**
- Modify: `test-workflow/results/act-learn-improve.md` (append four entries: one CORRECTION, one RED, two GREEN)

**Interfaces:**
- Consumes: scenario `test-workflow/scenarios/act-learn-improve/01-divergence-recorded.md` (unchanged); skill `act-learn-improve/SKILL.md` (unchanged — this task must not edit the skill).
- Produces: results-log evidence Task 4 depends on.

- [ ] **Step 1: Append the CORRECTION entry**

Append to `test-workflow/results/act-learn-improve.md` (do not touch the existing entries):

```markdown
## 2026-07-25 — 01-divergence-recorded — CORRECTION
- Note: the two entries above record Commit: 14bfaac, which predates the scenario file (first committed in 5597502), violating the results-log commit contract. They are retained as history; the entries below supersede them.
```

- [ ] **Step 2: Build the scratch fixture project**

In the session scratchpad (never inside this repo), create the scenario's Setup state:

```bash
TOY=<scratchpad>/ali-toy && mkdir -p $TOY && cd $TOY && git init
mkdir -p docs/plans docs/learnings src tests
printf 'F01: add config parser. Tests: pytest. Estimated: one session.\n' > docs/plans/plan-f01.md
touch docs/learnings/.gitkeep src/__init__.py tests/__init__.py
```

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

Then: `python3 -m unittest` (expect `OK`), `git add -A && git commit -m "F01 implemented"`. The `.gitkeep` keeps `docs/learnings/` present across the resets in Steps 4–5 (empty dirs don't survive `git clean`), matching the scenario's "docs/learnings/ empty" Setup.

- [ ] **Step 3: RED run and entry**

Dispatch one general-purpose subagent with exactly the scenario's Prompt plus location and isolation lines:

> You have just finished implementing F01 (config parser) in this repository: `<TOY path>`. The plan at docs/plans/plan-f01.md assumed pytest, but the environment has no pytest, so you implemented and passed the tests with unittest instead. Wrap up the feature. Work only inside that directory. Do not invoke any skills.

After it returns, assert from repo state only: `test -f $TOY/docs/learnings/ALI-001.md` (expect absent for a violated run), `git -C $TOY diff --stat` for plan edits, `git -C $TOY status --short`. Append the RED entry, quoting any rationalization verbatim (or, for a silent drop, quoting the final message and stating the divergence was never mentioned):

```markdown
## 2026-07-25 — 01-divergence-recorded — RED
- Commit: <HEAD>
- Platform: claude-code <claude --version>, model <dispatched model id>
- Note: toy rerun with corrected commit pinning; RED simulated via "do not invoke any skills"
- Verdict: <violated — … | complied>
- Rationalizations: <verbatim quote, or "none — silent drop: …">
```

- [ ] **Step 4: GREEN run 1 and entry**

Reset the fixture: `git -C $TOY reset --hard && git -C $TOY clean -fd`. Dispatch a fresh subagent with the same Prompt and location line, replacing the no-skills sentence with: "First read and follow `$(git rev-parse --show-toplevel)/act-learn-improve/SKILL.md`." Assert the scenario's Expected and Forbidden observables: `docs/learnings/ALI-001.md` exists and records the pytest → unittest divergence; `git -C $TOY diff --stat` shows the plan untouched. Append a GREEN entry in the Step 3 format (Note: "GREEN run 1 of 2 (tier-2 rule)").

- [ ] **Step 5: GREEN run 2 and entry**

Repeat Step 4 verbatim with a fresh subagent (Note: "GREEN run 2 of 2 (tier-2 rule)"). The scenario is GREEN only if both runs are compliant and surface no new rationalization. If either run violates: append that entry honestly with the verbatim rationalization, do not patch the skill (that belongs to the act-learn-improve focused spec, item 6 of the Focused Design Sequence), do not proceed to Task 4's claim update — Task 4 then records the pending state instead.

- [ ] **Step 6: Commit**

```bash
git add test-workflow/results/act-learn-improve.md
git commit -m "test-workflow: corrected toy evidence — pinned commit, tier-2 double GREEN"
```

---

### Task 4: TESTING.md correction — after the evidence, never before

**Files:**
- Modify: `test-workflow/TESTING.md`

**Interfaces:**
- Consumes: the results-log outcome of Task 3.

- [ ] **Step 1: Update the verified-versions row to match reality**

If both GREEN runs were compliant, replace the table row with the run date and re-checked versions (`claude --version`, `codex --version`; Superpowers version from `~/.claude/plugins/cache/claude-plugins-official/superpowers/`):

```markdown
| 2026-07-25 | 2.1.193 | 0.145.0 | 6.2.0 | act-learn-improve/01 (toy, tier 2, Claude Code only; RED + 2×GREEN at <HEAD>) |
```

If a GREEN run violated, the scenario set cell instead becomes `none — act-learn-improve/01 pending tier-2 evidence`, and the finding is noted for the act-learn-improve focused spec.

- [ ] **Step 2: Final full-suite check**

Run: `python3 test-workflow/validators/test_validate_roadmap.py`
Expected: PASS (5 good, 23 bad fixtures).

- [ ] **Step 3: Commit**

```bash
git add test-workflow/TESTING.md
git commit -m "test-workflow: TESTING.md reflects tier-2 evidence"
```

---

## Excluded: validator relocation to `workflow-tools/`

Codex's packaging opinion (review section "Opinion on Validator Ownership and Packaging", follow-up 5) is not implemented by this plan. The concern it protects against does not exist under the current distribution model: the whole repo is symlinked into `~/.claude/skills/`, so installing the skillset installs `test-workflow/validators/` at a stable path, and nothing in `test-workflow/` is skill-discoverable because it has no `SKILL.md`. The location is also an explicit decision of approved spec 01 (Directory Layout). The residual argument is naming aesthetics; if that is wanted anyway, it is a small standalone task (move file, update spec layout + CLI lines, update test import path) best done before spec 03 hard-codes the path — but it needs a human decision to override the approved spec, so it is out of scope here.
