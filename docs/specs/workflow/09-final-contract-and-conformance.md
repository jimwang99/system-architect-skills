# Spec 09: Final WORKFLOW.md Contract and End-to-End Conformance

> Status: approved design, 2026-07-26 (autonomous overnight run — decisions taken at the recommended option per the user's standing authorization; rationale recorded inline)
>
> Parent: [design-spec-of-workflow.md](../design-spec-of-workflow.md), Project Bootstrap (WORKFLOW.md mandate) and Verification Contract; closes the nine-item Focused Design Sequence.
>
> Scope: the final WORKFLOW.md invariant contract, the end-to-end conformance lane across all six workflow skills, the spec-08 ticket (execute-milestone's remediating-resume gap, RED-gated), and the umbrella's closing status.

## Problem

Three gaps remain after specs 01–08. The ambient contract is still the spec-03 stub (280 words, missing the reversibility escalation rule and the milestone ritual). The remediation loop closes on paper but not in execute-milestone's literal text: its preconditions, inference clause, and completion step exclude `remediating`, so a remediate verdict dead-ends (spec 08's ticketed finding). And nothing has ever run the six skills as one pipeline — every seam is pairwise-verified, none end-to-end.

## Decisions (Normative)

1. **WORKFLOW.md final contract.** The stub is revised in place, ≤ 400 words, invariants only: drop the stub disclaimer line; keep the artifact table, dispatch table, status location, human boundaries, and hard prohibitions as they stand; add (a) the reversibility escalation rule, two lines — an architecturally significant "how" that is undoable within roughly one feature of work is decided locally with a draft ADR; anything irreversible, or contradicting an accepted ADR or PRD, becomes a backlog entry and blocks; (b) one milestone-ritual line — every milestone ends with the review-milestone sweep (learnings, ADR audit, backlog triage, integration review, three-C, demo) and exactly one verdict; (c) one transaction line — planning documents (PRD, backlog, ROADMAP planning states, ADR drafts) change only through a previewed, human-approved session transaction. How-to stays in skills. Rationale: Q10's compact-invariant mandate; the stub already carries the rest.
2. **Remediating-resume fix, RED-first (spec-08 ticket).** New scenario `execute-milestone/07-remediation-resume` (application): seed = the state review-milestone's remediate verdict produces (milestone `remediating`, one fix feature `todo` with full keys, milestone branch with the review record's remediate pass, prior features `done`); prompt `execute-milestone MS-001`. RED expectation against the CURRENT skill: the literal preconditions stop it (the captured gap). Then the minimal edits to `execute-milestone/SKILL.md`: eligibility and inference include `remediating`; the completion step reads "last feature done → `in-progress → review-ready` or `remediating → review-ready`"; preconditions' state gate names `remediating` as recovery-eligible alongside mid-flight states. GREEN 2× on 07; scenario 06 (self-ignition) re-certified 2× because the guard paragraph's eligibility list changes; other scenarios' certified mechanics are untouched by the delta (adjudicate drift per precedent if the reviewer disagrees).
3. **STUBS-PATH scaffolding removal, mechanical.** The gate-invocation lines in `execute-milestone/SKILL.md` and `review-milestone/SKILL.md` drop the `PATH="$STUBS:$PATH"` test-harness prefix (production hazard: an unset `$STUBS` yields an empty PATH entry, which POSIX resolves as cwd). Its own commit, labeled mechanical — certified runs supplied PATH externally via dispatch, so no certified behavior changes; the spec-07 final review already classified this advisory.
4. **End-to-end conformance lane.** One scenario `test-workflow/scenarios/workflow-e2e/01-full-loop.md` (frontmatter `skill: workflow-e2e`, `type: application`, `tier: 2`) driven as SIX PHASE-CHAINED dispatches over one TARGET repo — one subagent per skill session, each conditioned on its own skill, exactly as a human drives separate sessions in production. Phases: (1) write-prd — bootstrap an empty git repo + first interview → `prd-001` with two REQs; (2) prd-to-milestones — two milestones (MS-001 covers REQ-001, MS-002 covers REQ-002); (3) milestone-to-features MS-001 — one feature; (4) execute-milestone MS-001 — implement the tiny feature (greet-class), tests pass, `success` review stub, evidence, review-ready; (5) review-milestone MS-001 — fast-disposition sweep, accept, merge, handoff deferred; (6) a no-op probe phase — a bare "keep things moving" message to a skill-less agent asserting nothing fires (the ignition boundary holds at the pipeline level). Expected (final state, all machine checks): main holds the merged milestone; every validator green over its artifact (`validate_prd`, `validate_roadmap`, `check_coverage`, `validate_learning` if an ALI exists, `validate_review` on the record's accept pass); ROADMAP shows MS-001 `accepted`, MS-002 `planning-pending`, `Next action: milestone-to-features MS-002`; the bootstrap reference line in AGENTS.md; the review JSON and plan file present; per-transition ROADMAP walk validator-clean. No RED is owed: the lane creates and edits no skill — it is integration conformance (the log records this explicitly). GREEN = 2 consecutive clean full-pipeline runs. Rationale: phase-chaining is deterministic and production-faithful; one mega-dispatch would blur which skill failed.
5. **Umbrella closing status.** `design-spec-of-workflow.md`'s Status line gains: `All nine focused specs designed, implemented, and tier-2 verified as of 2026-07-26; codex/tier-3 conformance deferred (TESTING.md).` The Focused Design Sequence section gets a one-line per-item done-marker pass. TESTING.md gains the workflow-e2e row and extends the execute-milestone row with scenario 07.

## Verification

Deterministic lane: no validator changes; all 11 suites are a regression gate.

Scenario work: `execute-milestone/07` RED (1 run, current skill) → edits → GREEN 2×; `execute-milestone/06` re-cert 2×; `workflow-e2e/01` GREEN 2× (phase-chained; no RED owed, noted in log). Results logs: append to `test-workflow/results/execute-milestone.md`; new `test-workflow/results/workflow-e2e.md`.

## Acceptance

1. WORKFLOW.md ≤ 400 words, stub disclaimer gone, the three additions present, everything else preserved in substance.
2. `execute-milestone/SKILL.md` includes `remediating` in eligibility, inference, and completion; scenario 07 RED + GREEN 2× and scenario 06 re-cert 2× logged with honest pins.
3. The STUBS-PATH prefix is absent from both SKILL gate lines (mechanical commit).
4. `workflow-e2e/01` GREEN 2× with the no-RED note; the final-state checklist passes mechanically in both runs.
5. Umbrella and TESTING.md carry the closing status; all 11 suites green.
6. No validator, fixture, or grammar file modified.

## Out of Scope

- Codex/tier-3 lanes (recorded deferred — the standing pattern).
- Production `workflow-review` wrappers.
- Any new skill or grammar.
- Team packaging (umbrella out-of-scope stands).
