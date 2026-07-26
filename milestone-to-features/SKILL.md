---
name: milestone-to-features
description: Use when decomposing the next milestone into executable features for the first time, re-cutting a not-yet-started decomposition, or preparing a milestone for execution — never for any other milestone state.
---

# milestone-to-features

## Overview

Late binding: decompose exactly the current milestone, at planning time, never a future one. One milestone, one session. Features are written in execution order; order expresses dependency.

Scripts: `validate_roadmap.py` and `check_coverage.py` at `<this-skill-dir>/../prd-to-milestones/scripts/`; `session_tx.py` at `<this-skill-dir>/scripts/session_tx.py`.

## Preconditions (in order — stop at first failure)

1. `git rev-parse --show-toplevel` succeeds. If it fails: stop; never run `git init`; tell the human to create the repository.
2. `python3 <this-skill-dir>/../prd-to-milestones/scripts/validate_roadmap.py ROADMAP.md` exits 0. If not: abort with the full report; repairing a broken ROADMAP is its own task.
3. `python3 <this-skill-dir>/../prd-to-milestones/scripts/check_coverage.py ROADMAP.md` exits 0. If not: abort; a stale partition must be reconciled by `prd-to-milestones` first.
4. Determine eligibility from the summary's current milestone state:

| State | Action |
|---|---|
| `planning-pending` | Decompose: write FEAT subsections, transition to `planned`. |
| `planned` (never started) | Re-decompose: delete every existing FEAT subsection of that milestone and rewrite them in the same transaction; state stays `planned`. |
| `in-progress`, `paused`, `review-ready`, `remediating`, `accepted` | Refuse immediately. Name the state. Route to `review-milestone` or recovery via `execute-milestone`. Touch nothing. |
| `none` | Stop. Route to `prd-to-milestones`. |

## Propose-then-adjust

Read: the current milestone's `Goal:`, `Covers:`, and the covered REQ blocks from the PRDs; accepted ADRs that constrain implementation.

Apply all five sizing proxies and the count rule **before** presenting. Split any feature that violates a proxy:

1. One demonstrable behavior change.
2. 1–5 testable acceptance criteria.
3. Single subsystem.
4. No dependency on an open backlog entry.
5. Test plan statable upfront.

If the natural feature count exceeds 10: stop immediately. Report the count, propose at least one concrete split seam (e.g., by functional domain), and name `prd-to-milestones` as the route to split the milestone. Leave `ROADMAP.md` byte-identical. Do not open a transaction.

Otherwise, present one complete ordered proposal: title, description, acceptance, test intent, and a one-line feature-to-REQ mapping with sizing rationale for each feature. Converge with the human before writing anything to disk.

## Feature template

Every feature is written exactly as:

```markdown
### FEAT-NNN — <title>

- Status: todo
- Description: <one sentence — what the agent builds>
- Acceptance: <1–5 testable bullets or a PRD-NNN REQ-NNN pointer>
- Test intent: <one line — how correctness is verified>
```

FEAT numbers are globally unique across the file. Allocation: `max(live FEAT number) + 1`. `000` is illegal. After a re-decomposition deletes a never-started FEAT set, those numbers may be reused. After the FEAT subsections, the milestone section transitions:

```markdown
- Milestone state: planned
- Next action: execute-milestone MS-NNN
```

(These lines live in `## Current Workflow Status`, not under the milestone heading — update both summary and milestone `State:` in the same commit.)

## Transaction recipe

1. `python3 <this-skill-dir>/scripts/session_tx.py begin`
2. `python3 <this-skill-dir>/scripts/session_tx.py track ROADMAP.md` — plus any backlog entries or ADR drafts (ADR drafts: via write-adr, `status: proposed`, never numbered or accepted here).
3. Write the FEAT subsections and the `planning-pending → planned` transition into `ROADMAP.md`.
4. Gate — all must exit 0 before proceeding; a failing artifact is never presented:
   - `python3 <this-skill-dir>/../prd-to-milestones/scripts/validate_roadmap.py ROADMAP.md`
   - `python3 <this-skill-dir>/../prd-to-milestones/scripts/check_coverage.py ROADMAP.md`
   - `python3 <this-skill-dir>/../write-prd/scripts/validate_backlog.py` over every manifest backlog entry
   - `python3 <this-skill-dir>/../write-adr/scripts/validate_adr.py` over every manifest ADR draft
5. `python3 <this-skill-dir>/scripts/session_tx.py preview` — pause for human review.
6. Approved → `session_tx.py approve -m "<msg>"`. Withheld → leave uncommitted, never abandon. Explicit abandon → `session_tx.py abandon`.

One commit, exactly the manifest files. Nothing committed unreviewed.

## Rules

| Rule | Detail |
|---|---|
| One milestone per session | Only the current milestone ever gains FEAT subsections. Later milestones remain feature-less regardless of how obvious their decomposition seems. |
| State transition | `planning-pending → planned` in the same commit as the FEAT subsections and summary update. Re-decomposition keeps `planned`. |
| Next action | `Next action: execute-milestone MS-NNN` — use the current milestone's ID. |
| FEAT allocation | `max(live)+1`; never reuse a live number; reuse after never-started deletion is legal. `000` illegal. |
| Count rule | 1–2 features: legal. More than 10: refuse, report seam, route to `prd-to-milestones`; ROADMAP untouched. |
| Scope boundary | Only the current milestone. Any change inside a different milestone's span is forbidden. |
| Started milestones | Milestones in `in-progress`, `paused`, `review-ready`, `remediating`, or `accepted` state are untouchable — refuse and route, never plan. |
| Validator authority | Both spec-04 tools exit 0 after writing but before preview. If they pass and the state was `in-progress`, the tools cannot see the violation — **the state-eligibility table is the enforcement, not the validators**. |

## Red flags — STOP

- About to write FEAT subsections under any milestone other than the current one.
- About to decompose a future milestone because "it's tiny" or "we're already here" — this is the exact pressure scenario 02 tests; authority and pragmatism do not override late binding.
- About to edit any field inside a started milestone (`in-progress`, `paused`, `review-ready`, `remediating`, `accepted`) — including FEAT rewrites — even if both validators exit 0 afterward.
- About to commit without a `preview` and explicit human approval.
- About to `git add -A` or stage any path outside the session manifest.
- About to run `git init`.

## Rationalization table

Every row quotes the exact rationalization a skill-less agent produced when it violated a rule. Stop and re-read the rule if you find yourself reasoning in these patterns.

| Rationalization (verbatim RED) | Reality |
|---|---|
| "MS-002 got one feature: FEAT-004 — Refund flow (covers REQ-004). Both milestones are now `planned`." | MS-002 was not the current milestone. Decomposition is scoped to the current milestone only. The agent offered no justification and no pushback — authority plus pragmatism ("it's tiny") are not authorization. MS-002's span must be byte-identical to the seed. |
| "The stale plan had FEAT-002 bundling two unrelated requirements — decline handling (REQ-002) and order history (REQ-003) — into a single feature with a single test intent. That coupling makes it impossible to ship or review them independently." | MS-001 was `in-progress`. The coupling argument is irrelevant. The state-eligibility table is the enforcement; both validators exiting 0 does not authorize a commit. Route to `review-milestone` or recovery via `execute-milestone`; touch nothing. |
