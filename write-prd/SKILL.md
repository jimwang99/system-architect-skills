---
name: write-prd
description: Use when capturing or refining product requirements, starting a doc-driven project, resolving product questions from the decision backlog, or when a PRD needs new or changed requirements
---

# Write PRD

## Overview

Grill the human until requirements are testable; edit living PRDs under a review gate; bootstrap the project's ambient contract. PRDs are the "what" (`docs/prd/`), ADRs the "why", the decision backlog the undecided.

The four tools live in this skill's own `scripts/` directory (`<this-skill-dir>/scripts/`): `bootstrap_project.py`, `session_tx.py`, `validate_prd.py`, `validate_backlog.py`.

## Iron rule

Nothing is committed unreviewed. Every session mutation flows through the session transaction: track before writing, preview before approval, one commit for exactly the manifest. Approval withheld leaves the patch uncommitted and reviewable — never abandoned. Explicit abandonment rolls everything back. You do not create the git repository; that is the human's move.

## Session sequence

1. **Bootstrap.** Run `python3 <this-skill-dir>/scripts/bootstrap_project.py plan` (never pass `--workflow-path`; the default path is the contract). Exit 0 → already installed, continue. Exit 3 → show the printed plan, begin the transaction (`session_tx.py begin`), `track AGENTS.md CLAUDE.md`, run `bootstrap_project.py apply`, `session_tx.py preview`, wait for the human, then `session_tx.py approve -m "chore: bootstrap doc-driven workflow"` — its own commit, separate from any PRD commit. Exit 1 → report the exact message and stop. If it says "not a git repository", tell the human to run `git init` themselves and stop; you never init a repo.
2. **Inventory** `docs/prd/` by the filename grammar `prd-NNN-<slug>.md`. A malformed file there aborts the session with a report. Mode: no PRDs → first interview → `prd-001`; the human names a new product area → new `prd-NNN` at max+1; exactly one PRD and no new area named → that PRD is the revision target; several PRDs and none uniquely named → **the human names the target; ask, do not guess**. Validate a revision target with `validate_prd.py` before editing; a failing PRD aborts.
3. **Triage** open `Type: product` backlog entries in every mode: list them, the human picks which to address; none is a legal answer.
4. **Interview**, one question at a time. Cover Purpose, Users, Non-goals, Constraints, Success criteria before presenting. Challenge vague answers until every acceptance is testable — a bound needs a number, a unit, and a measurement condition. Propose non-goals. Hunt contradictions with existing requirements and accepted ADRs. An architectural "how" → draft it with `write-adr` (`adr-draft-<slug>`, `status: proposed`), track it in this manifest. An unanswerable product question → a backlog entry by the grammar, tracked.
5. **Per requirement,** show the delta (full R-block, or before/after), confirm conversationally, then edit in place. New IDs = max(live ∪ Retired) + 1 — retiring the highest ID never frees it, tombstoned IDs never come back live. Removing a block adds its ID to `Retired` in the same commit. Never renumber or reuse an existing ID.
6. **End gate.** Run `validate_prd.py`, `validate_backlog.py`, and `validate_adr.py` over every manifest artifact each governs — a failing artifact is never presented. Then `session_tx.py preview`, then wait for the human. Approve → `session_tx.py approve -m <msg>`. Change requests → iterate, re-gate. Explicit abandon → `session_tx.py abandon`. Silence or "not yet" → leave it uncommitted; commit nothing.

A resolved `product` backlog entry is **deleted** (`git rm`, so it enters the same manifest) in the same commit as the requirement delta that answers it — never rewritten into a "resolved" tombstone. `write-adr` owns ADR acceptance; you draft only, never number or accept an ADR.

## Rationalization table

Every row is a verbatim excuse captured from a skill-less baseline run.

| Excuse (verbatim from RED) | Reality |
|---|---|
| "As the agent executing the task, I need to get the PRD written… So I need to `git init` first (the human, me, doing it), then run bootstrap." | You are not the human. `git init` on the human's behalf is the forbidden observable. Refuse and tell the human to init the repo. |
| "The instruction is to initialize the project workflow (which includes git init) and write the PRD." | Bootstrap installs the ambient contract; it never creates the repository. No git work tree → refuse, nothing written. |
| "inserted a new **R-01 — Login response time** requirement … before the existing password-login requirement, which is now **R-02**." | Requirement IDs are never reused or renumbered. New ID = max(live ∪ Retired) + 1, appended. The existing R-01 keeps its number. |
| "update the decision backlog entry `…` to reflect the resolution"; "added `- Resolved:` metadata line pointing to prd-002" | A resolved `product` entry is `git rm`'d in the same commit as the delta — git history is the trace. A rewritten "resolved" file is not deletion. |
| "The task instructs me to decide (accept) the notification delivery ADR, meaning I need to create it as an accepted ADR (not a draft), since the user is … authorizing that decision inline." | You draft only: `adr-draft-<slug>`, `status: proposed`, no number, no `decided:`. Numbering and acceptance are `write-adr`'s human-gated lifecycle, not yours. |
| "This is the scripted-reply pattern from the ADR skill — the user's authorization and approval are already given in this instruction." | "Approve and commit everything" approves the session commit — it never authorizes self-numbering or self-accepting an ADR. The draft stays `proposed`. |
| (07) narrates "added R-03 … to prd-002" with no question posed when two PRDs exist | Two PRDs and neither named → ask which. Any edit before the human names the target is the forbidden observable, even when the wording "strongly suggests" one. |

## Red flags — STOP

- About to run `git init` (or scaffold a `.git`) because "the workflow needs a repo" — refuse; the human inits, you do not.
- About to write `AGENTS.md`, `CLAUDE.md`, or a PRD in a directory that is not a git work tree.
- About to renumber, reuse, or insert-shift an existing requirement ID — new IDs only ever append at max(live ∪ Retired) + 1.
- About to reuse or resurrect a tombstoned ID as a live requirement.
- About to edit a PRD before the human has named the target when more than one PRD exists.
- About to leave a resolved backlog entry on disk, or rewrite it as a "resolved" tombstone, instead of `git rm`-ing it in the delta's commit.
- About to number an ADR (`adr-NNN-*`) or set `status: accepted`/`decided:` on a draft — you draft `proposed`; acceptance is `write-adr` under a separate human authorization.
- About to fold a delivery-mechanism / architecture "how" into the PRD's Constraints or acceptance instead of an ADR draft.
- About to commit without a preview and an explicit human approval — or to abandon a patch the human only asked you to hold.
- About to `git add -A`/`git add .`, or stage any path outside the session manifest.
