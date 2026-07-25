# Spec 03: write-prd and Project Bootstrap

> Status: approved design, 2026-07-25; revised same day after external review (transaction contract, ID tombstones, bootstrap state table, lexical rules).
>
> Parent: [design-spec-of-workflow.md](../design-spec-of-workflow.md), skill boundaries and Project Bootstrap sections.
>
> Scope: the PRD and decision-backlog artifact grammars with their validators, the session transaction contract, the write-prd session contract, project bootstrap mechanics, and the minimal `WORKFLOW.md` stub.

## Problem

The workflow needs one owner for product requirements: a skill that grills the human until requirements are testable, edits living PRDs under a review gate, and bootstraps a target project so every later skill finds the ambient contract in place. PRDs are the "what"; ADRs stay the "why" (spec 02); the decision backlog holds the "undecided". Spec 02 left the backlog entry format unowned while `write-adr` already consumes and deletes entries via `resolves:` — this spec closes that gap because `write-prd` is the primary creator of backlog entries.

## Ownership

Owned here: the PRD file grammar and `validate_prd.py`, the decision-backlog entry grammar and `validate_backlog.py`, the session transaction contract (shared by the PRD end gate and bootstrap), the write-prd session contract, project bootstrap mechanics, the minimal repo-root `WORKFLOW.md` stub, and the write-prd verification scenarios.

Owned elsewhere: ADR grammar and lifecycle (spec 02), `ROADMAP.md` creation and milestone decomposition (spec 04), the final `WORKFLOW.md` contract (spec 09), and how `execute-milestone` creates backlog entries mid-run (spec 07 — it follows the grammar pinned here).

## Lexical and Parser Rules (Normative)

Both validators implement these exact rules; prose elsewhere in this spec defers to them.

- Slug: `[a-z0-9]+(?:-[a-z0-9]+)*` — no leading, trailing, or doubled hyphen. (Stricter than the `[a-z0-9][a-z0-9-]*` that `validate_adr.py` ships; tightening that is a ledgered spec 02 follow-up, not this spec's work.)
- PRD number: exactly three digits, `001`–`999`. `000` is illegal. If allocation would exceed `999`, abort and escalate to the human; never wrap or widen silently.
- Requirement ID: `R-` followed by two or more digits, zero-padded to two below 100, minimum `R-01`. `R-00` is illegal.
- Placeholder: a value is a placeholder iff, after stripping surrounding whitespace, it case-insensitively equals `TBD` or `TODO`. Exact-value only — `TODO later` is not caught; prose quality stays with humans.
- Parser model: line-oriented, single pass. Fenced code blocks (``` fences) are opaque — headings and key lines inside them are content, never structure. An unknown `- Key:` line and its indented continuation lines belong to the enclosing block and are ignored together. Blank lines between blocks are insignificant.

## PRD File Grammar (Normative)

PRDs live at `docs/prd/prd-NNN-<slug>.md`, one per product area. `NNN` is assigned at creation as max-existing + 1 (`001` when none exist). Creation happens only inside a human-gated write-prd session, and deleting or renaming a PRD is illegal — there is no retirement lifecycle yet — so the filename scan is a sound allocator, the same argument as ADR numbering (spec 02). PRD numbers are never reused. The number appears only in the filename; the H1 is the product-area title alone.

Six H2 sections are mandatory, in this order, each non-empty: `Purpose`, `Users`, `Non-goals`, `Constraints`, `Success criteria`, `Requirements`. The first five are the interview coverage floor made machine-checkable. Additional H2 sections are permitted after the required six — a living document a human also edits should not fight its owner. This tolerance is a deliberate divergence from the ADR grammar's closed frontmatter, for the same reason ROADMAP tolerates unknown keys: mutable artifacts favor tolerance, frozen artifacts favor strictness.

`Constraints` holds product-level constraints only (platform, compliance, budget, compatibility). Architectural decisions belong in ADRs; the skill text polices this boundary, the validator cannot. `Success criteria` holds product-level measurable outcomes, distinct from per-requirement acceptance.

The `Requirements` section opens with an optional retirement tombstone line, followed by requirement blocks and nothing else:

```markdown
## Requirements

- Retired: R-02, R-05

### R-03 — Session expiry

- Statement: Sessions expire after a configurable idle timeout.
- Acceptance:
  - An idle session past the timeout rejects the next request with 401.
  - The timeout is configurable per deployment, default 30 minutes.
```

Heading grammar is `### R-NN — <title>`. Each block carries `- Statement:` exactly once (one sentence; the skill owns sentence discipline, the validator checks presence and non-emptiness) followed by `- Acceptance:` exactly once with one or more nested, non-empty, testable bullets. Other `- Key:` lines are permitted and ignored per the parser model.

Requirement IDs are never reused, and the tombstone makes that locally checkable: removing a requirement block is legal only together with adding its ID to `Retired` in the same commit. Live IDs are unique and strictly ascending in document order; the `Retired` list is ascending with no duplicates; the two sets are disjoint; and their union is exactly the contiguous range `R-01`..`R-<max>`. New IDs are assigned as max(live ∪ retired) + 1 — retiring the highest ID therefore never frees it. A gap not covered by the tombstone is a validation error (silent removal); a collision with the tombstone is a validation error (reuse).

The citation form for a requirement, used by later specs (ROADMAP `Acceptance:` pointers), is `prd-NNN R-NN`.

## validate_prd.py

Spec-01 validator conventions: stdlib Python 3.9, path argument, one `path:line: message` per violation on stderr, exit 0 pass / 1 violations / 2 usage or read error. Checks:

1. Filename matches `prd-NNN-<slug>.md` under the lexical rules.
2. Exactly one H1, and it is the first content line.
3. The six required H2 sections appear exactly once each, in the required order, before any unknown H2 section.
4. Every required section is non-empty (content beyond its heading).
5. The `Requirements` section contains only: at most one `- Retired:` line before the first requirement block, then requirement blocks whose headings match the requirement-ID grammar.
6. Live R-IDs are unique and strictly ascending; the `Retired` list is ascending with no duplicates.
7. Live and retired IDs are disjoint, and their union is exactly `R-01`..`R-<max>` contiguous.
8. `Statement` appears exactly once per requirement, before `Acceptance`, with a non-empty value.
9. `Acceptance` appears exactly once per requirement, with at least one nested non-empty bullet.
10. No `Statement` value or acceptance bullet is a placeholder.

Dual-use per spec 01: write-prd runs this validator as a self-check gate before presenting any PRD for approval.

## Decision-Backlog Entry Grammar (Normative)

Entries live at `docs/decision-backlog/<slug>.md`, slug per the lexical rules, no numbers — backlog entries are transient (memory Q5: transient items get slugs; only accepted artifacts get numbers).

```markdown
# Should sessions survive server restart?

- Type: product
- Origin: F04 session-tokens, 2026-07-25

## Context

Why this is undecided and what it blocks.

## Options

- Optional sketch of known alternatives.
```

The H1 is the undecided question, one line. The metadata keys `Type` and `Origin` must appear between the H1 and the first H2 section — metadata buried under a later section is a validation error. `Type` is `product` or `architecture` and routes triage: `product` entries are surfaced by write-prd sessions; `architecture` entries feed write-adr drafting at checkpoints. `Origin` records what raised the question (feature, session, or ADR) with a date. `Context` is mandatory and non-empty; `Options` is optional; additional sections and unknown keys are permitted per the parser model.

Entries carry no product-area scope field: triage lists every open `product` entry in every session mode and the human picks. For a solo user with a short backlog the question's own wording carries its scope; a `Scope:` field is deferred until triage noise actually appears.

Resolution symmetry: ADR acceptance deletes `architecture` entries (spec 02, shipped); the write-prd commit that lands the answering requirement delta deletes `product` entries — the deletion rides the same single commit as the delta that answers it. Any skill that hits an undecided question creates an entry by this grammar; creation mechanics stay with the skill that hits the question.

## validate_backlog.py

Same CLI conventions as `validate_prd.py`. Checks:

1. Filename is a legal slug ending `.md`.
2. Exactly one H1, first content line, non-empty.
3. `- Type:` appears exactly once, between the H1 and the first H2, with value `product` or `architecture`.
4. `- Origin:` appears exactly once, between the H1 and the first H2, with a non-empty value.
5. A `## Context` section exists and is non-empty.
6. No `Origin` value or `Context` content is a placeholder.

Skills run this validator as a self-check gate when creating an entry.

## Session Transaction (Normative)

The PRD end gate and bootstrap both run this transaction; it exists because plain `git diff` previews nothing for untracked files and `git restore` cannot roll them back.

- **Manifest.** The session keeps an explicit list of every path it creates, modifies, or deletes: the PRD, backlog entries, ADR drafts, `AGENTS.md`, `CLAUDE.md`. A path enters the manifest at the moment the session first intends to touch it. Paths outside the manifest are never touched, staged, or committed.
- **Manifest preflight.** At entry time the path must be clean: a tracked path has no staged or unstaged changes; an untracked path does not exist. A dirty path aborts with a report — pre-existing human work is never absorbed or restored away. This matches spec 02's touched-path cleanliness preflight.
- **Preview.** Tracked modifications and deletions are shown as diffs; untracked additions are shown as complete file contents. A preview that omits a manifest path is a contract violation.
- **Approve.** Stage and commit exactly the manifest (`git add -- <paths>`), nothing else. Never a broad `git add`.
- **Approval withheld.** Requested changes → iterate and re-run the gate. Silence or deferral → leave the exact session patch uncommitted and reviewable; commit nothing.
- **Abandon.** Explicit abandonment restores every tracked manifest path to its recorded pre-session state and deletes every file the session created. The end state is the pre-session filesystem and index for manifest paths, with all other paths untouched.
- **Write failure.** A failure mid-sequence triggers the same rollback as abandonment, then reports.

## write-prd Session Contract

Bootstrap ensure-steps (below) run at the start of every session. The session then inventories `docs/prd/` for files matching the PRD filename grammar — directory existence proves nothing; an empty or absent directory means no PRDs. A file in `docs/prd/` that fails the filename grammar aborts the session with a report (fail closed, like every malformed-inventory case in this workflow).

Interview mode follows from the inventory and the request:

- No PRDs → the first interview, producing `prd-001`.
- The human asks for a new product area → new `prd-NNN` at max + 1.
- Exactly one PRD and the request does not name a new area → that PRD is the revision target.
- Multiple PRDs and the request does not uniquely name one → the human names the target. Mode is detected; the target may require asking.

A revision target must pass `validate_prd.py` before the interview edits it; a failing PRD aborts with a report — repairing it is its own task, not a side effect of an interview.

Every session mode opens by triaging open `Type: product` backlog entries: the session lists them and the human picks which to address; none is a legal answer. A resolved entry is deleted in the same commit as the requirement delta that answers it.

The interview asks one question at a time. The six-section floor must be covered before the PRD is presentable. Beyond the floor the grilling is adaptive: challenge vague answers until every requirement's acceptance is testable, actively propose non-goals, and hunt contradictions against existing requirements and accepted ADRs. When a product question surfaces that the human cannot answer now, write a `Type: product` backlog entry and move on.

When an architectural decision surfaces, invoke `write-adr` to draft it (slug-named, `status: proposed`, spec 02). The draft is a session artifact: it enters the manifest, must pass `validate_adr.py` at the end gate, appears in full in the preview, lands in the same approved commit, and is deleted on abandonment. `write-adr` remains the schema owner; acceptance remains a separate human-authorized lifecycle operation.

As each requirement crystallizes, the session shows its delta — the full R-block, or a before/after for an edit — and confirms conversationally before editing the PRD in place. This is the incremental review; it does not replace the end gate.

End gate: run `validate_prd.py`, `validate_backlog.py`, and `validate_adr.py` over every manifest artifact they govern — a failing artifact is never presented for approval — then run the session transaction's preview, approval, withheld, and abandon branches as defined above. Nothing is ever committed unreviewed — that is the skill's one discipline rule; everything else is technique.

## Project Bootstrap

Bootstrap is a set of idempotent ensure-steps run at the start of every write-prd session; when everything is already installed they are a no-op and the session proceeds directly to the interview.

Preflight, fail-closed, nothing written on any failure:

- The target root is `git rev-parse --show-toplevel`, resolved and displayed to the human before any write; `--is-inside-work-tree` alone proves membership, not identity. All bootstrap paths are relative to this root. A target that is not a git work tree is refused with an exact message telling the human to run `git init` themselves; the workflow is git-bound end to end (spec 02 Out of Scope decision) and write-prd does not initialize repositories.
- `~/.agents/skills/system-architect-skills/WORKFLOW.md` resolves to a readable file. Otherwise the skill installation is broken; refuse rather than write a dangling reference.

The canonical content is the umbrella's `## Doc-driven workflow` section, and the check is the exact reference line `@~/.agents/skills/system-architect-skills/WORKFLOW.md` within it — heading presence alone proves nothing. Ensure-steps follow this state table exhaustively; every "stop" reports the exact state and changes nothing:

| Path | State | Action |
|---|---|---|
| `AGENTS.md` | absent | create with the canonical section |
| `AGENTS.md` | regular file, section absent | append the canonical section |
| `AGENTS.md` | regular file, section present, reference line intact | no-op |
| `AGENTS.md` | regular file, section heading present, reference line missing or altered | stop — malformed ambient contract; the human repairs it (existing instructions are never rewritten) |
| `AGENTS.md` | symlink or non-regular file | stop |
| `CLAUDE.md` | absent | create containing the single line `@AGENTS.md` |
| `CLAUDE.md` | symlink to `AGENTS.md` | no-op |
| `CLAUDE.md` | regular file, `@AGENTS.md` line present | no-op |
| `CLAUDE.md` | regular file, reference absent | append the line |
| `CLAUDE.md` | symlink to anything else, or non-regular file | stop — appending would follow the link and modify an unrelated file |

No directories are scaffolded: git does not track empty directories (spec 01 lesson — `git clean` deletes them), so `docs/prd/` and friends materialize when their first file is written.

Bootstrap writes run under the session transaction: the touched paths form their own manifest, the preview shows appended sections as diffs and new files in full, and approval commits exactly that manifest as its own small commit, separate from the PRD commit, so an abandoned first interview does not roll back the install. Explicit decline of the bootstrap preview rolls back per the transaction and ends the session — the workflow does not proceed without its ambient contract. A write failure mid-sequence rolls back the same way.

## WORKFLOW.md Stub

A minimal but valid `WORKFLOW.md` at this repository's root, roughly 250 words: the artifact ownership table, a situation-to-skill dispatch table, where current status lives (`ROADMAP.md`, Current Workflow Status), the `[H]` human boundaries, and the hard prohibitions (no self-ignition of execute/review-milestone, no crossing a milestone boundary, single writer, frozen ADR bodies, no milestone-N+1 preplanning). Spec 09 owns the final contract; the stub exists so bootstrap never installs a broken reference, and its content must not contradict the umbrella.

## Verification

Classification: write-prd is a technique skill — application and gap scenarios — plus one discipline rule (never commit unreviewed) worth pressure testing. Spec 01's classification row for write-prd is amended accordingly, mirroring the write-adr amendment.

Two lanes, per spec 01.

**Deterministic fixture lane** (scripted tests, no agent): every bootstrap state-table row including both stop-on-symlink cases; the malformed-section stop; append-then-fail rollback; abandonment deleting session-created untracked files while preserving a pre-existing dirty non-manifest path; approval-withheld leaving the exact session patch uncommitted; manifest preflight rejecting a pre-dirtied path. Validator fixtures cover one bad fixture per check and per near-miss class: trailing- and double-hyphen slugs, `prd-000`, `R-00`, tombstone-live collision, gap without tombstone, retired list out of order, metadata under `## Options`, fenced-code decoy headings and keys, `TODO`-cased placeholders.

**Tier-2 scenarios** (Claude Code; RED baselines captured before the skill exists; all assertions observable — files, validator exits, git state):

1. Bootstrap application: fixture git project without PRDs → correct `AGENTS.md`/`CLAUDE.md` end state, valid `prd-001`, bootstrap commit separate from PRD commit, no `ROADMAP.md` created.
2. No-git refusal: target directory without git → exact refusal, nothing written.
3. Gap scenario, prompt-specific: "make login fast" → Expected: the resulting requirement's acceptance carries a response-time bound with measurement conditions; Forbidden: `fast` or any synonym appearing in an acceptance bullet without a numeric bound. No assertion on interview process.
4. Highest-ID retirement: fixture PRD whose highest requirement is tombstoned → the new requirement takes max(live ∪ retired) + 1; Forbidden: any tombstoned ID reappearing live.
5. Backlog triage outside revision mode: a new-area session with an open `product` entry → the entry is surfaced; if resolved, its deletion and the answering requirement land in the same single commit.
6. ADR draft mid-session: the interview surfaces an architectural decision → a draft passing `validate_adr.py` exists, appears in the preview, and lands in the session commit; the abandonment variant leaves no draft on disk.
7. Multi-PRD ambiguity: two valid PRDs and a request naming neither → the session asks; Forbidden: any edit to either PRD before the human names the target.
8. Abandonment vs withheld: explicit abandonment restores the pre-session state (session-created files gone); the approval-withheld variant leaves the exact patch uncommitted with no commit created.

Results are logged per spec 01 (append-only per-skill log, verbatim rationalizations from violated runs, commit and platform pinned). GREEN requires two consecutive compliant runs with no new rationalization.

## Acceptance

This spec's implementation is done when:

1. `validate_prd.py` and `validate_backlog.py` exist, pass good fixture sets, and fail one fixture per violation class and near-miss class with line-referenced errors.
2. The deterministic fixture lane covers the bootstrap state table and every session-transaction branch, and passes.
3. The repo-root `WORKFLOW.md` stub exists and the bootstrap reference path resolves through the personal installation symlinks.
4. `write-prd/SKILL.md` exists with a rationalization table built from captured RED evidence.
5. All eight scenarios are GREEN per the tier-2 rule, recorded in `test-workflow/results/write-prd.md`.
6. `test-workflow/TESTING.md` and spec 01's classification row are updated.

## Out of Scope

- PRD retirement, splitting, or merging lifecycle.
- Prose-quality judgment in validators.
- `ROADMAP.md` creation (spec 04).
- Cross-PRD references and dependency tracking.
- Codex tier-3 conformance runs (deferred, as for specs 01 and 02).
- Backlog entry prioritization, aging policy, and a `Scope:` field (rejected as YAGNI for a solo short backlog; revisit if triage noise appears).
- Git-history-based allocation for PRD numbers (deletion is illegal, so the filename scan stays sound — the spec 02 argument; requirement IDs get tombstones instead because retirement is legal).
