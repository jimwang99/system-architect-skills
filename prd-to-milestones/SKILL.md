---
name: prd-to-milestones
description: Use when planning milestones from one or more PRDs for the first time, reconciling an existing ROADMAP after a PRD change (new REQ, scope change, or REQ retirement), or checking milestone coverage drift
---

# prd-to-milestones

## Overview

Each milestone is one demoable capability increment, sized for half-a-day to a few days of autonomous execution. Never size by feature count (that belongs to milestone-to-features). Deferral is a later milestone in document order, never an icebox.

Scripts in `<this-skill-dir>/scripts/`: `validate_roadmap.py`, `check_coverage.py`, `session_tx.py` (shared-transaction symlink). PRD validation: `<this-skill-dir>/../write-prd/scripts/validate_prd.py`.

## Session sequence

1. **Check preconditions — in order; stop at the first failure.**
   - `git rev-parse --show-toplevel` — if it fails: stop; this skill never runs `git init`; tell the human to create the repository.
   - `python3 <this-skill-dir>/../write-prd/scripts/validate_prd.py` over every `docs/prd/prd-NNN-<slug>.md` — if none exist or none pass: stop; point the human to write-prd.
   - If `ROADMAP.md` exists: `python3 <this-skill-dir>/scripts/validate_roadmap.py ROADMAP.md` — if exit non-zero: abort with the full report; repairing a broken ROADMAP is its own task.

2. **Enumerate drift.** `python3 <this-skill-dir>/scripts/check_coverage.py ROADMAP.md` (skip if no ROADMAP). Collect uncovered live REQs and stale citations.

3. **Propose before writing — present the complete cut, then converge.**
   - For each proposed milestone: title, one-sentence Goal, the `Covers:` list, one line of sizing rationale.
   - Human adjusts conversationally. Write nothing to disk until agreed.

4. **Open the transaction and write.**
   - `python3 <this-skill-dir>/scripts/session_tx.py begin`
   - `python3 <this-skill-dir>/scripts/session_tx.py track ROADMAP.md` (plus any backlog entries or ADR drafts — ADR drafts: via write-adr, `status: proposed`, never numbered or accepted here)
   - Write `ROADMAP.md` using the template below; fill placeholders, keep the `## Current Workflow Status` block verbatim.

5. **Gate, preview, wait, approve.** All gate steps: exit non-zero → fix and retry; never present a failing artifact.
   - `python3 <this-skill-dir>/scripts/validate_roadmap.py ROADMAP.md`
   - `python3 <this-skill-dir>/scripts/check_coverage.py ROADMAP.md`
   - `python3 <this-skill-dir>/../write-prd/scripts/validate_backlog.py` over every manifest backlog entry
   - `python3 <this-skill-dir>/../write-adr/scripts/validate_adr.py` over every manifest ADR draft
   - `python3 <this-skill-dir>/scripts/session_tx.py preview`; pause for human review.
   - Approved → `session_tx.py approve -m "<msg>"`. Withheld → leave uncommitted, never abandon. Explicit abandon → `session_tx.py abandon`.

## ROADMAP template

Every ROADMAP starts with this block verbatim (fill placeholders; never omit any key):

```markdown
## Current Workflow Status

- Current milestone: MS-001 — <title>
- Milestone state: planning-pending
- Active feature: none
- Next action: milestone-to-features MS-001

## MS-001 — <title>

- State: planning-pending
- Goal: <one demoable capability increment>
- Covers: PRD-001 REQ-001
```

Milestone heading: `## MS-NNN — <title>` (three-digit ID, em dash `—`, space both sides). Feature heading: `### FEAT-NNN — <title>`. Any other form (`M-01`, `MS-1`, `## MS-01`) is rejected by the validator.

The `## Current Workflow Status` section must be the first `##` section with exactly these four keys: `Current milestone`, `Milestone state`, `Active feature`, `Next action`. `Next action` must not be empty or a placeholder.

## Rules

| Rule | Detail |
|---|---|
| MS numbers | Allocated at max(live ∪ retired) + 1; never renumbered, never reused; `000` is illegal |
| Document order | Section order in the file is the planned execution order |
| Total coverage | Every live REQ must appear in exactly one milestone's `Covers:` — no gaps, no double-citations |
| Deferral | A REQ that cannot fit early goes into a later milestone in document order, not an icebox |
| Fold-in resets state | Adding scope to a `planned` milestone resets it to `planning-pending` and deletes all its `### FEAT-` subsections in the same transaction |
| Started milestones are scope-immutable | Milestones in `in-progress`, `paused`, `review-ready`, `remediating`, or `accepted` state are **never edited by this skill** — not their `State:`, `Goal:`, `Covers:`, nor any FEAT content |
| Retired REQ in not-yet-started milestone | Citations of retired REQs are removed from `planning-pending`/`planned` milestones in the same transaction as the REQ retirement |
| Stale citation in a started milestone | Report it to the human; leave the milestone section byte-identical; do not remove the citation or "fix" check_coverage by touching the started milestone |
| This skill writes only `planning-pending` | In two situations only: milestone creation and the fold-in reset; all other state transitions belong to other skills |
| Scaffold summary | Points at MS-001 with `Next action: milestone-to-features MS-001` |
| Summary/detail agreement | `## Current Workflow Status` and every milestone section always change in the same commit |

## Rationalization table

Every row quotes the exact rationalization a skill-less agent produced when it violated a rule. Stop and re-read the rule if you find yourself reasoning in these patterns.

| Rationalization (verbatim RED) | Reality |
|---|---|
| "REQ-004 (confirmation email) is triggered by the same successful charge event that FEAT-001 already owns … Slotting it as FEAT-002 inside MS-001 keeps payment-completion concerns together." | MS-001 was `in-progress`. Scope-immutability is absolute — coupling arguments do not override it. New REQ goes into a not-yet-started milestone. |
| "MS-001's `Covers` line cited … `PRD-001 REQ-002`; removing the retired reference is the only change needed." | MS-001 was `in-progress`. Removing a stale citation violates scope-immutability even if `check_coverage.py` passes afterward. Report the conflict; touch nothing. |
| (02) No reasoning stated for retaining `State: planned` and FEAT subsections after adding REQ-004 to MS-002's `Covers:`. The scope-change → state-reset rule was never applied. | Adding scope to a `planned` milestone resets it to `planning-pending` and deletes all its FEAT subsections in the same transaction. No exceptions. |
| "M-01 (Search) runs first … All 5 requirements across both PRDs are covered with no gaps." | Headings were `### M-01`/`### M-02` — not the required `## MS-001`/`## MS-002`. `## Current Workflow Status` was omitted. `validate_roadmap.py` exits 1. Follow the template exactly. |

## Red flags — STOP

- About to run `git init` because "the workflow needs a repo" — refuse; the human inits, you do not.
- About to write or read any file outside the target git work tree.
- About to edit any field inside a started milestone's section (`in-progress`, `paused`, `review-ready`, `remediating`, `accepted`) — including removing a stale REQ citation, adding a FEAT, or updating `Goal:`.
- About to keep `State: planned` on a milestone after adding scope to it, or about to leave its FEAT subsections intact.
- About to use a heading form other than `## MS-NNN — <title>` or `### FEAT-NNN — <title>` (three-digit IDs, em dash, correct heading level).
- About to omit or rename any of the four required `## Current Workflow Status` keys.
- About to commit without a `preview` and explicit human approval.
- About to `git add -A` or stage any path outside the session manifest.
