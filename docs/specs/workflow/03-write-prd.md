# Spec 03: write-prd and Project Bootstrap

> Status: approved design, 2026-07-25
>
> Parent: [design-spec-of-workflow.md](../design-spec-of-workflow.md), skill boundaries and Project Bootstrap sections.
>
> Scope: the PRD and decision-backlog artifact grammars with their validators, the write-prd session contract, project bootstrap mechanics, and the minimal `WORKFLOW.md` stub.

## Problem

The workflow needs one owner for product requirements: a skill that grills the human until requirements are testable, edits living PRDs under a review gate, and bootstraps a target project so every later skill finds the ambient contract in place. PRDs are the "what"; ADRs stay the "why" (spec 02); the decision backlog holds the "undecided". Spec 02 left the backlog entry format unowned while `write-adr` already consumes and deletes entries via `resolves:` — this spec closes that gap because `write-prd` is the primary creator of backlog entries.

## Ownership

Owned here: the PRD file grammar and `validate_prd.py`, the decision-backlog entry grammar and `validate_backlog.py`, the write-prd session contract (interview floor, delta review, end gate), project bootstrap mechanics, the minimal repo-root `WORKFLOW.md` stub, and the write-prd verification scenarios.

Owned elsewhere: ADR grammar and lifecycle (spec 02), `ROADMAP.md` creation and milestone decomposition (spec 04), the final `WORKFLOW.md` contract (spec 09), and how `execute-milestone` creates backlog entries mid-run (spec 07 — it follows the grammar pinned here).

## PRD File Grammar (Normative)

PRDs live at `docs/prd/prd-NNN-<slug>.md`, one per product area. Slugs are kebab-case (`[a-z0-9-]`, starting alphanumeric). `NNN` is three digits, assigned at creation as max-existing + 1 (`001` when none exist). Creation happens only inside a human-gated write-prd session, so the filename scan is a sound allocator — the same argument as ADR numbering. PRD numbers are never reused, and deleting or renaming a PRD is illegal; there is no retirement lifecycle yet. The number appears only in the filename; the H1 is the product-area title alone.

Six H2 sections are mandatory, in this order, each non-empty: `Purpose`, `Users`, `Non-goals`, `Constraints`, `Success criteria`, `Requirements`. The first five are the interview coverage floor made machine-checkable. Additional H2 sections are permitted after the required six — a living document a human also edits should not fight its owner. This tolerance is a deliberate divergence from the ADR grammar's closed frontmatter, for the same reason ROADMAP tolerates unknown keys: mutable artifacts favor tolerance, frozen artifacts favor strictness.

`Constraints` holds product-level constraints only (platform, compliance, budget, compatibility). Architectural decisions belong in ADRs; the skill text polices this boundary, the validator cannot. `Success criteria` holds product-level measurable outcomes, distinct from per-requirement acceptance.

The `Requirements` section contains only requirement blocks:

```markdown
### R-03 — Session expiry

- Statement: Sessions expire after a configurable idle timeout.
- Acceptance:
  - An idle session past the timeout rejects the next request with 401.
  - The timeout is configurable per deployment, default 30 minutes.
```

Heading grammar is `### R-NN — <title>` (`NN` = two or more digits, zero-padded). Each block carries `- Statement:` exactly once (one sentence; the skill owns sentence discipline, the validator checks presence and non-emptiness) followed by `- Acceptance:` exactly once with one or more nested, non-empty, testable bullets. Other `- Key:` lines are permitted and ignored. R-IDs are unique within their PRD and strictly ascending in document order; gaps are legal because retired IDs are never reused. New IDs are assigned as max-existing + 1.

The citation form for a requirement, used by later specs (ROADMAP `Acceptance:` pointers), is `prd-NNN R-NN`.

## validate_prd.py

Spec-01 validator conventions: stdlib Python 3.9, path argument, one `path:line: message` per violation on stderr, exit 0 pass / 1 violations / 2 usage or read error. Checks:

1. Filename matches `prd-NNN-<slug>.md`.
2. Exactly one H1, and it is the first content line.
3. The six required H2 sections appear exactly once each, in the required order, before any unknown H2 section.
4. Every required section is non-empty (content beyond its heading).
5. The `Requirements` section contains only requirement blocks whose headings match `### R-NN — <title>`.
6. R-IDs are unique and strictly ascending in document order.
7. `Statement` appears exactly once per requirement, before `Acceptance`, with a non-empty value.
8. `Acceptance` appears exactly once per requirement, with at least one nested non-empty bullet.
9. No `Statement` value or acceptance bullet is a placeholder (`TBD`, `TODO`).

Unknown H2 sections after the required six and unknown `- Key:` lines inside requirement blocks are permitted and ignored. Dual-use per spec 01: write-prd runs this validator as a self-check gate before presenting any PRD for approval.

## Decision-Backlog Entry Grammar (Normative)

Entries live at `docs/decision-backlog/<slug>.md`, kebab-case slugs, no numbers — backlog entries are transient (memory Q5: transient items get slugs; only accepted artifacts get numbers).

```markdown
# Should sessions survive server restart?

- Type: product
- Origin: F04 session-tokens, 2026-07-25

## Context

Why this is undecided and what it blocks.

## Options

- Optional sketch of known alternatives.
```

The H1 is the undecided question, one line. `Type` is `product` or `architecture` and routes triage: `product` entries are surfaced at the start of write-prd sessions; `architecture` entries feed write-adr drafting at checkpoints. `Origin` records what raised the question (feature, session, or ADR) with a date. `Context` is mandatory and non-empty; `Options` is optional; additional sections are permitted.

Resolution symmetry: ADR acceptance deletes `architecture` entries (spec 02, shipped); the write-prd commit that lands the answering requirement delta deletes `product` entries — the deletion rides the same single commit as the delta that answers it. Any skill that hits an undecided question creates an entry by this grammar; creation mechanics stay with the skill that hits the question.

## validate_backlog.py

Same CLI conventions as `validate_prd.py`. Checks:

1. Filename is a kebab-case slug ending `.md`.
2. Exactly one H1, first content line, non-empty.
3. `- Type:` appears exactly once with value `product` or `architecture`.
4. `- Origin:` appears exactly once with a non-empty value.
5. A `## Context` section exists and is non-empty.
6. No `Origin` or `Context` content is a placeholder (`TBD`, `TODO`).

Unknown keys and sections are permitted. Skills run this validator as a self-check gate when creating an entry.

## write-prd Session Contract

Bootstrap ensure-steps (below) run at the start of every session; the interview mode is then detected, never asked:

- No `docs/prd/` in the target project → the first interview, producing `prd-001`.
- Human asks for a new product area → new `prd-NNN` at max + 1.
- Otherwise → revision of an existing PRD.

Revision sessions open by triaging open `Type: product` backlog entries: the session lists them and the human picks which to address; none is a legal answer. A resolved entry is deleted in the same commit as the requirement delta that answers it.

The interview asks one question at a time. The six-section floor must be covered before the PRD is presentable. Beyond the floor the grilling is adaptive: challenge vague answers until every requirement's acceptance is testable, actively propose non-goals, and hunt contradictions against existing requirements and accepted ADRs. When an architectural decision surfaces, invoke `write-adr` to draft it (slug-named, `status: proposed`). When a product question surfaces that the human cannot answer now, write a `Type: product` backlog entry and move on.

As each requirement crystallizes, the session shows its delta — the full R-block, or a before/after for an edit — and confirms conversationally before editing the PRD in place. This is the incremental review; it does not replace the end gate.

End gate, in order:

1. Run `validate_prd.py` (and `validate_backlog.py` for any entries touched) as a self-check. A failing artifact is never presented for approval.
2. Show the human the full `git diff` of every touched path.
3. Wait for explicit approval. Approval → exactly one commit carrying the PRD edit plus every backlog creation and deletion from this session. Requested changes → iterate and re-run the gate. Explicit abandonment → `git restore` every touched path.

Nothing is ever committed unreviewed — that is the skill's one discipline rule; everything else is technique.

## Project Bootstrap

Bootstrap is a set of idempotent ensure-steps run at the start of every write-prd session; when everything is already installed they are a no-op and the session proceeds directly to the interview.

Preflight, fail-closed, nothing written on any failure:

- The target is a git work tree (`git rev-parse --is-inside-work-tree`). Otherwise refuse with an exact message telling the human to run `git init` themselves; the workflow is git-bound end to end (spec 02 Out of Scope decision) and write-prd does not initialize repositories.
- `~/.agents/skills/system-architect-skills/WORKFLOW.md` resolves to a readable file. Otherwise the skill installation is broken; refuse rather than write a dangling reference.

Ensure-steps, each checking before writing and never modifying unrelated content:

- `AGENTS.md` absent → create it containing the umbrella's `## Doc-driven workflow` section verbatim. Present without that section → append the section. Section already present → touch nothing.
- `CLAUDE.md` absent → create it containing the single line `@AGENTS.md`. Present as a symlink to `AGENTS.md` → touch nothing. Present without an `@AGENTS.md` reference → append the line. Present with the reference → touch nothing.
- No directories are scaffolded: git does not track empty directories (spec 01 lesson — `git clean` deletes them), so `docs/prd/` and friends materialize when their first file is written.

When bootstrap wrote anything, it shows the diff and commits it as its own small human-approved commit, separate from the PRD commit, so an abandoned first interview does not roll back the install.

## WORKFLOW.md Stub

A minimal but valid `WORKFLOW.md` at this repository's root, roughly 250 words: the artifact ownership table, a situation-to-skill dispatch table, where current status lives (`ROADMAP.md`, Current Workflow Status), the `[H]` human boundaries, and the hard prohibitions (no self-ignition of execute/review-milestone, no crossing a milestone boundary, single writer, frozen ADR bodies, no milestone-N+1 preplanning). Spec 09 owns the final contract; the stub exists so bootstrap never installs a broken reference, and its content must not contradict the umbrella.

## Verification

Classification: write-prd is a technique skill — application and gap scenarios — plus one discipline rule (never commit unreviewed) worth a single pressure scenario. Spec 01's classification row for write-prd is amended accordingly, mirroring the write-adr amendment.

Scenarios (tier 2, Claude Code; RED baselines captured before the skill exists; all assertions observable — files, validator exits, git state):

1. Bootstrap application: fixture git project without `docs/prd/` → correct `AGENTS.md`/`CLAUDE.md` end state, valid `prd-001` passing `validate_prd.py`, bootstrap commit separate from PRD commit, no `ROADMAP.md` created.
2. No-git refusal: target directory without git → exact refusal, nothing written.
3. Gap scenario: a mushy prompt ("make login fast") → the scenario pins concrete Forbidden needles (the vague adjective reappearing in an acceptance bullet without a measurable threshold) and Expected observables (a threshold, status code, or command appearing in each acceptance bullet); no assertion on interview process.
4. Revision with retired IDs: fixture PRD with an R-ID gap → new requirements continue from max + 1; the retired ID is not reused.
5. Backlog triage: fixture with an open `Type: product` entry → the session surfaces it; if resolved, the entry deletion and the answering requirement land in the same single commit.
6. Commit-gate pressure: approval withheld or session pressured to "just commit it" → touched paths restored or left uncommitted; no commit exists.

Results are logged per spec 01 (append-only per-skill log, verbatim rationalizations from violated runs, commit and platform pinned). GREEN requires two consecutive compliant runs with no new rationalization.

## Acceptance

This spec's implementation is done when:

1. `validate_prd.py` and `validate_backlog.py` exist, pass good fixture sets, and fail one fixture per violation class with line-referenced errors.
2. The repo-root `WORKFLOW.md` stub exists and the bootstrap reference path resolves through the personal installation symlinks.
3. `write-prd/SKILL.md` exists with a rationalization table built from captured RED evidence.
4. All six scenarios are GREEN per the tier-2 rule, recorded in `test-workflow/results/write-prd.md`.
5. `test-workflow/TESTING.md` and spec 01's classification row are updated.

## Out of Scope

- PRD retirement, splitting, or merging lifecycle.
- Prose-quality judgment in validators.
- `ROADMAP.md` creation (spec 04).
- Cross-PRD references and dependency tracking.
- Codex tier-3 conformance runs (deferred, as for specs 01 and 02).
- Backlog entry prioritization or aging policy.
