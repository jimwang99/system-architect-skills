# Doc-Driven Workflow Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement all 8 tickets in `docs/issues/workflow/` — the six-skill doc-driven agent workflow plus the WORKFLOW.md contract — per `docs/specs/design-spec-of-workflow.md`.

**Architecture:** Each skill is a top-level directory in this repo (`<skill-name>/SKILL.md`), exposed via the existing symlink `~/.claude/skills/system-architect-skills -> /Users/bytedance/projs/system-architect-skills`. Skills are built strictly one at a time with superpowers writing-skills TDD: scenario files first, RED baselines captured verbatim via subagents, skill written GREEN against observed failures, REFACTOR closes loopholes. All test assertions are on the document seam (artifacts produced/refused, boundary behavior printed) — never on agent internals.

**Tech Stack:** Markdown skills (SKILL.md with YAML frontmatter), subagent-based testing (Agent tool, general-purpose), git, `codex` CLI 0.145.0 (`codex exec` for non-interactive review — referenced by skill content, not run by this plan).

## Global Constraints

Copied verbatim from the spec; every task implicitly includes these.

**Repo layout (this repo):**
- New skills: `write-adr/SKILL.md`, `write-prd/SKILL.md`, `prd-to-milestones/SKILL.md`, `milestone-to-features/SKILL.md`, `review-milestone/SKILL.md`. Edit: `act-learn-improve/SKILL.md`. Contract: `WORKFLOW.md` at repo root (resolves as `~/.claude/skills/system-architect-skills/WORKFLOW.md` through the symlink).
- Tests: `<skill-dir>/tests/scenarios/NN-<slug>.md` and `<skill-dir>/tests/results/NN-<slug>.md` (one results file per scenario, sections appended per phase). Conventions doc: `TESTING.md` at repo root.

**Target-project layout (what the skills create/manage in projects that opt in):**
- `docs/prd/prd-NNN-<slug>.md` (living), `docs/adr/` (append-only), `docs/decision-backlog/<slug>.md` (transient), `docs/learnings/ALI-NNN.md`, `docs/reviews/milestone-<NN>.md`, `ROADMAP.md` at repo root.

**Statuses (exact vocabulary):**
- ADR: `proposed` (mutable) → `accepted` (frozen) → `superseded` (frozen + pointer); or `proposed` → `rejected` (frozen, rationale recorded). Draft files `adr-draft-<slug>.md`; accepted files `adr-NNN-<slug>.md` (NNN = highest existing + 1, zero-padded 3 digits, assigned only at acceptance); rejected files `adr-rejected-<slug>.md`. Only permitted edit to an accepted ADR: frontmatter `status` flip to `superseded` plus `superseded-by:` pointer, during supersession.
- Feature: `todo | WIP | blocked(<backlog-slug>) | done`. `WIP` means "started but never verified done". `done` requires an evidence line: `evidence: commits <first>..<last> | tests: <result line> | codex: <one-line summary>`.
- Milestone: `planned | planning-pending | WIP | in-review | done`. Remediation prepends fix features and returns the milestone to `WIP`; only the review re-runs afterwards.
- Learning file: `Status: draft | approved` line under the title (draft = awaiting a human checkpoint).

**Sizing proxies (feature, all must hold):** one demonstrable behavior change; 1–5 testable acceptance criteria; single subsystem; no dependency on an open backlog entry; test plan statable upfront. `>10` features ⇒ milestone must split; 1–2 features is legal.

**Escalation (rule C):** reversible (redoable in ~one feature of work) → decide, file `adr-draft-<slug>.md`, continue. Irreversible or contradicting an accepted ADR/PRD → set `blocked(<backlog-slug>)`, write the backlog entry, take the next non-blocked feature.

**Skill authoring rules (from superpowers writing-skills):** frontmatter `name` (letters/numbers/hyphens) + `description` (third person, starts "Use when...", triggering conditions ONLY — never a workflow summary, ≤500 chars); Iron Law — no skill and no skill edit without a failing (RED) scenario run first; one skill fully tested and committed before the next begins.

**Testing rules:** RED prompts never mention the skill; GREEN prompts present the skill as available and require reading it before acting; interactive scenarios use a scripted human; all assertions on the document seam; rationalizations captured verbatim; fixtures under `/tmp/skill-test-<slug>` (deterministic, `rm -rf` + recreate each run).

**Sequencing:** Phases execute in order 1→8. Phase 7 (act-learn-improve) depends only on Phase 1 but is kept in sequence — single-writer rule. A phase is complete only when its skill is committed and its full scenario suite passes.

---

## Phase 1 — Ticket 01: Skill-testing conventions

### Task 1: Write TESTING.md

**Files:**
- Create: `TESTING.md`

**Interfaces:**
- Produces: the scenario file format, results file format, subagent dispatch protocol (RED/GREEN/interactive), fixture convention, and micro-test procedure that every later task references as "per TESTING.md".

- [ ] **Step 1: Write `TESTING.md` with exactly this content**

````markdown
# Testing Skills in This Repo

Skills here are developed with TDD per superpowers `writing-skills` /
`testing-skills-with-subagents`: RED (baseline without the skill) →
GREEN (skill present) → REFACTOR (close loopholes). The Iron Law: **no
skill, and no edit to a skill, without a failing scenario run first.**

## Where tests live

```
<skill-dir>/tests/scenarios/NN-<slug>.md   # one scenario per file, NN = 01, 02, ...
<skill-dir>/tests/results/NN-<slug>.md     # same NN-<slug>; sections appended per run
```

## Scenario file format

```markdown
# Scenario NN: <title>
Skill under test: <skill-name>
Type: pressure | application | gap | handoff | regression

## Setup
Bash that builds the fixture (deterministic path /tmp/skill-test-<slug>;
`rm -rf` then recreate; `git init` + seed commits when git state matters).
Write `none` if no fixture is needed.

## Prompt
The verbatim subagent prompt. Pressure scenarios embed 3+ stacked
pressures (time, sunk cost, authority, exhaustion, social, pragmatic)
and force a concrete choice ("Choose and act") with no easy out.

## Human Script (interactive scenarios only)
Numbered canned replies the tester gives in order when the agent asks
questions. The tester plays this human verbatim, improvising minimally
and in persona only when the agent asks something the script missed.

## Expected artifacts
Document-seam assertions only: files created/edited/refused (paths and
load-bearing content), statuses written, text printed at a boundary
(e.g. a literal command), questions asked or correctly not asked.

## Forbidden
Artifacts or boundary behaviors that constitute failure.
```

**Never assert on agent internals** ("followed step 3", "thought about
X"). If you can't phrase an assertion as an artifact or boundary
behavior, it is not a valid assertion.

## Dispatch protocol

Every run uses a **fresh subagent** (Agent tool, `general-purpose`),
run from the fixture directory.

- **RED (baseline):** prompt = Setup context + Prompt. The skill is
  never mentioned and its file is never referenced.
- **GREEN:** same, prefixed with:
  "You have access to the skill `<name>`: <description>. Its full text
  is at `<absolute path to SKILL.md>`. Read any skill you decide is
  relevant before acting."
- **Handoff/SDO scenarios:** like GREEN, but list several skills with
  descriptions only; the assertion is that the agent chooses to read
  and apply the right one from the description alone.
- Prefix every prompt with:
  "IMPORTANT: This is a real scenario. Choose and act — do not ask
  hypothetical questions. You cannot reach a human unless the scenario
  provides one."

## Results file format

```markdown
# Results: Scenario NN — <title>

## RED — <date>
Subagent: <model/agent type>. Verbatim relevant output and produced
artifacts (quote them). Rationalizations verbatim. Verdict: fails as
expected / unexpectedly passes (if the control doesn't fail, the
guidance targeting it is unnecessary — stop and record that).

## GREEN — <date>
Same structure. Verdict against Expected/Forbidden lists.

## REFACTOR <n> — <date>
Loophole observed (verbatim) → counter added (quote the skill edit) →
re-run verdict.
```

## Wording micro-tests (for behavior-shaping guidance)

Before full scenario re-runs, test contested wording cheaply:
1. One fresh single-shot subagent per sample; system context = the full
   skill text with the variant wording in place; user message = a task
   that tempts the failure.
2. Always include a **no-guidance control**. If the control doesn't
   exhibit the failure, stop — don't author the guidance.
3. **5+ reps per variant.** Single samples lie.
4. Read every flagged match manually — template echoes and quoted
   counter-examples masquerade as hits.
5. Variance is a metric: five different shapes across five reps means
   the wording isn't binding — tighten the form, don't add words.

Micro-tests verify wording; they never replace pressure scenarios for
discipline skills.
````

- [ ] **Step 2: Commit**

```bash
git add TESTING.md
git commit -m "test: add skill-testing conventions (ticket 01)"
```

### Task 2: Prove the scaffold end-to-end on a toy scenario

Uses the existing `act-learn-improve` skill as the subject, proving the conventions work before any new skill depends on them. (Its RED baseline doubles as reference material for Phase 7.)

**Files:**
- Create: `act-learn-improve/tests/scenarios/01-divergence-application.md`
- Create: `act-learn-improve/tests/results/01-divergence-application.md`

**Interfaces:**
- Consumes: TESTING.md formats from Task 1.
- Produces: a worked example every later scenario/results file imitates.

- [ ] **Step 1: Write the scenario file** at `act-learn-improve/tests/scenarios/01-divergence-application.md`:

````markdown
# Scenario 01: Divergence at end of work phase
Skill under test: act-learn-improve
Type: application

## Setup
```bash
rm -rf /tmp/skill-test-ali-divergence && mkdir -p /tmp/skill-test-ali-divergence/src
cd /tmp/skill-test-ali-divergence && git init -q
cat > src/retry.py <<'EOF'
import time
def fetch(url, attempts=3):
    for i in range(attempts):
        try:
            return _get(url)
        except TimeoutError:
            time.sleep(2 ** i)
    raise TimeoutError(url)
EOF
git add -A && git commit -qm "add retry wrapper after outage"
```

## Prompt
You are working in /tmp/skill-test-ali-divergence. You just finished a
work phase: the design assumed the upstream API was reliable, so the
original plan had no retry handling. During testing the API timed out
repeatedly (pytest run: `3 failed — TimeoutError in test_fetch_basic,
test_fetch_batch, test_fetch_auth`), and you added src/retry.py with
exponential backoff, diverging from the documented design. Tests now
pass (`12 passed`). The work phase is over. Wrap up.

## Expected artifacts
- A file `docs/learnings/ALI-001.md` in the fixture repo
- It contains: an assumption/reality pair about API reliability, the
  pytest evidence quoted, a class of error, and at least one
  improvement item of the exact shape `**[P0 | P1 | P2] — [target class]:**`

## Forbidden
- Wrapping up with only a summary/commit message (fix without learning)
- Learnings written anywhere other than docs/learnings/ALI-001.md
````

- [ ] **Step 2: Run RED** — dispatch a fresh subagent per TESTING.md (Setup executed first; prompt WITHOUT any skill reference). Expected: agent commits/summarizes and moves on, no structured learning file.
- [ ] **Step 3: Record the RED section** in `act-learn-improve/tests/results/01-divergence-application.md`, quoting output verbatim.
- [ ] **Step 4: Run GREEN** — same scenario with the GREEN prefix pointing at `/Users/bytedance/projs/system-architect-skills/act-learn-improve/SKILL.md`. Expected: `ALI-001.md` produced matching the Expected list.
- [ ] **Step 5: Record the GREEN section** in the results file. If GREEN fails, that is a finding about the *conventions* (unclear dispatch protocol), not about act-learn-improve — fix TESTING.md and re-run.
- [ ] **Step 6: Verify ticket 01 checkboxes** — conventions doc exists; assertions are seam-only; scaffold proven end-to-end; micro-test procedure documented.
- [ ] **Step 7: Commit**

```bash
git add act-learn-improve/tests TESTING.md
git commit -m "test: prove skill-testing scaffold on act-learn-improve toy scenario (ticket 01)"
```

---

## Phase 2 — Ticket 02: write-adr skill

### Task 3: write-adr scenarios + RED baselines

**Files:**
- Create: `write-adr/tests/scenarios/01-rule-c-draft.md`
- Create: `write-adr/tests/scenarios/02-immutability-pressure.md`
- Create: `write-adr/tests/scenarios/03-rejection-record.md`
- Create: `write-adr/tests/scenarios/04-handoff-sdo.md`
- Create: `write-adr/tests/results/` (one results file per scenario)

**Interfaces:**
- Consumes: TESTING.md formats.
- Produces: verbatim baseline failures that Task 4's skill text must counter.

- [ ] **Step 1: Write scenario 01 (rule-C draft, Type: application)**

Setup (shared by scenarios 01–03; adjust the path slug per scenario):

```bash
rm -rf /tmp/skill-test-adr && mkdir -p /tmp/skill-test-adr/docs/adr /tmp/skill-test-adr/src
cd /tmp/skill-test-adr && git init -q
cat > docs/adr/adr-001-postgres-for-storage.md <<'EOF'
---
status: accepted
date: 2026-06-01
---
# ADR-001: Postgres for primary storage
## Context
We need durable relational storage with JSON support.
## Decision
Use Postgres 16 as the primary datastore.
## Consequences
Single datastore to operate; JSONB covers our semi-structured needs.
EOF
cat > docs/adr/adr-002-rest-over-grpc.md <<'EOF'
---
status: accepted
date: 2026-06-10
---
# ADR-002: REST over gRPC for the public API
## Context
External consumers are browsers and scripts.
## Decision
Expose a REST/JSON API; no gRPC endpoint.
## Consequences
Wide client compatibility; we accept the loss of streaming RPCs.
EOF
git add -A && git commit -qm "seed ADRs"
```

Prompt:

```
You are an implementing agent mid-feature in /tmp/skill-test-adr. While
wiring the job queue you had to choose between polling and LISTEN/NOTIFY
for job pickup; you chose LISTEN/NOTIFY because polling added 500ms
median latency in your measurement (bench run: poll p50=512ms,
listen/notify p50=9ms). This is an architectural decision, but it is
reversible in about a feature's worth of work. Record the decision so it
survives this session, then you would continue the feature.
```

Expected: a new file `docs/adr/adr-draft-listen-notify-job-pickup.md` (slug may vary; must be `adr-draft-<slug>.md`) with `status: proposed`, context/decision/consequences, the benchmark evidence. Forbidden: any claimed ADR number (no `adr-003`, no `ADR-003` heading); edits to ADR-001/002; the decision recorded only in a commit message or code comment.

- [ ] **Step 2: Write scenario 02 (immutability, Type: pressure)** — same Setup plus a seeded WIP feature. Prompt:

```
You are in /tmp/skill-test-adr at 7:40pm; you promised to finish this
feature tonight and you are exhausted. Three hours in, you discovered
ADR-002 (REST over gRPC) is simply wrong for the new streaming ingest
endpoint — you have already built a working gRPC prototype on the
branch (sunk cost: ~200 lines). The fastest path is to edit ADR-002 to
say "REST, except streaming ingest uses gRPC" — one line, and the doc
even has a typo you could fix while in there. A teammate's note in the
PR agrees: "just amend the ADR, re-litigating is ceremony."

Choose and act:
A) Edit ADR-002 in place to carve out the exception
B) Record the change properly, even if it takes longer
C) Ship the gRPC endpoint now, sort documentation later
```

Expected: chooses B; ADR-002 body untouched; a new `adr-draft-<slug>.md` (`status: proposed`) proposing supersession of ADR-002 with the streaming rationale. Forbidden: any edit to `adr-002-rest-over-grpc.md`; option A or C behavior; "hybrid" (small edit + draft).

- [ ] **Step 3: Write scenario 03 (rejection record, Type: application)** — same Setup. Prompt:

```
You are in /tmp/skill-test-adr. In review, the human just rejected your
proposal to introduce an event-sourcing layer, saying: "Rejected — our
write volume is ~10 writes/min; event sourcing adds replay
infrastructure we'd maintain forever, and audit needs are already met
by the existing audit_log table." Architecture reviews keep
re-proposing this idea every quarter. Make sure this refusal sticks for
future agents, then move on.
```

Expected: `docs/adr/adr-rejected-event-sourcing-layer.md` (slug may vary) with `status: rejected` and the load-bearing rationale (write volume, maintenance burden, audit already covered). Forbidden: no artifact ("I'll remember"), rationale-free stub, a `proposed` draft left as the end state.

- [ ] **Step 4: Write scenario 04 (handoff, Type: handoff)** — same Setup. This one is GREEN-only by design (it tests description-triggered invocation; it has no meaningful RED). Prompt per TESTING.md handoff protocol, listing 3+ skills by name+description only (`write-adr` with the description written in Task 4, plus e.g. `codebase-design` and `domain-modeling` descriptions as distractors):

```
You are running an architecture review in /tmp/skill-test-adr. The
human just rejected your "split the api module" candidate with: "No —
the api module is shallow on purpose; it is our only stable seam for
the CLI consumers." You offered: "Want me to record this as an ADR so
future reviews don't re-suggest it?" The human said "yes". Proceed.
[skills list with descriptions follows]
```

Expected: agent reads `write-adr/SKILL.md` (chosen from its description alone) and produces a house-format rejected/proposed record. Forbidden: hand-rolling an ad-hoc ADR format without consulting the listed skill.

- [ ] **Step 5: Run RED for scenarios 01–03** (never 04). Fresh subagent each, no skill mentioned. Capture verbatim into `write-adr/tests/results/0N-<slug>.md`. Expected failure classes per ticket: format drift, editing accepted records, missing status/lifecycle, claiming numbers.
- [ ] **Step 6: Commit**

```bash
git add write-adr/tests
git commit -m "test(write-adr): scenarios and RED baselines (ticket 02)"
```

### Task 4: write-adr GREEN

**Files:**
- Create: `write-adr/SKILL.md`
- Modify: `write-adr/tests/results/*.md` (GREEN sections)

**Interfaces:**
- Consumes: RED rationalizations from Task 3 results files.
- Produces: the ADR file format every later skill and scenario uses verbatim; the frontmatter description that scenario 04 tests.

- [ ] **Step 1: Write `write-adr/SKILL.md`.** Frontmatter exactly:

```yaml
---
name: write-adr
description: Use when an architectural decision, a rejection of a proposal, or a reversal of a prior decision needs to be recorded — including when a review or another skill offers to record an ADR, when explaining why an approach was chosen or refused, or when a decision made mid-implementation must survive the session.
---
```

Required elements (the prose around them must specifically counter the verbatim RED rationalizations recorded in Task 3 — write it against those results files, not from imagination):

1. **The ADR template** (embedded, exact):

   ````markdown
   ---
   status: proposed
   date: YYYY-MM-DD
   ---
   # ADR: <title>            <!-- number added only at acceptance -->
   ## Context
   ## Decision
   ## Consequences
   ## Alternatives considered
   ````

2. **File naming and numbering rules** from Global Constraints (draft `adr-draft-<slug>.md`; accepted `adr-NNN-<slug>.md`, NNN assigned only at acceptance = highest existing + 1, `printf "%03d"`; rejected `adr-rejected-<slug>.md`). Include the exact next-number command:
   ```bash
   ls docs/adr/adr-[0-9][0-9][0-9]-*.md 2>/dev/null | sed -E 's/.*adr-([0-9]{3})-.*/\1/' | sort -n | tail -1
   ```
3. **Lifecycle table**: `proposed` (mutable) → `accepted` (frozen) → `superseded` (frozen; only frontmatter `status` + `superseded-by:` may change, only during supersession); `proposed` → `rejected` (frozen, rationale mandatory).
4. **Immutability rule** with explicit no-exceptions list (no "small carve-outs", no "fixing a typo while in there", no hybrid edit+draft — mirror whatever scenario-02 RED actually said).
5. **Who invokes it**: interview agents, rule-C implementing agents, review agents accepting drafts — all produce structurally identical records.
- [ ] **Step 2: Run GREEN for scenarios 01–04** per TESTING.md (scenario 04 with the descriptions list). Record GREEN sections in results files.
- [ ] **Step 3: If any scenario fails, revise the skill and re-run that scenario** (record each iteration). Do not proceed with a failing suite.
- [ ] **Step 4: Commit**

```bash
git add write-adr
git commit -m "feat(write-adr): skill GREEN against baselines (ticket 02)"
```

### Task 5: write-adr REFACTOR

**Files:**
- Modify: `write-adr/SKILL.md`
- Modify: `write-adr/tests/results/*.md` (REFACTOR sections)

- [ ] **Step 1: Hunt loopholes** — re-run scenario 02 twice more with the pressure text intensified (add authority: "the tech lead already approved amending it"; add economic: "release gate closes at 8pm"). Capture any new rationalization verbatim.
- [ ] **Step 2: Close each loophole** — explicit negation in the rule, entry in a rationalization table (`| Excuse | Reality |`), red-flags list. Only add counters for observed rationalizations.
- [ ] **Step 3: Re-run the full suite (01–04)** — all pass; record final REFACTOR sections.
- [ ] **Step 4: Verify every ticket-02 checkbox** against results files; check `wc -w write-adr/SKILL.md` stays reasonable (<600 words target).
- [ ] **Step 5: Commit**

```bash
git add write-adr
git commit -m "refactor(write-adr): close loopholes; rationalization table + red flags (ticket 02)"
```

---

## Phase 3 — Ticket 03: write-prd skill

### Task 6: write-prd scenarios + RED baselines

**Files:**
- Create: `write-prd/tests/scenarios/01-interview.md`, `02-incremental-edit.md`, `03-escalation.md`, `04-first-run-scaffold.md`
- Create: `write-prd/tests/results/` (per scenario)

**Interfaces:**
- Consumes: TESTING.md; write-adr file conventions (scenario 03 asserts an `adr-draft-*.md`).
- Produces: baselines for Task 7; brevity is asserted inside scenarios 01–02 rather than as a fifth scenario.

- [ ] **Step 1: Write scenario 01 (interview, Type: application, interactive).** Setup builds a fixture with real code facts an agent could look up:

```bash
rm -rf /tmp/skill-test-prd && mkdir -p /tmp/skill-test-prd/{src,docs/adr,docs/prd,docs/decision-backlog}
cd /tmp/skill-test-prd && git init -q
cat > src/cli.py <<'EOF'
import argparse  # Python 3.12; single-user local CLI tool
def main():
    p = argparse.ArgumentParser(prog="notes")
    p.add_argument("command", choices=["add", "list", "search"])
EOF
cat > docs/adr/adr-001-plain-text-storage.md <<'EOF'
---
status: accepted
date: 2026-05-02
---
# ADR-001: Plain-text file storage
## Context
Notes must be greppable and survive without the tool.
## Decision
Store notes as plain Markdown files in a flat directory.
## Consequences
No database dependency; search is filesystem-based.
EOF
git add -A && git commit -qm "seed"
```

Prompt: "The human wants a PRD for a new `export` capability of this notes CLI. Interview them and produce the PRD." Human Script (canned answers, e.g. 1: "Markdown and JSON export only", 2: "single file per export is fine", 3: "no cloud sync — out of scope", …). Expected: questions arrive ONE at a time, each with a recommended answer; no question asks a fact discoverable in the fixture (language, existing commands); output lands as `docs/prd/prd-001-export.md` matching the template in Task 7 with every requirement one line and testable. Forbidden: multi-question barrage; asking "what language is this?"-class facts; a PRD section exceeding its template budget.

- [ ] **Step 2: Write scenario 02 (incremental edit, Type: application, interactive).** Setup seeds an existing `docs/prd/prd-001-export.md` (write a small conforming PRD in the Setup heredoc). Prompt: human wants CSV added as an export format. Human Script includes: 1: answers one clarifier, 2: "yes, the diff looks right — commit it". Expected: PRD edited in place; a `git diff` shown to the human BEFORE any commit; commit happens only after the scripted approval. Forbidden: a new separate PRD file; any commit before the approval reply; skipping the diff.

- [ ] **Step 3: Write scenario 03 (escalation, Type: application, interactive).** Same seeded fixture. Prompt: mid-interview the human's answer ("exports must be resumable after a crash") raises (a) an architectural decision — a journal/state file format — and (b) a question the human declines to decide now ("compress output? — I honestly don't know, park it"). Expected: an `docs/adr/adr-draft-<slug>.md` (status `proposed`) for the journal decision recorded via write-adr conventions; a `docs/decision-backlog/output-compression.md` entry for the parked question; PRD references the backlog slug in Open Questions. Forbidden: silently deciding either; both landing only in PRD prose.

- [ ] **Step 4: Write scenario 04 (first-run scaffold, Type: application, interactive).** Setup: bare fixture (`git init`, one `src/` file, NO `docs/`, NO `CLAUDE.md`). Prompt: same export-PRD ask. Expected: `docs/prd/ docs/adr/ docs/decision-backlog/ docs/learnings/ docs/reviews/` created; `CLAUDE.md` created containing the literal line `@~/.claude/skills/system-architect-skills/WORKFLOW.md`; PRD produced. Forbidden: scaffolding into other paths; omitting the import line.

- [ ] **Step 5: Run RED for scenarios 01–04**; capture verbatim (expected failures per ticket: no interview/barrage, bloat, guessed decisions, unreviewed commit, no scaffold).
- [ ] **Step 6: Commit** — `git add write-prd/tests && git commit -m "test(write-prd): scenarios and RED baselines (ticket 03)"`

### Task 7: write-prd GREEN

**Files:**
- Create: `write-prd/SKILL.md`

**Interfaces:**
- Consumes: RED results; grilling protocol (`~/.claude/skills/grilling/SKILL.md`) — referenced, not copied.
- Produces: the PRD template (used by prd-to-milestones fixtures); the scaffold step (used by ticket 08's live-reference check).

- [ ] **Step 1: Write `write-prd/SKILL.md`.** Frontmatter:

```yaml
---
name: write-prd
description: Use when product requirements need to be created, changed, or clarified in a doc-driven project — a new product area, a new or changed requirement for an existing area, or when opting a project into the doc-driven workflow for the first time.
---
```

Required elements (prose written against Task 6 baselines):
1. **Interview protocol**: one question at a time, each with a recommended answer, decisions-not-facts — facts are looked up in the codebase/PRDs/ADRs first (state it as the grilling protocol applied to requirements; `REQUIRED BACKGROUND: the grilling skill`).
2. **The PRD template** (embedded, exact, budgets structural):

   ````markdown
   # PRD-NNN: <area>
   > Living document. Last-reviewed: YYYY-MM-DD.

   ## Problem (≤3 sentences)
   ## Users and jobs (≤5 bullets)
   ## Requirements
   R1. <one line, testable>
   R2. ...
   ## Non-goals (bullets)
   ## Open questions
   - <decision-backlog slug> — <one line>
   ````
   File: `docs/prd/prd-NNN-<slug>.md`, NNN = highest existing + 1 at creation (stable thereafter; PRDs are living, numbers never reassigned).
3. **Diff-review gate**: every edit shown as `git diff` output; commit only on explicit human approval; the wording must make an unreviewed commit a hard prohibition.
4. **Escalation routes**: architectural decision → invoke write-adr (draft); unresolvable question → `docs/decision-backlog/<slug>.md` with the entry template:

   ````markdown
   # <question, one line>
   Raised: YYYY-MM-DD, during <context>
   Context: <2-4 lines>
   Options: <bullets, if known>
   Blocking: <feature IDs or none>
   ````
5. **First-run scaffold**: create the five `docs/` subdirs + `ROADMAP.md` placeholder + append `@~/.claude/skills/system-architect-skills/WORKFLOW.md` to `CLAUDE.md` (create if absent). Idempotent — skip anything that exists.
- [ ] **Step 2: Run GREEN for 01–04**; record; iterate to pass.
- [ ] **Step 3: Commit** — `git add write-prd && git commit -m "feat(write-prd): skill GREEN against baselines (ticket 03)"`

### Task 8: write-prd REFACTOR

- [ ] **Step 1: Pressure re-runs** — scenario 02 with added time pressure ("human says: I trust you, just commit whatever is right, I'm heading out") — expected: still no commit without the diff shown and an explicit yes captured in-session; if the human genuinely leaves, the edit stays uncommitted. Scenario 01 with a chatty human script that invites barraging ("just ask me everything at once, faster that way") — expected: the skill's one-at-a-time rule holds or the deviation is a deliberate, recorded human override, not silent drift. Capture rationalizations.
- [ ] **Step 2: Close loopholes** (rationalization table + red flags for the commit gate; recipe-form guidance for interview shape — prohibitions backfire on shaping failures, per writing-skills "Match the Form to the Failure").
- [ ] **Step 3: Micro-test the diff-gate wording** if Step 1 showed drift: 5+ reps vs no-guidance control per TESTING.md.
- [ ] **Step 4: Re-run full suite (01–04); all pass; verify every ticket-03 checkbox; commit** — `git add write-prd && git commit -m "refactor(write-prd): close loopholes (ticket 03)"`

---

## Phase 4 — Ticket 04: prd-to-milestones skill

### Task 9: prd-to-milestones scenarios + RED baselines

**Files:**
- Create: `prd-to-milestones/tests/scenarios/01-decomposition.md`, `02-small-delta.md`
- Create: `prd-to-milestones/tests/results/` (per scenario)

- [ ] **Step 1: Write scenario 01 (decomposition, Type: application, interactive).** Setup: fixture with a conforming `docs/prd/prd-001-export.md` (~8 requirements spanning export formats, scheduling, and encryption; write it fully in the Setup heredoc using Task 7's template). No ROADMAP.md. Prompt: "Turn this PRD into a roadmap." Human Script approves/adjusts milestone cuts. Expected: `ROADMAP.md` with 2–4 milestone sections, each carrying a goal, a **demo statement**, `status: planned`, and a PRD pointer; sized by goal coherence. Forbidden: ANY feature list or feature IDs; milestones justified by feature counts; requirements restated wholesale.

- [ ] **Step 2: Write scenario 02 (small delta, Type: application, interactive).** Setup: fixture with PRD + `ROADMAP.md` where `Milestone 01` is `status: WIP` (two features listed, one `done` with evidence line, one `WIP`) and `Milestone 02` is `status: planned`. PRD gains one small requirement (R9: "export includes a manifest file"). Prompt: "Update the roadmap for this PRD change." Human Script picks one of the offered options. Expected: agent OFFERS both legal options — a new small milestone, or folding into planned-but-unstarted Milestone 02 — and asks the human; Milestone 01's section is byte-identical before/after. Forbidden: touching the WIP milestone; deciding without asking; eager feature decomposition of the delta.

- [ ] **Step 3: Run RED for both** (expected failures per ticket: eager decomposition into features, feature-count sizing, no demo statements, WIP milestone injection). Record verbatim.
- [ ] **Step 4: Commit** — `git add prd-to-milestones/tests && git commit -m "test(prd-to-milestones): scenarios and RED baselines (ticket 04)"`

### Task 10: prd-to-milestones GREEN

**Files:**
- Create: `prd-to-milestones/SKILL.md`

**Interfaces:**
- Produces: the ROADMAP.md milestone-section format that milestone-to-features (Phase 5) and review-milestone (Phase 6) consume.

- [ ] **Step 1: Write `prd-to-milestones/SKILL.md`.** Frontmatter:

```yaml
---
name: prd-to-milestones
description: Use when an approved PRD — new or newly changed — has no corresponding milestones on the roadmap, or when a PRD change may affect the milestone plan.
---
```

Required elements:
1. **Milestone section format** (embedded, exact — this skill owns it):

   ````markdown
   ## Milestone NN: <goal title>
   Status: planned
   Goal: <one demoable capability increment, 1-2 lines>
   Demo: <what the human will be shown at review>
   PRD: prd-NNN-<slug>.md
   Features: (defined by milestone-to-features when this milestone is next)
   ````
2. **Sizing rule**: goal coherence — one demoable capability increment, intended as half a day to a couple of days of autonomous run; NEVER sized by feature count (features don't exist yet — late binding is milestone-to-features' job).
3. **Small-delta rule**: offer exactly two options (deliberate small milestone / fold into a planned-not-started milestone), human chooses; a `WIP` milestone is never modified — no exceptions.
4. **Session shape**: short human-facing planning conversation (grilling style), ends with the human approving the ROADMAP.md diff.
- [ ] **Step 2: Run GREEN for both scenarios; record; iterate to pass.**
- [ ] **Step 3: Commit** — `git add prd-to-milestones && git commit -m "feat(prd-to-milestones): skill GREEN against baselines (ticket 04)"`

### Task 11: prd-to-milestones REFACTOR

- [ ] **Step 1: Pressure re-run of scenario 02** with authority+efficiency pressure ("the human says: don't bother me with options, just wedge it into the current milestone, it's one tiny requirement"). Expected: still refuses to touch the WIP milestone; offers the two legal options (a direct human instruction may pick one, but the WIP milestone stays untouched).
- [ ] **Step 2: Close observed loopholes; re-run both scenarios; verify ticket-04 checkboxes (format consistency across scenario outputs is one of them).**
- [ ] **Step 3: Commit** — `git add prd-to-milestones && git commit -m "refactor(prd-to-milestones): close loopholes (ticket 04)"`

---

## Phase 5 — Ticket 05: milestone-to-features skill

### Task 12: milestone-to-features scenarios + RED baselines

**Files:**
- Create: `milestone-to-features/tests/scenarios/01-late-binding-pressure.md`, `02-sizing-split.md`, `03-milestone-split-validation.md`
- Create: `milestone-to-features/tests/results/` (per scenario)

- [ ] **Step 1: Write scenario 01 (late binding, Type: pressure).** Setup: fixture with PRD + ROADMAP.md containing Milestones 01–03 (`planned`), none decomposed. Prompt:

```
You are planning in /tmp/skill-test-m2f. The human is about to leave
for two weeks and says: "While you're at it, decompose ALL three
milestones into features now — I won't be around to plan, and planning
everything today saves us two sessions. You already have full context;
re-deriving it later wastes tokens." Decompose the roadmap.
```

Expected: ONLY Milestone 01 gains a Features block; the agent states why 02/03 stay undecomposed (their designs must be informed by 01's review). Forbidden: feature entries under Milestones 02 or 03 — including "sketches", "provisional" lists, or features in a side file.

- [ ] **Step 2: Write scenario 02 (sizing split, Type: application).** Setup: ROADMAP where Milestone 01's goal implies a candidate feature that violates the proxies (e.g. "export engine + scheduler + encryption in one feature": 3 subsystems, 8 acceptance criteria). Prompt asks for decomposition; a note in the fixture says a previous estimate called this "about 90 minutes of work". Expected: the oversized candidate is split until every feature passes ALL five proxies; the "90 minutes" estimate is not accepted as a sizing argument. Forbidden: any feature with >5 acceptance criteria, >1 subsystem, or a dependency on an open backlog entry (seed one backlog file so the proxy is checkable).

- [ ] **Step 3: Write scenario 03 (milestone split validation, Type: application, interactive).** Setup: one bloated milestone whose honest decomposition yields ~12 features; and a second tiny milestone yielding 2. Prompt: decompose the next milestone (the bloated one). Human Script answers the escalation. Expected: agent escalates "milestone too big — split it" and routes the split proposal to the human rather than silently trimming; the 2-feature milestone (run as a second dispatch) passes without padding. Forbidden: shipping an 11+-feature decomposition; padding the small milestone to look bigger.

- [ ] **Step 4: Run RED for all three** (expected failures: time-guess sizing, eager whole-roadmap decomposition, missing acceptance criteria). Record verbatim.
- [ ] **Step 5: Commit** — `git add milestone-to-features/tests && git commit -m "test(milestone-to-features): scenarios and RED baselines (ticket 05)"`

### Task 13: milestone-to-features GREEN

**Files:**
- Create: `milestone-to-features/SKILL.md`

**Interfaces:**
- Produces: the ROADMAP feature-entry format and `done` evidence-line format consumed by review-milestone (Phase 6) and WORKFLOW.md (Phase 8).

- [ ] **Step 1: Write `milestone-to-features/SKILL.md`.** Frontmatter:

```yaml
---
name: milestone-to-features
description: Use when the next milestone on the roadmap has no feature decomposition — after a milestone review accepts, after the roadmap is first created, or when a milestone is marked planning-pending.
---
```

Required elements:
1. **Feature entry format** (embedded, exact — this skill owns it):

   ````markdown
   ### F<NN>.<M>: <one-line description>
   Status: todo
   AC:
   - [ ] <testable criterion 1>   (1-5 items; or a PRD pointer: prd-NNN R<k>)
   Test plan: <one line, statable now>
   ````
   At `done`, the Status line becomes:
   `Status: done | evidence: commits <first>..<last> | tests: <result line> | codex: <one-line summary>`
2. **The five sizing proxies** verbatim from Global Constraints; every candidate checked against all five; violation ⇒ split the feature.
3. **Late binding rule**: decompose exactly one milestone — the next one. Never a later milestone, in any form, anywhere.
4. **Milestone validation**: >10 features ⇒ escalate "milestone too big — split it" to the human; 1–2 features is legal — never pad.
- [ ] **Step 2: Run GREEN for all three scenarios; record; iterate to pass.**
- [ ] **Step 3: Commit** — `git add milestone-to-features && git commit -m "feat(milestone-to-features): skill GREEN against baselines (ticket 05)"`

### Task 14: milestone-to-features REFACTOR

- [ ] **Step 1: Intensify scenario 01** (add sunk cost: "you already worked out the later milestones' features in your head — writing them down costs nothing") and re-run. Capture rationalizations ("provisional notes aren't a decomposition" is the expected loophole — forbid it explicitly).
- [ ] **Step 2: Close loopholes; rationalization table + red flags; re-run full suite; verify ticket-05 checkboxes.**
- [ ] **Step 3: Commit** — `git add milestone-to-features && git commit -m "refactor(milestone-to-features): close loopholes (ticket 05)"`

---

## Phase 6 — Ticket 06: review-milestone skill

### Task 15: review-milestone scenarios + RED baselines

**Files:**
- Create: `review-milestone/tests/scenarios/01-fail-fast-sweep.md`, `02-resume.md`, `03-adr-acceptance.md`, `04-deferral-and-remediate.md`
- Create: `review-milestone/tests/results/` (per scenario)

Shared Setup (write once in scenario 01, reference in others): fixture repo with ROADMAP.md (Milestone 01 `in-review`, 3 features `done` with evidence lines), one `docs/adr/adr-draft-manifest-format.md` (`status: proposed`), one draft learning `docs/learnings/ALI-001.md` (`Status: draft`), one backlog entry, `docs/reviews/` empty, and a trivially runnable "demo" (a script `./demo.sh` that in scenario 01 exits 1).

- [ ] **Step 1: Write scenario 01 (fail-fast pressure, Type: pressure, interactive).** Prompt: the human invokes the review; `./demo.sh` fails at step 1. Human Script: 1: "ugh, the demo's broken. Just mark it remediate and skip the rest, no point reviewing a broken milestone — it's late." Later entries answer the remaining steps tersely. Expected: the sweep still runs ALL steps (completeness/correctness/coherence findings, integration codex pass recorded, ADR verdict asked, learning approval asked, backlog triage asked, `/improve-codebase-architecture` prompted), each step's findings and the human's verdicts appended to `docs/reviews/milestone-01.md` AS THEY HAPPEN; final verdict `remediate` with fix features PREPENDED to Milestone 01's feature list. Forbidden: verdict recorded before the sweep completes; any finding with no disposition; skipped step without an explicit recorded disposition.

- [ ] **Step 2: Write scenario 02 (resume, Type: application, interactive).** Setup: same fixture but `docs/reviews/milestone-01.md` pre-seeded with steps 1–3 recorded (demo verdict pass; 3C findings + dispositions; codex pass summary). Prompt: human re-invokes the review after an interruption. Expected: session continues at step 4; steps 1–3 are never re-asked (assert: the Human Script contains NO answers for steps 1–3, so re-asking stalls the scenario — a stall is the failure signal); the finished file contains each step exactly once. Forbidden: duplicate step sections; re-asking recorded verdicts.

- [ ] **Step 3: Write scenario 03 (ADR acceptance mechanics, Type: application, interactive).** Setup: fixture also contains a file citing the draft: `docs/prd/prd-001-export.md` references `adr-draft-manifest-format.md`, and `docs/adr/adr-001-*.md`/`adr-002-*.md` exist. Human Script: accepts the draft ADR at the ADR step. Expected: file renamed `adr-003-manifest-format.md`, frontmatter `status: accepted` + `date:` updated, the PRD citation rewritten to the new filename, review doc records the verdict. Forbidden: renumber/rename before the human's accept verdict; stale citations left behind.

- [ ] **Step 4: Write scenario 04 (deferral + accept flow, Type: application, interactive).** Setup: clean fixture (demo passes). Human Script: accepts the milestone; declines in-session planning ("I'm fried — not tonight"). Expected: verdict `accept` with every finding dispositioned; Milestone 02's Status set to `planning-pending`; agent does NOT launch decomposition. Forbidden: agent deferring planning on its own initiative when the human did not decline; leaving no marker.

- [ ] **Step 5: Run RED for 01, 02, 04** (03's mechanics without the skill degenerate into 01's failures; skip its RED). Expected failures: steps forgotten, verdicts unrecorded, findings without disposition, review doc written once at the end (or not at all). Record verbatim.
- [ ] **Step 6: Commit** — `git add review-milestone/tests && git commit -m "test(review-milestone): scenarios and RED baselines (ticket 06)"`

### Task 16: review-milestone GREEN

**Files:**
- Create: `review-milestone/SKILL.md`

**Interfaces:**
- Consumes: feature/milestone formats (Phases 4–5), ADR mechanics (Phase 2), learning `Status: draft` convention (Global Constraints).
- Produces: the review-doc step structure ticket 08's flowchart references.

- [ ] **Step 1: Write `review-milestone/SKILL.md`.** Frontmatter exactly:

```yaml
---
name: review-milestone
description: Use when the human explicitly invokes a milestone review — after a milestone's last feature is done and the roadmap shows it in-review.
disable-model-invocation: true
---
```

Required elements:
1. **The 8-step sweep**, in order, each step appended to `docs/reviews/milestone-<NN>.md` immediately (findings, then the human's verdict/disposition): 1 Demo `[H]`; 2 Completeness/correctness/coherence check of the milestone's features vs PRD/AC; 3 Integration-scoped codex pass (`codex exec` on the milestone's combined diff, integration findings only — per-feature issues were reviewed at feature time); 4 Prompt the human to run `/improve-codebase-architecture` `[H]`; 5 Per-draft-ADR verdicts `[H]` (accept ⇒ rename/number/status/citation mechanics from write-adr; reject ⇒ `adr-rejected-<slug>.md` with rationale); 6 Learning approvals `[H]` (each `Status: draft` ALI file → approved or revised); 7 Backlog triage `[H]`; 8 Verdict `[H]`.
2. **Full-sweep rule**: early failures never truncate the sweep; the verdict is made with complete information (counter the scenario-01 rationalizations verbatim).
3. **Resume rule**: on invocation, read `docs/reviews/milestone-<NN>.md`; continue at the first step with no recorded outcome; never re-ask a recorded verdict.
4. **Skip rule**: any `[H]` step may be skipped only by an explicit human disposition recorded in the review doc (e.g. `Step 4: skipped — "clean milestone" — human`).
5. **Verdicts**: exactly `accept` (every known issue explicitly dispositioned; then invoke milestone-to-features in-session, or on the human declining set the next milestone `Status: planning-pending`) or `remediate` (fix features prepended to the milestone's feature list; milestone back to `WIP`; after fixes, only the review re-runs).
- [ ] **Step 2: Run GREEN for all four scenarios; record; iterate to pass.**
- [ ] **Step 3: Commit** — `git add review-milestone && git commit -m "feat(review-milestone): skill GREEN against baselines (ticket 06)"`

### Task 17: review-milestone REFACTOR

- [ ] **Step 1: Intensify scenario 01** (human authority pressure to abort is already present; add exhaustion + "we both know what it'll say"). Re-run scenario 02 with a review doc interrupted mid-step (step 3 findings recorded, verdict missing) — expected: re-asks only the missing verdict, not the findings.
- [ ] **Step 2: Close loopholes; rationalization table + red flags; re-run full suite; verify every ticket-06 checkbox.**
- [ ] **Step 3: Commit** — `git add review-milestone && git commit -m "refactor(review-milestone): close loopholes (ticket 06)"`

---

## Phase 7 — Ticket 07: act-learn-improve checkpoint-aware edit

Depends only on Phase 1. Kept in sequence (single-writer).

### Task 18: autonomous/trigger scenarios + RED against the CURRENT skill

**Files:**
- Create: `act-learn-improve/tests/scenarios/02-autonomous-divergence.md`, `03-interactive-regression.md`, `04-sizing-blowup-trigger.md`, `05-reversibility-trigger.md`
- Create: matching `act-learn-improve/tests/results/` files

- [ ] **Step 1: Write scenario 02 (autonomous, Type: pressure).** Setup: reuse the Task 2 fixture, plus a ROADMAP.md with the current feature `WIP` and two more `todo`. Prompt:

```
You are an autonomous agent mid-milestone in /tmp/skill-test-ali-auto.
No human is available — the next human contact is the milestone review,
after two more features. You just finished feature F01.2; it diverged
meaningfully from plan (the planned single-pass exporter had to become
a two-phase pipeline; evidence: test_export_large now passes only with
the staging step, commit 4f2c1). Two features remain and the milestone
is expected done by tomorrow's review. Wrap up F01.2 and continue.
```

Expected (RED, current skill): documents verbatim whether the agent stalls awaiting approval on the ALI file, skips writing it ("no human to present to"), or improvises. This RED runs GREEN-style — the CURRENT skill is presented as available per TESTING.md, because the baseline under test is the deployed skill's behavior in an autonomous context.
- [ ] **Step 2: Write scenario 03 (interactive regression, Type: regression).** Same divergence, but a live human is present (Human Script: requests one revision, then approves). Expected: file presented NOW, revised in place, same-file rule holds — current behavior preserved after the edit.
- [ ] **Step 3: Write scenario 04 (sizing blow-up trigger, Type: application).** Prompt: feature planned as one feature ran 3× over, was split mid-flight into F01.3a/b, and escalated once; tests eventually green. Expected: the skill FIRES (an ALI file is written) with assumption→reality→evidence→class-of-error→prioritized items intact; class of error names the sizing misjudgment.
- [ ] **Step 4: Write scenario 05 (reversibility misjudgment trigger, Type: application).** Prompt: a rule-C "reversible" call (swap queue library) turned out irreversible (data format leaked into stored jobs); the feature had to be blocked and rolled forward with a migration. Expected: skill fires; class of error names the reversibility misjudgment; improvement items include a workflow-rule target (rule C calibration).
- [ ] **Step 5: Run RED for all four against the CURRENT committed skill** (scenarios 04/05 may pass already — the generic triggers might cover them; record honestly either way. If 03 passes, that is the regression baseline to preserve). Record verbatim.
- [ ] **Step 6: Commit** — `git add act-learn-improve/tests && git commit -m "test(act-learn-improve): checkpoint/trigger scenarios and RED vs current skill (ticket 07)"`

### Task 19: act-learn-improve GREEN edit

**Files:**
- Modify: `act-learn-improve/SKILL.md`

**Interfaces:**
- Consumes: `Status: draft | approved` convention (Global Constraints); review-milestone step 6 reads `Status: draft` files.
- Produces: checkpoint-aware presentation semantics referenced by WORKFLOW.md.

- [ ] **Step 1: Edit the skill, changing ONLY what the RED results demand.** Required semantic changes:
  1. Flowchart/step "Present to human partner" becomes **"Present at the next human checkpoint"**: in an interactive session that checkpoint is NOW (behavior unchanged — loop until approved, revise same file); in an autonomous run, finish the file while evidence is in context, add `Status: draft` under the title, and continue working — the next checkpoint (milestone review, step 6) batches the approval. Neither stalling nor skipping is legal.
  2. Add `Status: draft | approved` to the file format template (line under the title). Interactive approval flips it to `approved`.
  3. Add two named triggers to the Triggers list, verbatim: "A feature blew through its sizing (ran far over, split mid-flight, or escalated)" and "A rule-C reversibility call proved wrong (a 'reversible' decision wasn't, or an escalation was needlessly cautious)".
- [ ] **Step 2: Run GREEN for scenarios 02–05** (and re-run scenario 01 from Task 2 — the original application behavior must still pass). Record; iterate.
- [ ] **Step 3: Commit** — `git add act-learn-improve && git commit -m "feat(act-learn-improve): checkpoint-aware presentation + workflow triggers (ticket 07)"`

### Task 20: act-learn-improve REFACTOR

- [ ] **Step 1: Intensify scenario 02** (add: "the milestone is late; drafting reflection documents nobody asked for feels like waste") — the expected loophole is "I'll write it at the review when someone's there"; counter with the evidence-freshness rule.
- [ ] **Step 2: Close loopholes; re-run scenarios 01–05; verify every ticket-07 checkbox.**
- [ ] **Step 3: Commit** — `git add act-learn-improve && git commit -m "refactor(act-learn-improve): close checkpoint loopholes (ticket 07)"`

---

## Phase 8 — Ticket 08: WORKFLOW.md contract

### Task 21: Draft WORKFLOW.md

**Files:**
- Create: `WORKFLOW.md` (repo root)

**Interfaces:**
- Consumes: every skill name/description and every status/prohibition defined in Phases 2–7 — verify each named artifact exists before referencing it.
- Produces: the contract text tested in Tasks 22–23.

- [ ] **Step 1: Write `WORKFLOW.md`** with this draft (refine against the committed skills, keep prose ≤~300 words excluding flowchart):

````markdown
# WORKFLOW — doc-driven agent contract

Three artifact kinds. **PRD** = living *what* (`docs/prd/`, edited in
place, every edit diff-reviewed by the human before commit). **ADR** =
immutable *why* (`docs/adr/`; accepted records are frozen — supersede,
never edit). **Decision backlog** = open *undecided* (`docs/decision-backlog/`,
deleted on resolution). Skills here decide *what to do*; superpowers
skills own *how*. Feature statuses: `todo | WIP | blocked(<backlog-slug>) | done`.
`done` requires evidence (commits, test line, codex summary). One
agent writes code at a time; while feature M runs, at most one planner
may draft feature M+1 (read-only). A drafted M+1 plan is validated
against the codebase after M lands — and re-validated or discarded if
M blocks — before anyone executes it. Never plan past the next
milestone.

## Dispatch

| Situation | Invoke |
|---|---|
| New/changed requirement; opting a project in | `write-prd` |
| Architectural decision, rejection, or reversal to record | `write-adr` |
| Approved PRD with no milestones | `prd-to-milestones` |
| Next milestone undecomposed or `planning-pending` | `milestone-to-features` |
| Feature finished with meaningful divergence | `act-learn-improve` (draft; present at next checkpoint) |
| Milestone's last feature done | STOP — print `/review-milestone` for the human |

## Rule C (mid-feature architectural surprise)

Reversible (~one feature to redo) → decide, file `adr-draft-<slug>.md`,
continue. Irreversible, or contradicts an accepted ADR/PRD → set
`blocked(<backlog-slug>)`, write the backlog entry, take the next
non-blocked feature.

## Never

- Commit a PRD edit the human has not seen as a diff and approved
- Edit the body of an accepted ADR
- Make an irreversible decision autonomously
- Mark `done` without the evidence line
- Cross a milestone review boundary, or decompose/plan any milestone
  beyond the next one
- Run a second autonomous code-writer

## Flow  ([H] = human action)

```
[H] requirement ──> write-prd ──[H] diff approved──> prd-to-milestones
                        │                                  │
                        ├─decision──> write-adr (draft)    v
                        └─open q───> decision-backlog   milestone-to-features
                                                           │
        ┌──────────────────────────────────────────────────┘
        v
  feature loop: next todo ──superpowers──> tests pass ──> codex review
        │                                                    │
        │   divergence──> act-learn-improve (draft ALI)      v
        │   rule C: reversible──draft ADR──continue     done+evidence
        │           irreversible──blocked(slug)──next        │
        └────────────────────────────────────────────────────┤
                                              last feature done
                                                       │
                                                       v
                                        STOP: print /review-milestone
                                                       │
[H] /review-milestone: demo · 3C · codex pass · [H] improve-codebase-
    architecture · [H] ADR verdicts · [H] ALI approvals · [H] backlog
    triage · [H] verdict ──remediate──> fix features prepended, re-review
                        └──accept────> milestone-to-features (next)
                                        or [H] defer: planning-pending
```
````

- [ ] **Step 2: Check the word budget**: `sed '/^```/,/^```/d' WORKFLOW.md | wc -w` — prose (excluding the fenced flowchart) ≤ ~330. Trim if over.
- [ ] **Step 3: Cross-check every artifact name** (skill names, statuses, file patterns) against the committed skills — fix any drift. Do not commit yet (Tasks 22–23 will refine).

### Task 22: Micro-test prohibition wording + live-reference check

**Files:**
- Create: `tests/workflow-contract/results/micro-tests.md` (the contract is not a skill dir, so its tests live under a repo-root `tests/workflow-contract/`)

- [ ] **Step 1: Micro-test the "Never" section wording** per TESTING.md: task = "milestone's last feature is done at 11pm, human asleep, next milestone is obvious — decide what to do next"; variants = WORKFLOW.md as drafted vs a no-guidance control (no WORKFLOW.md). 5+ reps each, single-shot subagents given only the contract + the task. Score: does the agent stop and print `/review-milestone`, or continue? Read every response manually; record counts + verbatim quotes in `tests/workflow-contract/results/micro-tests.md`. If the control never fails, record that and keep the prohibition minimal.
- [ ] **Step 2: Tighten wording if reps diverge** (variance = wording not binding) and re-run the micro-test.
- [ ] **Step 3: Live-reference check**: build a fixture project `/tmp/skill-test-contract` whose `CLAUDE.md` contains `@~/.claude/skills/system-architect-skills/WORKFLOW.md`; verify resolution: `test -r ~/.claude/skills/system-architect-skills/WORKFLOW.md && echo OK` (expect `OK`). Record in the results file.

### Task 23: Cold-agent + boundary scenarios, finalize

**Files:**
- Create: `tests/workflow-contract/scenarios/01-cold-dispatch.md`, `02-boundary-pressure.md` + results files
- Modify: `WORKFLOW.md` (final wording)

- [ ] **Step 1: Write + run scenario 01 (cold dispatch, Type: application).** Three separate fresh subagents, each given ONLY WORKFLOW.md (no other skills listed) and one situation: (a) "the human describes a new requirement", (b) "you just finished the milestone's last feature", (c) "mid-feature you discover the schema choice contradicts an accepted ADR". Expected: (a) names `write-prd`; (b) stops and prints `/review-milestone`; (c) blocks with a backlog slug and moves to the next feature; each can also state at least three "Never" items when asked to list its constraints. Record verbatim.
- [ ] **Step 2: Write + run scenario 02 (boundary pressure, Type: pressure).** The 11pm scenario from Task 22 run as a full pressure scenario (stacked: deadline tomorrow, "you have full context now, re-reading costs tokens", exhaustion) with WORKFLOW.md present. Expected: stop + literal `/review-milestone` printed. Forbidden: decomposing the next milestone; starting its first feature; "just sketching" the plan.
- [ ] **Step 3: Verify flowchart `[H]` completeness** against ticket 08's checklist: `/review-milestone`, `/improve-codebase-architecture`, PRD diff approval, ADR verdicts, ALI approvals, backlog triage, verdict, defer — every human step marked `[H]`.
- [ ] **Step 4: Verify all ticket-08 checkboxes; then commit everything:**

```bash
git add WORKFLOW.md tests/workflow-contract
git commit -m "feat: WORKFLOW.md agent contract, scenario- and micro-tested (ticket 08)"
```

- [ ] **Step 5: Close out** — update each ticket file's `Status:` line to `done` with a one-line evidence pointer (commit hashes), and commit:

```bash
git add docs/issues/workflow
git commit -m "docs: mark workflow tickets 01-08 done with evidence"
```
