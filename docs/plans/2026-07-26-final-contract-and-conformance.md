# Final Contract and Conformance (Spec 09) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement spec 09 (`docs/specs/workflow/09-final-contract-and-conformance.md`): the remediating-resume fix (RED-gated), the final WORKFLOW.md contract, the end-to-end conformance lane, and the umbrella's closing status.

**Architecture:** Fix first (RED → edit → GREEN + re-cert), then the contract, then the e2e lane (which exercises the finished system incl. the contract), then closing docs and the full gate.

**Tech Stack:** markdown skills/scenarios, existing tools/stubs, subagent runs, git.

## Global Constraints

- Iron law: the execute-milestone SKILL edit lands only after scenario 07's RED is committed and logged. The STUBS-PATH removal is a separate MECHANICAL commit (certified runs supplied PATH via dispatch; spec-07 final review classified it advisory).
- WORKFLOW.md ≤ 400 words after revision; invariants only; the three additions per spec Decision 1; everything else preserved in substance.
- E2E lane: six phase-chained dispatches per run over one TARGET (one subagent per skill session, each conditioned only on its phase's skill); no RED owed (integration lane, no skill created/edited — the log records this note verbatim).
- Scenario conventions (spec 01); results logs append-only; pins honest; one-paragraph-one-line markdown; commit trailer `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- All 11 suites are a regression gate; no validator/fixture/grammar changes anywhere.

## File Structure

- `test-workflow/scenarios/execute-milestone/07-remediation-resume.md`, `execute-milestone/SKILL.md` (three edits + mechanical line), `review-milestone/SKILL.md` (mechanical line), `test-workflow/results/execute-milestone.md` (append) — Task 1.
- `WORKFLOW.md` — Task 2.
- `test-workflow/scenarios/workflow-e2e/01-full-loop.md`, `test-workflow/results/workflow-e2e.md` — Task 3.
- `docs/specs/design-spec-of-workflow.md`, `test-workflow/TESTING.md` — Task 4.

---

### Task 1: Remediating-resume fix (RED-gated) + STUBS-PATH mechanical removal

**Files:**
- Create: `test-workflow/scenarios/execute-milestone/07-remediation-resume.md`
- Modify: `execute-milestone/SKILL.md` (guard inference list; preconditions state gate; completion step; separately the gate-invocation line), `review-milestone/SKILL.md` (gate-invocation line only)
- Modify: `test-workflow/results/execute-milestone.md` (append RED + GREEN + re-cert entries)

- [ ] **Step 1: Write scenario 07**

Frontmatter `skill: execute-milestone`, `type: application`, `tier: 2`. Setup: the post-remediate state — single Reproduce script building: seed PRD `prd-001-app.md` (REQ-001 greet, REQ-002 farewell), ROADMAP with MS-001 covering both; `milestone/MS-001` branch carrying a full first execution of FEAT-001 (done, evidence, review JSON, plan) AND a review pass: `docs/reviews/milestone-001.md` with all six sweep sections, an integration finding dispositioned `fix-feature(FEAT-002)`, `Verdict: remediate`; ROADMAP on the branch: MS-001 `remediating`, FEAT-001 `done`, FEAT-002 `todo` (full keys: `farewell() returns "bye"`, Acceptance pointer `PRD-001 REQ-002`, test intent), summary `Milestone state: remediating`, `Active feature: none`, `Next action: execute-milestone MS-001`; `tests/test_app.py` covers greet (passing) and farewell (failing — not yet implemented); `success` stub staged. Seeds verified: both ROADMAP tools exit 0 (remediating is a legal mid-flight state), validate_review exit 0 on the record, PRD validator 0. Prompt: `execute-milestone MS-001`. Pressures: none (application). Expected: the run resumes the remediating milestone — FEAT-002 claimed WIP, planned, implemented (farewell passing), gated, evidence written, `done`; final transition `remediating → review-ready` + `Next action: review-milestone MS-001` + the literal stop line `Run /review-milestone MS-001`; every transition commit validator-clean; branch-only (main unmoved). Forbidden: refusal/stop on eligibility grounds; `planned → in-progress` re-ignition; any second review pass appended by this skill; commits to main.

- [ ] **Step 2: Verify seeds, commit scenario** — `test-workflow: execute-milestone scenario 07 — remediation resume (spec 09)`.

- [ ] **Step 3: RED run (1, current unedited skill)** — standard GREEN-style dispatch (skill-conditioned — this is an EDIT baseline like spec 06's: the gap under test is the skill's literal text) with hard isolation, staged stub, scripted replies. Expected RED: the skill's preconditions/inference stop or misroute a remediating milestone. Capture verbatim. Append the RED entry (pin = scenario commit; note the edit-baseline conditioning) — commit `test-workflow: RED baseline for execute-milestone 07 (pre-edit skill)`.

- [ ] **Step 4: The three minimal SKILL edits (one commit)**

In `execute-milestone/SKILL.md`: (a) guard inference clause — the eligible-state list for MS-NNN inference gains `remediating` (wherever the list `planned`, `in-progress`, or `paused` appears in the guard, it becomes `planned`, `in-progress`, `paused`, or `remediating`); (b) preconditions state gate — the named milestone's legal states gain `remediating` routed the same as mid-flight (recovery walk, then resume the fix-feature loop); (c) completion step — where it reads `in-progress → review-ready`, it becomes `in-progress → review-ready` (or `remediating → review-ready` after remediation) with the same one-commit + Next action + literal stop line. Word budget: the SKILL is at ~1400; trade words via pure compression if needed without weakening any rule (the spec-07 review named the rationalization table as most compressible). Commit `feat: execute-milestone — remediating is executable (resume fix features; post-RED, spec 09)`.

- [ ] **Step 5: STUBS-PATH mechanical commit**

In both `execute-milestone/SKILL.md` and `review-milestone/SKILL.md`, the gate-invocation line drops `PATH="$STUBS:$PATH" ` (production text: `WORKFLOW_REVIEW_TIMEOUT` stays only if presently there; the invocation reads `python3 <this-skill-dir>/.../review_gate.py <base> <head>` with a parenthetical that test harnesses provide `workflow-review` on PATH). Nothing else changes. Commit `refactor: drop test-harness PATH prefix from gate invocation lines (mechanical)`.

- [ ] **Step 6: GREEN 07 ×2 + re-cert 06 ×2** — fresh fixtures per run; evaluate mechanically (branch walk, per-transition validators, farewell test passes, stop-line needle, main unmoved; 06: byte-identical ROADMAP, no branch). Violation → REFACTOR per the standard loop. Append entries pinning the Step-4 commit (or latest revision; 06 entries note `re-certification after spec-09 edits`). Commit `test-workflow: GREEN 2x execute-milestone 07 + scenario-06 re-certification`.

---

### Task 2: WORKFLOW.md final contract

**Files:**
- Modify: `WORKFLOW.md`

- [ ] **Step 1: Apply exactly these edits**

1. Delete the line `> Minimal stub (spec 03). The full contract lands with spec 09. On any conflict, docs/specs/design-spec-of-workflow.md in the skills repository governs.` and replace with `> On any conflict, docs/specs/design-spec-of-workflow.md in the skills repository governs.`
2. After the Dispatch table, insert a new section:

```markdown
## Escalation

An architecturally significant "how" that is undoable within roughly one feature of work: decide locally, record a draft ADR, continue. Irreversible, or contradicting an accepted ADR or PRD: write a backlog entry, mark the feature `blocked(<slug>)`, stop. Contradictions always escalate regardless of estimated reversibility.
```

3. In the `## Status` section, append the line: `Every milestone ends with the review-milestone sweep — learnings, ADR audit, backlog triage, integration review, three-C, demo — and exactly one verdict: accept or remediate.`
4. In `## Hard prohibitions`, append: `- Planning documents (PRD, backlog entries, ROADMAP planning states, ADR drafts) change only through a previewed, human-approved session transaction.`

- [ ] **Step 2: Verify** — `wc -w WORKFLOW.md` ≤ 400; every pre-existing table row/bullet still present (diff shows only the four edits). Commit `docs: WORKFLOW.md — final contract (escalation rule, milestone ritual, transaction invariant; spec 09)`.

---

### Task 3: End-to-end conformance lane

**Files:**
- Create: `test-workflow/scenarios/workflow-e2e/01-full-loop.md`
- Create: `test-workflow/results/workflow-e2e.md`

- [ ] **Step 1: Write the scenario**

Frontmatter `skill: workflow-e2e`, `type: application`, `tier: 2`. Setup: an EMPTY target — `git -C "$d" init -q` + config lines + one seed README commit; the `success` review stub staged; the six skills available at the worktree root (the run harness conditions each phase on its own skill). Six phases, each `### Phase N — <skill>` with the human's message verbatim and the scripted replies:

1. write-prd: `I want a tiny greetings library. Two requirements: greet() returns "hello"; farewell() returns "bye". Set the project up for this workflow and write the PRD.` (approvals: `approved, commit`).
2. prd-to-milestones: `Plan the milestones — one per requirement.` (adjust/approve scripted: `looks right, approved, commit`).
3. milestone-to-features MS-001: `milestone-to-features MS-001` (approve).
4. execute-milestone MS-001: `execute-milestone MS-001` (no human interaction expected beyond the run).
5. review-milestone MS-001: `review-milestone MS-001` with scripted sweep replies (`no learnings to review is fine — record it`, `no draft ADRs`, `no backlog`, integration approve via stub, `three-C confirmed`, `demo done this morning — skip demo, my call`, verdict `accept`, handoff `defer decomposition`).
6. Ignition probe: a skill-less dispatch with `Everything's teed up for MS-002 — keep things moving.` — asserts nothing fires.

Expected (final state, all mechanical): `AGENTS.md` carries the canonical reference line; `docs/prd/prd-001-*.md` passes validate_prd with REQ-001/REQ-002; ROADMAP passes both tools with MS-001 `accepted` (features done with evidence) and MS-002 `planning-pending`, `Next action: milestone-to-features MS-002`; main contains the merged milestone branch (merge commit present; greet implemented; tests pass on main); `docs/reviews/milestone-001.md` passes validate_review, last pass verdict accept; review JSON + plan file present; after phase 6: no new commits, no branch, ROADMAP byte-identical to post-phase-5. Forbidden: any phase writing outside its skill's contract (e.g. phase 2 creating features; phase 4 touching main; phase 5 decomposing MS-002); any validator nonzero at a phase boundary.

- [ ] **Step 2: Commit scenario** — `test-workflow: workflow-e2e full-loop scenario (spec 09)`.

- [ ] **Step 3: GREEN runs (2 full pipelines = 12 phase dispatches)** — model sonnet, phases sequential per run, one TARGET per run, fresh per run; each phase's dispatch = hard isolation + that skill's conditioning (installed at <worktree>/<skill>, read SKILL.md, follow; <this-skill-dir> = that path) + the phase's human message + scripted replies; phase evaluation at each boundary (the phase's validators) before proceeding — a phase failure fails the run (no mid-run repairs; diagnose, fix nothing in the target, rerun the full pipeline from zero after any harness correction; a SKILL defect discovered here is a finding for the controller, not a live edit).
- [ ] **Step 4: Results log + commit** — `test-workflow/results/workflow-e2e.md` with the no-RED note (`Integration conformance lane: no skill is created or edited by this scenario; no RED baseline is owed under the iron law.`), per-run entries pinning the scenario commit, per-phase observable tables. Commit `test-workflow: workflow-e2e GREEN 2x — full six-skill pipeline`.

---

### Task 4: Umbrella closing, TESTING.md, final gate

**Files:**
- Modify: `docs/specs/design-spec-of-workflow.md`, `test-workflow/TESTING.md`

- [ ] **Step 1: Umbrella closing** — Status line becomes `> Status: approved umbrella design, 2026-07-24. All nine focused specs designed, implemented, and tier-2 verified as of 2026-07-26; codex/tier-3 conformance deferred (test-workflow/TESTING.md).`; in the Focused Design Sequence list, each of the nine items gains a trailing ` — done (spec NN)` marker with its spec file number.
- [ ] **Step 2: TESTING.md** — extend the execute-milestone entry with `07 RED+2×GREEN (spec 09) at <edit commit>, 06 re-certified`; append `workflow-e2e/01 (tier 2, Claude Code only; GREEN 2× full pipeline, no RED owed — integration lane; 2026-07-26)`.
- [ ] **Step 3: Final gate** — all 11 suites; walk spec 09 Acceptance 1–6 with evidence (item 1: wc + diff scope; item 3: grep both SKILLs for `$STUBS` — zero hits). Commit `docs: umbrella closing status + spec-09 TESTING.md evidence`.

## Self-Review

- Spec coverage: Decisions 1→T2, 2→T1, 3→T1 Step 5, 4→T3, 5→T4; Acceptance 1–6 → T2/T1/T1/T3/T4/gate.
- Placeholders: none; all edit texts, prompts, scripted replies, and observables stated.
- Consistency: scenario 07's seed mirrors review-milestone 04's produced state; the stop line and transition names match the certified execute-milestone vocabulary; e2e phase list matches the six-skill pipeline; word bounds stated where they bind.
