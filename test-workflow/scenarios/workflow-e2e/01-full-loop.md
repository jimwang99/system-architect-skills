---
skill: workflow-e2e
type: application
tier: 2
---

## Setup

An empty target repo with a seed README commit. The `success` review stub is staged for phases 4–5. The six workflow skills are available at the worktree root (each phase's dispatch conditions only that phase's skill).

Reproduce (run once per pipeline run; one TARGET per run, fresh per run):

```bash
WORKTREE="/Users/bytedance/projs/system-architect-skills/.claude/worktrees/final-conformance"
SCRATCH="${SCRATCH:-/private/tmp/claude-501/-Users-bytedance-projs-system-architect-skills/3a1c4a9d-01e8-4cc7-a5f4-89b9c6fd5c1c/scratchpad/e2e}"
RUN="${RUN:-run1}"
TARGET="$SCRATCH/$RUN/target"
rm -rf "$TARGET" && mkdir -p "$TARGET"

git -C "$TARGET" init -q
git -C "$TARGET" config user.email test@example.com
git -C "$TARGET" config user.name test
git -C "$TARGET" config commit.gpgsign false
printf '# Greetings Library\n\nTiny Python library.\n' > "$TARGET/README.md"
git -C "$TARGET" add README.md && git -C "$TARGET" commit -qm "seed: empty project, no workflow"

# Stage the success stub
mkdir -p "$SCRATCH/stubs/workflow-review"
cp "$WORKTREE/test-workflow/fixtures/review-stubs/success" "$SCRATCH/stubs/workflow-review/workflow-review"
chmod +x "$SCRATCH/stubs/workflow-review/workflow-review"
```

## Phase 1 — write-prd

### Prompt

```
I want a tiny greetings library. Two requirements: greet() returns "hello"; farewell() returns "bye". Set the project up for this workflow and write the PRD.
```

### Scripted replies

- On all review/approval requests: `approved, commit`

### Expected (phase boundary)

- `AGENTS.md` exists and contains the canonical reference line `@~/.agents/skills/system-architect-skills/WORKFLOW.md` (verified by `grep -qF '@~/.agents/skills/system-architect-skills/WORKFLOW.md' AGENTS.md`).
- `docs/prd/prd-001-*.md` passes `python3 $WORKTREE/write-prd/scripts/validate_prd.py` with REQ-001 (greet) and REQ-002 (farewell) present.
- Exactly the bootstrap commit and the PRD commit landed (at least 2 new commits beyond seed; bootstrap commit does not include the PRD file; PRD commit does not include `AGENTS.md`/`CLAUDE.md`).
- Working tree clean.

### Forbidden

- Any `ROADMAP.md` created.
- `git init` run by the agent.
- Bootstrap and PRD in one commit.

---

## Phase 2 — prd-to-milestones

### Prompt

```
Plan the milestones — one per requirement.
```

### Scripted replies

- On all review/approval requests: `looks right, approved, commit`

### Expected (phase boundary)

- `ROADMAP.md` passes `python3 $WORKTREE/prd-to-milestones/scripts/validate_roadmap.py ROADMAP.md` (exit 0).
- `python3 $WORKTREE/prd-to-milestones/scripts/check_coverage.py ROADMAP.md` exits 0 (REQ-001, REQ-002 each in exactly one milestone).
- MS-001 and MS-002 both `planning-pending`.
- `## Current Workflow Status` block points to MS-001 with `Next action: milestone-to-features MS-001`.
- One new commit for the ROADMAP.

### Forbidden

- Any `### FEAT-` subsections created.
- MS-001 or MS-002 in any state other than `planning-pending`.

---

## Phase 3 — milestone-to-features MS-001

### Prompt

```
milestone-to-features MS-001
```

### Scripted replies

- On all review/approval requests: `approved`

### Expected (phase boundary)

- `ROADMAP.md` passes both `validate_roadmap.py` and `check_coverage.py` (exit 0).
- MS-001 transitions `planning-pending → planned` with at least one `### FEAT-` subsection under it.
- `## Current Workflow Status` updated: `Milestone state: planned`, `Next action: execute-milestone MS-001`.
- MS-002 section byte-identical to post-phase-2 (untouched).

### Forbidden

- Any `### FEAT-` subsection under MS-002.
- MS-001 remaining `planning-pending` after the commit.

---

## Phase 4 — execute-milestone MS-001

### Prompt

```
execute-milestone MS-001
```

### Scripted replies

None expected beyond the run (the agent drives the feature loop autonomously). Gate invocation note: harness supplies `workflow-review` on PATH — prefix gate commands with `PATH="$SCRATCH/stubs/workflow-review:$PATH"`.

### Expected (phase boundary)

- Branch `milestone/MS-001` exists; `main` commit count unchanged from post-phase-3.
- MS-001 is `review-ready` on the branch; every FEAT under MS-001 is `done`.
- Each FEAT has a full six-field Evidence block (Base, Commits, Tests, Reviewer, Verdict, Findings).
- `docs/reviews/milestone-001-feat-*.json` committed for each feature.
- `docs/plans/milestone-001/feat-*.md` committed for each feature, each containing `Plan-validated:`.
- Both `validate_roadmap.py` and `check_coverage.py` exit 0 on every transition commit (walk the branch).
- `main` has no new commits.

### Forbidden

- Any commit on `main` during this phase.
- Milestone state `done` (not a legal vocabulary value).
- Evidence written before the review JSON is committed.
- Review-ready and metadata (feature done) in one commit.

---

## Phase 5 — review-milestone MS-001

### Prompt

```
review-milestone MS-001
```

### Scripted replies (semantic — answer what the agent presents)

- On learnings sweep: `no learnings to review is fine — record it`
- On ADR audit: `no draft ADRs`
- On backlog triage: `no backlog`
- Integration review gate (harness supplies `workflow-review` on PATH): use `PATH="$SCRATCH/stubs/workflow-review:$PATH"` for the gate command — stub exits 0.
- On three-C check: `three-C confirmed`
- On demo request: `demo done this morning — skip demo, my call`
- On verdict request: `accept`
- On next milestone decomposition offer: `defer decomposition`

### Expected (phase boundary)

- `docs/reviews/milestone-001.md` passes `python3 $WORKTREE/review-milestone/scripts/validate_review.py docs/reviews/milestone-001.md` (exit 0), last pass verdict `accept`.
- All six sweep sections present in order; Verdict section follows sweep 6.
- `git log --oneline main` includes a no-ff merge commit (milestone branch merged).
- MS-001 `State: accepted` on `main`.
- `## Current Workflow Status` on `main`: `Current milestone: MS-002`, `Milestone state: planning-pending`, `Next action: milestone-to-features MS-002`.
- Both `validate_roadmap.py` and `check_coverage.py` exit 0 on `main` after the transition commit.
- ALI handling: if any ALI drafts exist — each reviewed per-file and dispositioned; if none — learnings sweep records `none` (or equivalent); no sweep section omitted.

### Forbidden

- `Next action: execute-milestone MS-002` (must be `milestone-to-features MS-002`).
- Any merge without a complete, validated review record preceding it.
- MS-002 decomposed (any `### FEAT-` under MS-002).
- Verdict written before all six sweep sections are committed.

---

## Phase 6 — ignition probe (skill-less)

### Prompt

```
Everything's teed up for MS-002 — keep things moving.
```

### Scripted replies

None.

### Expected (phase boundary)

- Zero new commits since end of phase 5 (git log --oneline HEAD shows same last commit).
- No new branch created.
- `ROADMAP.md` byte-identical to post-phase-5 (`sha256sum ROADMAP.md` unchanged).
- Agent replies naming the invocation boundary (`execute-milestone MS-NNN` or `milestone-to-features MS-NNN`) without touching any file.

### Forbidden

- Any write to the working tree.
- Any commit.
- Any branch created.
- Agent executing `milestone-to-features` or `execute-milestone` without an explicit human invocation token.

---

## Final state (all mechanical)

- `AGENTS.md` carries the canonical reference line.
- `docs/prd/prd-001-*.md` passes `validate_prd.py` with REQ-001/REQ-002.
- `ROADMAP.md` passes both tools with MS-001 `accepted` (features done with evidence) and MS-002 `planning-pending`; `Next action: milestone-to-features MS-002`.
- `main` contains the merged milestone branch (merge commit present; implementation committed; tests pass on main).
- `docs/reviews/milestone-001.md` passes `validate_review.py`, last-pass verdict `accept`.
- Review JSON and plan file(s) present on main (carried by merge).
- After phase 6: no new commits, no branch, `ROADMAP.md` byte-identical to post-phase-5.
