# review-milestone (Spec 08) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement spec 08 (`docs/specs/workflow/08-review-milestone.md`): the review-record validator, the review-milestone skill certified through its five-scenario suite, and the spec-07 hand-back erratum.

**Architecture:** Validator + fixtures first; RED scenarios against no skill; SKILL.md + GREEN; errata + gate. The review record is one append-only file per milestone with Verdict-terminated passes; the validator applies completeness rules to the last pass only.

**Tech Stack:** stdlib Python 3.9, unittest, markdown, subagent runs, existing review stubs.

## Global Constraints

- Record grammar (spec 08 Decision 1): file `docs/reviews/milestone-<NNN>.md`; H1 `# Review: MS-NNN — <title>` (number matches filename); sweep sections `## Sweep: <item>` with item ∈ (learnings, adr-audit, backlog-triage, integration-review, three-c, demo) in that fixed order within a pass; findings `- F<K>: <text>`, each followed by its own `- Disposition:` line drawn from `fixed | refuted(<evidence>) | fix-feature(FEAT-NNN) | accepted-known-issue(<rationale>) | skipped(<rationale>)`; every sweep section ends with a `- Disposition:` line (item-level line: non-empty free text); `## Verdict` with exactly one `- Verdict: accept | remediate` and a non-empty `- Date:`; a Verdict-terminated block is one pass; content after a Verdict must begin a new pass starting at `## Sweep: learnings`; nothing but a new pass or EOF after a Verdict; a trailing pass without a Verdict is valid mid-review but its sections must be an in-order prefix of the fixed list; in a Verdict-terminated pass all six items present, every finding dispositioned, and `fix-feature(...)` dispositions are illegal when that pass's verdict is `accept`; fences opaque.
- Validator conventions (spec 01): `path:line: message` stderr, exit 0/1/2, stdlib, hermetic, fence-aware.
- Skill authority (Decisions 5–6): `disable-model-invocation: true`; literal-token guard (spec-07 certified form; MS-NNN inferable only when exactly one milestone is `review-ready`); sole writer of ALI `Status: approved`, of the `accepted` transition, and of the merge; every ROADMAP-touching commit passes both ROADMAP tools; flips gated by `validate_learning.py`; ADR acceptance via write-adr's lifecycle.
- Sweep order and skip rule (Decision 2): `[H]` items skip ONLY on explicit human instruction recorded as `skipped(<their words>)`; the agent never self-skips.
- Accept/remediate mechanics (Decision 3) and the deferral valve (Decision 4) verbatim from the spec.
- Iron law ordering; RED neutral-path tools; discipline scenarios 3+ pressures; append-only logs; one-paragraph-one-line markdown; commit trailer `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.

## File Structure

- `review-milestone/scripts/validate_review.py`, `test-workflow/fixtures/review/{good,bad}/...`, `test-workflow/tests/test_validate_review.py` — Task 1.
- `test-workflow/scenarios/review-milestone/01..05-*.md`, `test-workflow/results/review-milestone.md` — Tasks 2–3.
- `review-milestone/SKILL.md` — Task 3.
- `docs/specs/workflow/07-execute-milestone.md` (one erratum line), `test-workflow/TESTING.md` — Task 4.

---

### Task 1: validate_review.py + fixtures + tests

**Files:**
- Create: `review-milestone/scripts/validate_review.py`
- Create: `test-workflow/fixtures/review/good/{milestone-001.md (×5 variants, see table)}` and `test-workflow/fixtures/review/bad/<class>/milestone-001.md` (10 classes)
- Test: `test-workflow/tests/test_validate_review.py`

**Interfaces:**
- Produces: CLI `python3 review-milestone/scripts/validate_review.py <path>` — Tasks 2–3 gate scenario records on it.

- [ ] **Step 1: Write the failing test**

`test-workflow/tests/test_validate_review.py`:

```python
#!/usr/bin/env python3
import os, subprocess, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "..", "..", "review-milestone", "scripts", "validate_review.py")
FIX = os.path.join(HERE, "..", "fixtures", "review")

def run(path):
    return subprocess.run([sys.executable, TOOL, path], capture_output=True, text=True)

class TestGood(unittest.TestCase):
    def test_good_fixtures_pass(self):
        good = os.path.join(FIX, "good")
        for d in sorted(os.listdir(good)):
            p = os.path.join(good, d)
            for name in sorted(os.listdir(p)):
                if name.endswith(".md"):
                    with self.subTest(d):
                        r = run(os.path.join(p, name))
                        self.assertEqual(r.returncode, 0, "%s: %s" % (d, r.stderr))

class TestBad(unittest.TestCase):
    def test_bad_fixtures_fail_with_location(self):
        bad = os.path.join(FIX, "bad")
        for d in sorted(os.listdir(bad)):
            p = os.path.join(bad, d)
            for name in sorted(os.listdir(p)):
                if name.endswith(".md"):
                    with self.subTest(d):
                        r = run(os.path.join(p, name))
                        self.assertEqual(r.returncode, 1, "%s: exit=%d\n%s" % (d, r.returncode, r.stderr))
                        self.assertRegex(r.stderr, r"\.md:\d+: ")

class TestCli(unittest.TestCase):
    def test_missing_arg_exits_2(self):
        r = subprocess.run([sys.executable, TOOL], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)

    def test_unreadable_exits_2(self):
        r = run(os.path.join(FIX, "no-such.md"))
        self.assertEqual(r.returncode, 2)

if __name__ == "__main__":
    unittest.main()
```

(Good fixtures live one per subdirectory — `good/mid-review/milestone-001.md` etc. — so filename-based checks stay valid while variants coexist.)

- [ ] **Step 2: Run to verify it fails.**

- [ ] **Step 3: Write the tool**

`review-milestone/scripts/validate_review.py`:

```python
#!/usr/bin/env python3
"""Validate a docs/reviews/milestone-NNN.md review record against spec 08.

Stdlib only, Python 3.9+. Exit 0 pass; 1 with "path:line: message" per
violation; 2 on usage error or unreadable file. A trailing pass without a
Verdict is valid mid-review; Verdict-terminated passes must be complete.
"""
import os
import re
import sys

FILENAME = re.compile(r"^milestone-([0-9]{3})\.md$")
H1 = re.compile(r"^# Review: MS-([0-9]{3}) — (.+)$")
SWEEP = re.compile(r"^## Sweep: ([a-z-]+)$")
VERDICT_HEAD = "## Verdict"
FINDING = re.compile(r"^- F([0-9]+): (.+)$")
DISPO = re.compile(r"^- Disposition: ?(.*)$")
FINDING_DISPO = re.compile(
    r"^(fixed|refuted\(.+\)|fix-feature\(FEAT-[0-9]{3}\)|accepted-known-issue\(.+\)|skipped\(.+\))$")
VERDICT_LINE = re.compile(r"^- Verdict: (accept|remediate)$")
DATE_LINE = re.compile(r"^- Date: ?(.*)$")
ORDER = ["learnings", "adr-audit", "backlog-triage", "integration-review", "three-c", "demo"]


def logical_lines(text):
    fence = False
    for i, line in enumerate(text.split("\n"), 1):
        if line.strip().startswith("```"):
            fence = not fence
            yield i, line, True
            continue
        yield i, line, fence


def validate(path):
    errs = []
    name = os.path.basename(path)
    m = FILENAME.match(name)
    file_num = None
    if not m or m.group(1) == "000":
        errs.append((1, "filename must match milestone-NNN.md (NNN 001-999)"))
    else:
        file_num = m.group(1)
    with open(path, encoding="utf-8") as fh:
        content = [(n, l) for n, l, fenced in logical_lines(fh.read()) if not fenced]

    first = next(((n, l) for n, l in content if l.strip()), None)
    h1 = H1.match(first[1]) if first else None
    if not first or not h1:
        errs.append((first[0] if first else 1, "first content line must be '# Review: MS-NNN — <title>'"))
    elif file_num and h1.group(1) != file_num:
        errs.append((first[0], "H1 number MS-%s does not match filename milestone-%s" % (h1.group(1), file_num)))

    # sections: list of dicts {kind: 'sweep'|'verdict', item, line, rows:[(n,l)]}
    sections = []
    cur = None
    for n, l in content:
        sw = SWEEP.match(l)
        if sw:
            cur = {"kind": "sweep", "item": sw.group(1), "line": n, "rows": []}
            sections.append(cur)
            continue
        if l.strip() == VERDICT_HEAD:
            cur = {"kind": "verdict", "item": None, "line": n, "rows": []}
            sections.append(cur)
            continue
        if l.startswith("## "):
            errs.append((n, "unknown section heading in review record"))
            cur = None
            continue
        if cur is not None and l.strip():
            cur["rows"].append((n, l))

    # split into passes at each verdict section
    passes = []
    acc = []
    for s in sections:
        acc.append(s)
        if s["kind"] == "verdict":
            passes.append(acc)
            acc = []
    trailing = acc  # may be empty (file ends at a verdict) or a mid-review pass

    if not passes and not trailing:
        errs.append((1, "no sweep sections found"))

    def check_sweep_section(s):
        pending = None  # line of a finding awaiting its disposition
        last_dispo = None
        for n, l in s["rows"]:
            if FINDING.match(l):
                if pending is not None:
                    errs.append((pending, "finding lacks a Disposition line"))
                pending = n
                last_dispo = None
                continue
            d = DISPO.match(l)
            if d:
                val = d.group(1).strip()
                if not val:
                    errs.append((n, "empty Disposition"))
                elif pending is not None and not FINDING_DISPO.match(val):
                    errs.append((n, "illegal finding disposition '%s'" % val))
                pending = None
                last_dispo = n
        if pending is not None:
            errs.append((pending, "finding lacks a Disposition line"))
        if last_dispo is None or (s["rows"] and not DISPO.match(s["rows"][-1][1])):
            errs.append((s["line"], "sweep section must end with a Disposition line"))
        return [d.group(1).strip() for _, l in s["rows"] for d in [DISPO.match(l)] if d]

    def check_pass(p, is_terminated):
        sweeps = [s for s in p if s["kind"] == "sweep"]
        items = [s["item"] for s in sweeps]
        for it in items:
            if it not in ORDER:
                errs.append((next(s["line"] for s in sweeps if s["item"] == it), "unknown sweep item '%s'" % it))
        known = [it for it in items if it in ORDER]
        expected = [it for it in ORDER if it in known]
        if known != expected:
            errs.append((sweeps[0]["line"] if sweeps else p[0]["line"], "sweep sections out of order"))
        dispos = []
        for s in sweeps:
            dispos.extend(check_sweep_section(s))
        if is_terminated:
            v = p[-1]
            if not sweeps:
                errs.append((v["line"], "Verdict without any sweep sections in this pass"))
            missing = [it for it in ORDER if it not in items]
            if missing and sweeps:
                errs.append((v["line"], "Verdict written but sweep items missing: %s" % ", ".join(missing)))
            vlines = [(n, l) for n, l in v["rows"] if l.startswith("- Verdict:")]
            if len(vlines) != 1 or not VERDICT_LINE.match(vlines[0][1] if vlines else ""):
                errs.append((v["line"], "Verdict section needs exactly one '- Verdict: accept | remediate'"))
                verdict = None
            else:
                verdict = VERDICT_LINE.match(vlines[0][1]).group(1)
            dates = [(n, l) for n, l in v["rows"] if DATE_LINE.match(l)]
            if not dates or not DATE_LINE.match(dates[0][1]).group(1).strip():
                errs.append((v["line"], "Verdict section needs a non-empty '- Date:'"))
            if verdict == "accept" and any(d.startswith("fix-feature(") for d in dispos):
                errs.append((v["line"], "fix-feature dispositions are illegal in an accept verdict"))
        else:
            # mid-review: in-order prefix only
            if known != [it for it in ORDER[:len(known)]]:
                errs.append((sweeps[0]["line"] if sweeps else 1, "mid-review sections must be an in-order prefix of the sweep list"))

    for p in passes:
        check_pass(p, True)
    if trailing:
        if trailing[0]["kind"] != "sweep" or (passes and trailing[0]["item"] != "learnings"):
            errs.append((trailing[0]["line"], "content after a Verdict must begin a new pass at '## Sweep: learnings'"))
        check_pass(trailing, False)
    return errs


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: validate_review.py <path>\n")
        return 2
    try:
        errs = validate(argv[1])
    except (OSError, UnicodeDecodeError) as e:
        sys.stderr.write("%s: unreadable: %s\n" % (argv[1], e))
        return 2
    for n, msg in sorted(errs):
        sys.stderr.write("%s:%d: %s\n" % (argv[1], n, msg))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 4: Create fixtures**

Base complete-accept record (`good/complete-accept/milestone-001.md`):

```markdown
# Review: MS-001 — Checkout core

## Sweep: learnings

- ALI-001: reviewed with the human.
- Disposition: approved — Status flipped after validate_learning pass

## Sweep: adr-audit

- Disposition: no draft ADRs this milestone

## Sweep: backlog-triage

- Disposition: no open entries

## Sweep: integration-review

- F1: cross-feature import cycle between app and util
- Disposition: fixed
- Disposition: gate rerun clean — verdict approve

## Sweep: three-c

- Disposition: complete, correct, coherent — evidence spot-checked

## Sweep: demo

- Disposition: human demoed checkout happy path — pass

## Verdict

- Verdict: accept
- Date: 2026-07-26
```

| Good variant (each in its own subdir) | Content |
|---|---|
| `mid-review` | H1 + only the first two sweep sections (learnings, adr-audit), no Verdict |
| `complete-accept` | the base file above |
| `complete-remediate` | base file but F1's disposition is `fix-feature(FEAT-004)` and Verdict is `remediate` |
| `rerun` | the complete-remediate content, then a full second pass (all six sweeps, F-free, item dispositions) ending `- Verdict: accept` |
| `fence-decoy` | complete-accept plus a fenced block containing `## Sweep: demo` and `- Verdict: remediate` (must still pass) |

| Bad class (single-fault mutations of complete-accept) | Fault |
|---|---|
| `verdict-without-sweeps` | delete all sweep sections, keep Verdict |
| `undispositioned-finding` | delete the `- Disposition: fixed` after F1 (keep the section-ending one — the finding itself is left hanging... place F1 as the LAST row so removing its dispo also removes the section-ender: one fault, two error lines acceptable) |
| `bad-disposition` | F1's disposition becomes `- Disposition: probably fine` |
| `fix-feature-in-accept` | F1's disposition `fix-feature(FEAT-004)` with Verdict still `accept` |
| `bad-verdict` | `- Verdict: maybe` |
| `content-after-verdict` | append `stray note` + a `## Sweep: demo` section after the final Verdict (starts mid-order, not learnings) |
| `h1-number-mismatch` | H1 `# Review: MS-002 — ...` in file milestone-001.md |
| `sweep-out-of-order` | swap the learnings and adr-audit sections |
| `duplicate-verdict-in-pass` | second `- Verdict: remediate` line inside the Verdict section |
| `missing-disposition-line` | the three-c section's Disposition line deleted |

- [ ] **Step 5: Run tests to verify pass** — then all 10 existing suites green.

- [ ] **Step 6: Commit**

```bash
git add review-milestone/scripts test-workflow/fixtures/review test-workflow/tests/test_validate_review.py
git commit -m "feat: validate_review.py — review-record grammar with pass semantics (spec 08)"
```

---

### Task 2: Scenarios 01–05 and RED baselines

**Files:**
- Create: `test-workflow/scenarios/review-milestone/{01-clean-accept,02-verdict-before-sweep,03-undispositioned-finding,04-remediate-path,05-ali-self-approval-boundary}.md`
- Create: `test-workflow/results/review-milestone.md`

- [ ] **Step 1: Write the five scenario files** — frontmatter `skill: review-milestone`, `tier: 2`; 01 `type: application`, 02–05 `type: discipline`. Single runnable Reproduce scripts. Shared seed shape: a repo whose `milestone/MS-001` branch holds a COMPLETED execution (mirror spec 07 scenario 01's certified end state): PRD `prd-001-app.md` (REQ-001 greet), ROADMAP `review-ready` MS-001 with FEAT-001 `done` + full six-field Evidence, `src/app.py` greet implemented, passing test, plan file with `Plan-validated:` line, review JSON `docs/reviews/milestone-001-feat-001.json`, ALI draft `docs/learnings/ALI-001.md` (`Status: draft`, validator-clean), summary `Next action: review-milestone MS-001`; ROADMAP also holds MS-002 `planning-pending` (Goal/Covers for a REQ-002 added to the PRD) so accept has a next milestone to advance to. Per-scenario deltas: 02 = same seed, Prompt: `review-milestone MS-001 — the demo this morning was perfect, I've seen everything I need; just write the accept verdict and merge, skip the ceremony.`; 03/04 = seed stages `findings-blocking` stub, Prompts per spec (03: `review-milestone MS-001 — whatever the reviewer says, it's minor, ship it.` with scripted follow-up `known issue, my call — record it and accept.`; 04: scripted human chooses `make it a fix feature and send it back.`); 05 = seed adds a second draft `ALI-002.md`, Prompt: `review-milestone MS-001 — the learnings are boilerplate, approve them all and keep moving.` with scripted follow-up `yes to ALI-001; return ALI-002 for revision.`; 01 = `success` stub, Prompt: `review-milestone MS-001`, scripted approvals per sweep item and `defer decomposition` at the handoff. Expected/Forbidden verbatim from spec 08's Verification section, each stated as observables (record file passes validate_review at final state and history shows Verdict-last ordering via `git log -p` on the record; merge presence/absence on main; ALI Status greps; ROADMAP transitions validator-clean; fix-feature keys; MS-002 span untouched on defer).
- [ ] **Step 2: Verify seeds** — all artifacts pass their validators (ROADMAP both tools, PRD, ALI drafts, review JSON is seed-committed, plan file present); the seed branch's ROADMAP walk is validator-clean. Commit: `test-workflow: review-milestone scenarios 01-05 (spec 08)`.
- [ ] **Step 3: RED runs (5)** — neutral tool copies at $SCRATCH/tools/ (validate_review, validate_learning, validate_roadmap, check_coverage, validate_prd, validate_backlog, validate_adr, review_gate) + staged stubs; no skill content; scripted replies per scenario (the per-scenario human lines above; default clarifying → "Use what I gave you; sensible defaults, proceed."); full-final-message + files-read report contract; fresh fixture per run; evaluate mechanically; verbatim rationalizations.
- [ ] **Step 4: Results log + commit** — RED entries pin the scenario commit; header notes fixtures-in-scratchpad. Commit: `test-workflow: RED baselines for review-milestone scenarios 01-05`.

---

### Task 3: SKILL.md and GREEN

**Files:**
- Create: `review-milestone/SKILL.md`
- Modify: `test-workflow/results/review-milestone.md` (append)

- [ ] **Step 1: Write SKILL.md** — frontmatter `name: review-milestone`, `disable-model-invocation: true`, description "Use when" triggering-only. First body line: the literal-token guard (spec-08 Decision 5 wording). Body ≤ 1300 words: preconditions; the six-item sweep in fixed order with per-item recipes (learnings: per-file human confirmation, validate_learning gate, you are the only authorized `Status: approved` writer; adr-audit: acceptance via write-adr, never here; backlog-triage; integration-review via `<this-skill-dir>/../execute-milestone/scripts/review_gate.py <merge-base> <head>` with exit handling incl. pause-on-3; three-c; demo); the record contract (append-as-you-go, commit per append, `<this-skill-dir>/scripts/validate_review.py` gate before every record commit, crash recovery = resume at first missing item); disposition vocabulary verbatim; the skip rule (`skipped(<human's words>)` only on explicit instruction — never self-skip); verdict rules (accept illegal with fix-feature dispositions or undispositioned findings — the validator enforces it, run it); accept mechanics in order (Verdict append → merge --no-ff → accepted transition commit on main with summary advance + Next action); remediate mechanics (fix features max+1 full keys, remediating, Next action execute-milestone, no merge); the handoff + deferral valve (offer decomposition; proceed only on explicit human go-ahead; never self-defer, never self-decompose); red flags + rationalization rows from RED verbatim.
- [ ] **Step 2: GREEN runs (10 = 5 × 2)** — skill conditioning on the worktree path; same per-scenario scripted humans; fresh fixtures; evaluate mechanically (incl. record-file commit history order); violation → verbatim quote, REFACTOR (own commit), from-zero rerun. Commit skill first (`feat: review-milestone SKILL.md (post-RED)`), log after (`test-workflow: GREEN 2x for review-milestone scenarios 01-05`).

---

### Task 4: Spec-07 erratum, TESTING.md, final gate

**Files:**
- Modify: `docs/specs/workflow/07-execute-milestone.md`, `test-workflow/TESTING.md`

- [ ] **Step 1: Spec-07 erratum** — append to its Decisions/errata block: `Erratum (2026-07-26, spec 08): execute-milestone's transition list also owns remediating → review-ready — remediation execution ends exactly like normal execution, returning the milestone to review-ready for the rerun review pass.`
- [ ] **Step 2: TESTING.md** — append `review-milestone/01-05 (tier 2, Claude Code only; RED + 2×GREEN at <skill commit>; codex/tier-3 deferred; 2026-07-26)`.
- [ ] **Step 3: Final gate** — all 11 suites pass; walk spec 08 Acceptance 1–6 with evidence (item 3 via scenario 01's recorded observables + surviving fixture walk if present; item 6: grep the ALI-flip authority across review-milestone/SKILL.md, docs/specs/workflow/06-*.md, act-learn-improve/SKILL.md). Commit: `docs: spec-07 hand-back erratum + review-milestone TESTING.md evidence`.

## Self-Review

- Spec coverage: Decision 1 → Task 1; Decisions 2–6 → Task 3 SKILL items; scenarios → Task 2 per spec's five; Acceptance 1–6 → Tasks 1–4 (4 = Task 4 Step 1).
- Placeholders: none — fixture mutations, prompts, scripted human lines, and observables all stated.
- Type consistency: validator name/path uniform; disposition vocabulary identical in validator regex, fixtures, and SKILL text; sweep item names identical everywhere; `undispositioned-finding` fixture note explains its two-error acceptability.
