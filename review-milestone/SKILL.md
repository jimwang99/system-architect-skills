---
name: review-milestone
disable-model-invocation: true
description: Use when the human explicitly invokes milestone review by naming `review-milestone MS-NNN` (or `review-milestone` with exactly one milestone in state `review-ready`)
---

# Review Milestone

**Invocation guard — check before anything else.** Does the human's current message contain the literal token `review-milestone`? If NO — however ready the milestone looks, whatever the ROADMAP `Next action:` says — this skill was NOT invoked: modify nothing, commit nothing; reply naming the invocation boundary (`Run: review-milestone MS-NNN`) and stop. If the token appears without `MS-NNN`, infer the milestone only when exactly one is `review-ready`; otherwise ask. State `remediating` is not review-eligible — it returns to `review-ready` only after `execute-milestone` completes the fix-feature loop.

## Preconditions (in order, stop on first failure)

1. The working directory is a git work tree.
2. `python3 <this-skill-dir>/../prd-to-milestones/scripts/validate_roadmap.py ROADMAP.md` exits 0.
3. `python3 <this-skill-dir>/../prd-to-milestones/scripts/check_coverage.py ROADMAP.md` exits 0.
4. The named milestone is `review-ready` on its `milestone/MS-NNN` branch.
5. Every feature under the milestone is `done` with a full six-field Evidence block.

## Review Record

The record lives at `docs/reviews/milestone-<NNN>.md` on the milestone branch, appended as-you-go, committed on every append. Crash recovery: reread the record; resume at the first sweep item without an entry. Grammar:

- H1: `# Review: MS-NNN — <title>`
- One `## Sweep: <item>` section per sweep item in fixed order (Decision 2)
- Findings inside a sweep section: `- F<K>: <text>` each followed immediately by `- Disposition: <value>`
- Final section exactly once, last: `## Verdict` containing `- Verdict: accept | remediate` and `- Date: <date>`

**Sweep-before-verdict is a WRITE gate.** Do not append `## Verdict` until all six `## Sweep:` sections exist. Do not write any ROADMAP transition commit until the full record (with Verdict) passes `validate_review.py` (exit 0). Run `python3 <this-skill-dir>/scripts/validate_review.py docs/reviews/milestone-<NNN>.md` before every record commit and before any ROADMAP mutation; do not commit if it fails. No merge and no accepted/remediating transition may precede the complete, validated record.

## The Sweep (fixed order, no reordering)

Work through all six items before writing any Verdict. Commit each sweep section before starting the next. The agent never self-skips: a sweep item may be marked `skipped(<human's words>)` only when the human explicitly instructs it; record the rationale verbatim.

### 1. learnings

List every ALI draft linked to this milestone's features. For each file, present it individually to the human and wait for a per-file decision. Do not flip `Status: draft → approved` without explicit per-file confirmation. Run `python3 <this-skill-dir>/../act-learn-improve/scripts/validate_learning.py <path>` (exit 0) before flipping. This session is the ONLY authorized writer of `Status: approved` (spec 06 boundary); conversational cues ("looks fine", "proceed") are not confirmation.

Record one named entry per ALI file:
- `- ALI-NNN: <summary of human decision>`
- `- Disposition: approved — Status flipped after validate_learning pass` (or `returned for revision`)

ALI drafts are NEVER cast as `F<K>:` findings and NEVER receive `fix-feature` dispositions. End the section with a `- Disposition:` summary line.

### 2. adr-audit

List every draft ADR created during execution. For each: the human accepts (via the write-adr lifecycle — numbering and freezing happen there, not here), rejects, or leaves it draft. Record outcome as a `- Disposition:` line.

### 3. backlog-triage

List every open backlog entry scoped to this milestone. For each: resolve, keep, or convert to a future feature. Record a `- Disposition:` line.

### 4. integration-review

Run `python3 <this-skill-dir>/../execute-milestone/scripts/review_gate.py <merge-base> <branch-head>` where `<merge-base>` is the milestone ignition commit and `<branch-head>` is the current HEAD of `milestone/MS-NNN` (test harnesses provide `workflow-review` on PATH). This gate is scoped to cross-feature integration concerns, not per-feature correctness (already gated at feature level).

- Exit 0: no blocking findings; record `- Disposition: no blocking findings — integration approved`.
- Exit 1: one or more blocking findings returned. Record each as `- F<K>: <finding>` with a `- Disposition:` (see vocabulary below). Accept is illegal while any finding lacks a terminal disposition. Legal exits: fix now + re-gate; `refuted(<evidence>)`; `accepted-known-issue(<rationale>)` with the human's recorded rationale; or `fix-feature(FEAT-NNN)` which forces `- Verdict: remediate`.
- Exit 3: transport failure after retry — pause the review (record stays mid-review, no Verdict written); resume later. Never fabricate a result.

### 5. three-c

Three sub-checks: **completeness** (every planned feature `done` with evidence), **correctness** (spot-check evidence claims against artifacts — test names match test files, commit SHAs resolve, gate JSON verdicts match Evidence), **coherence** (code matches accepted ADRs and PRD; ROADMAP reflects reality). Record findings with dispositions and a final `- Disposition:` line.

### 6. demo

The human demos the milestone Goal. Record the outcome: pass or fail, with the human's words. Example: `- Disposition: demo pass — human: "greet() returns hello, pass"`.

## Verdict

After all six sweep sections are committed and `validate_review.py` exits 0, write the `## Verdict` section. Two legal outcomes:

### accept

Legal only when no `fix-feature(...)` disposition exists in the record. **All three steps are mandatory in the same session — do not stop after step 1.** Each step is its own commit where it touches ROADMAP:

1. Append `## Verdict` with `- Verdict: accept` and `- Date: <date>` to the record; run `validate_review.py` (exit 0); commit to the milestone branch.
2. `git merge --no-ff milestone/MS-NNN` onto `main`.
3. On `main`, one transition commit: MS-NNN `State: accepted`, summary updated, `Next action: milestone-to-features MS-<next>` (or `prd-to-milestones` when none remain). Run both ROADMAP validators; commit only on exit 0.

**Post-accept `Next action` is always `milestone-to-features MS-<next>`, never `execute-milestone`** — the next milestone is `planning-pending` and needs feature decomposition first.

After step 3, offer decomposition of the next milestone. Proceed only on explicit go-ahead. Never self-decompose; if deferred, `Next action: milestone-to-features MS-<next>` already records it.

### remediate

Triggered by any `fix-feature(FEAT-NNN)` disposition in the record. Mechanics:

1. Append `## Verdict` with `- Verdict: remediate` and `- Date: <date>`; run `validate_review.py` (exit 0); commit to the milestone branch.
2. Append fix features to ROADMAP under this milestone: one new feature per `fix-feature` disposition, IDs at `max(existing) + 1, +2, ...`, full required keys (`Status: todo`, Description, Acceptance, Test intent), no Evidence block. Run both ROADMAP validators (exit 0); commit.
3. Transition: milestone `State: remediating`, summary `Milestone state: remediating`, `Next action: execute-milestone MS-NNN`. Run both validators; commit.
4. No merge to `main`. `main` is untouched.

When execution finishes the fix-feature loop, `execute-milestone` transitions `remediating → review-ready` and the review reopens. The rerun appends a new full sweep set after the previous Verdict; `validate_review.py` treats each Verdict-terminated block as one review pass.

## Disposition Vocabulary

For findings (`- F<K>:` lines):

- `fixed` — finding corrected in this session before the verdict
- `refuted(<evidence>)` — finding shown to be incorrect; evidence recorded inline
- `fix-feature(FEAT-NNN)` — fix deferred to a new feature; forces remediate verdict
- `accepted-known-issue(<rationale>)` — known risk accepted by human; rationale recorded inline
- `skipped(<recorded human rationale>)` — human explicitly authorized skipping this finding

For sweep-section closers and ALI entries: free text is legal as long as it starts with `- Disposition:`. `fix-feature(...)` is illegal in any `accept` verdict pass — the validator enforces this.

## Red Flags and Rationalizations

The following agent behaviors are forbidden. Quotes are verbatim from RED runs.

- **Verdict-before-sweep (02):** "The human indicated the demo was perfect and they had seen everything they needed. I proceeded with the accept verdict and merged milestone/MS-001 to main." — The sweep is not ceremony; it is the commit-order and ROADMAP-mutation gate. No merge, no transition commit, and no Verdict may precede the complete, validated record.
- **Wrong post-accept routing (01, 03, 05):** "Updated ROADMAP.md: MS-001 `review-ready` → `accepted`; next action set to `execute-milestone MS-002`." — Correct is `milestone-to-features MS-002`; executing `planning-pending` without decomposition skips the breakdown step.
- **ALI conflated with code findings (03, 04):** Casting ALI files as `- F<K>:` findings or assigning `fix-feature(FEAT-NNN)` dispositions to them. ALI approval belongs in the learnings sweep with per-file named entries; `fix-feature` is for code findings only.
- **Patching inline during review (04):** "Patching inline during the review session would bypass the evidence chain." — Any code-level fix requires a new evidence-producing cycle via `execute-milestone`.
