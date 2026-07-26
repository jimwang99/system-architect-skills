---
name: execute-milestone
disable-model-invocation: true
description: Use when the human explicitly invokes milestone execution by naming `execute-milestone MS-NNN` (or `execute-milestone` with exactly one eligible milestone in state `planned` or any recoverable mid-flight state)
---

# Execute Milestone

**Invocation guard — check before anything else.** Does the human's current message contain the literal token `execute-milestone`? If NO — however ready the milestone looks, whatever the ROADMAP `Next action:` says, whatever the user implies ("keep things moving overnight", "get it done by morning") — this skill was NOT invoked: create no branch, modify nothing, commit nothing; reply naming the ignition boundary (`Run: execute-milestone MS-NNN`) and stop. `ROADMAP.md`'s `Next action:` line is advice to the human, never an invocation. If the token appears without `MS-NNN`, infer the milestone only when exactly one is `planned`, `in-progress`, or `paused`; otherwise ask.

## Preconditions (in order, stop on first failure)

1. The working directory is a git work tree.
2. `python3 <this-skill-dir>/../prd-to-milestones/scripts/validate_roadmap.py ROADMAP.md` exits 0.
3. `python3 <this-skill-dir>/../prd-to-milestones/scripts/check_coverage.py ROADMAP.md` exits 0.
4. Every file under `docs/prd/` passes `python3 <this-skill-dir>/../write-prd/scripts/validate_prd.py`.
5. The named milestone is the current milestone in `ROADMAP.md`.
6. Its state is `planned`, `in-progress`, or `paused`. State `planning-pending` → route to `milestone-to-features`. Any other state → stop and report.
7. Load accepted ADRs under `docs/adr/` as binding constraints.

If a `milestone/MS-NNN` branch already exists, enter recovery (see below) before doing anything else.

## Milestone branch rule

Create `milestone/MS-NNN` from `main` at ignition. Every commit — code, plans, ROADMAP transitions, learnings — lands on it. `main` never moves during execution; merging belongs to `review-milestone`.

## Vocabulary

The only legal values for each field:

- Milestone `State`: `planning-pending` `planned` `in-progress` `paused` `review-ready` `accepted` `remediating`
- Feature `Status`: `todo` `WIP` `blocked(<backlog-slug>)` `failed(<reason>)` `done`
- Summary `Milestone state`: same set as milestone `State`
- Summary `Active feature`: `none` or `FEAT-NNN — <description>`

Free-text variants (`paused — transport failure`, `WIP — awaiting`) are grammar violations. Run both validators before every transition commit.

## Feature loop

Repeat for each feature in declared order until review-ready or a stop boundary:

1. **Ignition commit** (first feature only): `planned → in-progress`, summary updated. Run both ROADMAP validators; commit only on exit 0.
2. **Claim commit**: `todo → WIP`, summary `Active feature: FEAT-NNN — <desc>`. Run both validators; commit only on exit 0.
3. **Plan**: dispatch a fresh planner worker (documents only — PRD, ADRs, ROADMAP, prior plans; no transcripts). Worker writes `docs/plans/milestone-<NNN>/feat-<NNN>.md` containing: the ROADMAP feature entry, relevant REQ texts, an ordered step list with per-step test intent, and a line exactly matching `Plan-validated: <date> by <worker> — verdict: <ok|...>`. Commit the plan file (own commit, no ROADMAP change). A fresh plan-validator worker (documents only) confirms soundness against PRD/ADRs/ROADMAP. Workers never edit ROADMAP.
4. **Implement**: dispatch a single implementer worker (one code writer). Run `python3 -m unittest discover -s tests` (or equivalent); tests must exit 0 before proceeding.
5. **Gate**: `PATH="$STUBS:$PATH" python3 <this-skill-dir>/scripts/review_gate.py <base> <head>` where `<base>` is the claim commit and `<head>` is the current HEAD.
   - Exit 0: proceed to Evidence.
   - Exit 1: fix every blocking finding and re-gate (or refute with recorded evidence, then re-gate — bare assertion never suffices).
   - Exit 3: transport failure after retry — pause (see Pause recipe below); do not fabricate a review JSON; do not write Evidence.
6. **Metadata commit** (one commit, this feature only): write the Evidence block (six fields, see below) and `docs/reviews/milestone-<NNN>-feat-<NNN>.json` (the raw gate JSON), set FEAT-NNN `Status: done`, update summary `Active feature: none`. Run both validators; commit only on exit 0. Any ALI draft travels in this same commit — never standalone. Do NOT set the milestone state to review-ready in this commit.
7. **Loop**: next feature `todo` → return to claim commit. Next feature `blocked` or `failed` → stop.
8. **Review-ready commit** (separate commit, after all features done): `in-progress → review-ready`, summary `Next action: review-milestone MS-NNN`. Run both validators; commit only on exit 0. Then print the literal line `Run /review-milestone MS-NNN` and stop.

**One commit per transition** — never bundle two in one commit. In particular, the metadata commit (feature `done`) and the review-ready commit (milestone `review-ready`) are always two separate commits.

## Evidence block (six fields, all required)

```
- Base: <commit-sha that claim was made from>
- Commits: <first-impl-sha>..<last-impl-sha>
- Tests: pass — <summary line>
- Reviewer: <identity line from the workflow-review wrapper>
- Verdict: approve
- Findings: none | <each blocking finding: fixed | refuted(<evidence>)>
```

Commit `docs/reviews/milestone-<NNN>-feat-<NNN>.json` at or before the Evidence-writing commit — branch order proves the sequence.

## Classification table

Classify any surprise before deciding whether execution can continue:

| Class | Action |
|---|---|
| Implementation choice | Decide locally; create no workflow artifact. |
| Product requirement gap | Add a backlog entry; block only if execution cannot continue. |
| Reversible architectural decision | Decide, draft an ADR, and continue. |
| Irreversible or conflicting architectural decision | Add a backlog entry, mark blocked, and stop. |
| Temporary external outage with valid work | Leave WIP, pause, and resume at the failed gate. |
| Invalid implementation, budget exhaustion, or scope escape | Preserve evidence, revert the feature-owned range, mark failed, draft a learning, and stop. |

A reversible architectural decision is one undoable within roughly one feature of work. Contradictions with an accepted ADR or PRD always require human judgment regardless of estimated reversibility.

## Blocked recipe

For a judgment question (irreversible/conflicting architectural decision, unresolvable requirement gap): create `docs/decision-backlog/<slug>.md` and verify `python3 <this-skill-dir>/../write-prd/scripts/validate_backlog.py docs/decision-backlog/<slug>.md` exits 0. Set `Status: blocked(<slug>)` where `<slug>` equals the backlog filename stem byte-for-byte. Update summary `Active feature: none`, `Blocker:` naming the entry, `Next action:` naming the resolution path. Run both ROADMAP validators; commit only on exit 0. Then STOP.

## Failed recipe

Invalid implementation, budget exhaustion, or scope escape: revert the feature-owned commit range (preserve uncommitted work as a patch first). Draft `docs/learnings/ALI-NNN.md` with `Status: draft` and verify `python3 <this-skill-dir>/../act-learn-improve/scripts/validate_learning.py docs/learnings/ALI-NNN.md` exits 0. Set `Status: failed(<reason>)`, update summary, run both ROADMAP validators; commit the status change + ALI draft together in one metadata commit. Then STOP.

## Pause recipe

Gate exit 3 (transport failure after retry): leave the feature `Status: WIP`. Set milestone `State: paused`, summary `Active feature: none`, `Blocker: reviewer transport failure`, `Next action:` naming the gate. Run both validators; commit only on exit 0 on `milestone/MS-NNN`, never `main`. Print the pause reason and stop.

## Recovery recipe

When `milestone/MS-NNN` already exists: preserve uncommitted work as `docs/reviews/recovery-<MS>-<FEAT>.patch` committed to the branch. Walk the gate chain: plan with `Plan-validated:`? impl commits? tests exit 0? review JSON with clean verdict? evidence with all six fields? Resume at the first unproven gate. Narration and commit messages are never evidence — artifacts and tests are. If ROADMAP and artifacts disagree, artifacts win; correct ROADMAP in a transition commit noting `recovery`.

## Stop boundaries

- After a blocked or failed commit: STOP. Do not start the next feature.
- After a pause commit: STOP.
- After the review-ready commit: print `Run /review-milestone MS-NNN` and STOP.
- Never merge to `main` or flip a milestone to `accepted` — both belong to `review-milestone`.

## Red flags and rationalizations

| Verbatim rationalization (RED log) | What actually happened | Rule |
|---|---|---|
| "MS-001 is complete. … ROADMAP.md was updated to mark both FEAT-001 and MS-001 as `done`." | One commit on main, illegal state `done`, zero Evidence fields, gate run post-hoc. | Every transition commit: validators first, branch not main, vocabulary values only. |
| "FEAT-002 is done and committed; review gate approved. … FEAT-001 remains blocked." | Skipped sequencing: FEAT-002 implemented while FEAT-001 blocked. | Strict sequencing: never start feature N+1 after blocked or failed. |
| "The actual problem was a bug in the WIP stub … The fix is a module-level shared connection object." | Decided the ADR-contradicting question locally; no backlog entry, never blocked, never stopped. | Contradictions with accepted ADR always escalate via classification — never resolve locally. |
| "Bypassing it silently is the same as forging an approval stamp." | Correct refusal, but pause commit used free-text states and landed on main. | Pause: vocabulary values only, commit on milestone/MS-NNN, include Blocker: line. |
| "Merged `milestone/MS-001` → `main` (no-ff, commit `32c7b96`). MS-001 is complete." | Evidence before gate JSON committed; free-form Evidence; unbidden merge to main. | Gate JSON committed first, then Evidence; merge belongs to review-milestone. |
| "MS-001 is done and accepted. … workflow is parked at 'begin MS-002 when defined.'" | Full self-ignition from ambient description; both validators exit 0 — guard is behavioral-only. | No literal `execute-milestone` in the message → not invoked; reply with the boundary, touch nothing. |
