# Spec 04: prd-to-milestones and ROADMAP Ownership

> Status: approved design, 2026-07-25
>
> Parent: [design-spec-of-workflow.md](../design-spec-of-workflow.md), skill boundaries, `ROADMAP.md` Contract, and Lifecycle Contracts sections.
>
> Scope: the milestone-level ROADMAP grammar and `validate_roadmap.py` (claimed from the test harness), the cross-artifact coverage checker, the prd-to-milestones session contract including first-run ROADMAP creation, the ID naming normalization erratum to specs 01–03, and the skill's application scenarios.

## Problem

`write-prd` produces validated requirements but nothing turns them into an executable plan of demoable increments. The ROADMAP grammar pinned by spec 01 records milestone state but not milestone intent: with only `- State:`, a milestone is a title that cannot be reviewed for goal coherence and connects to no requirement. Nothing creates `ROADMAP.md` in the first place, and nothing guarantees that PRD scope and ROADMAP scope agree as PRDs evolve.

## Ownership

Owned here: the milestone-section grammar (Goal, Covers, milestone tombstones), the `MS-NNN`/`FEAT-NNN` ID forms, `validate_roadmap.py` (relocated to `prd-to-milestones/scripts/` and extended), `check_coverage.py`, the prd-to-milestones session contract with first-run ROADMAP scaffolding, the naming normalization erratum (this spec's section binds specs 01–03 and the umbrella), and scenarios `prd-to-milestones/01–05`.

Owned elsewhere: feature decomposition and the feature-count validity check (spec 05); execution-time state transitions, milestone branches, and evidence writing (spec 07); review verdicts (spec 08); the feature-level grammar semantics already pinned by spec 01 (statuses, evidence fields, tuple table — unchanged here except ID spelling).

## Naming Normalization (Normative; erratum to specs 01–03)

One ID scheme everywhere: `<PREFIX>-<NNN>` with PREFIX ∈ {`PRD`, `REQ`, `MS`, `FEAT`, `ADR`, `ALI`} and `NNN` exactly three digits, `001`–`999`; `000` is illegal; no other width is ever legal. This replaces spec 03's two-tier R-ID width rule (two digits to 99, then unpadded) with fixed three-digit width and a hard cap of 999.

- Requirement IDs: `R-NN` becomes `REQ-NNN`. PRD requirement headings are `### REQ-NNN — <title>`; the tombstone line is `- Retired: REQ-NNN, ...`; allocation stays max(live ∪ retired) + 1.
- Citations are fully qualified and uppercase: `PRD-NNN REQ-NNN` (was `prd-NNN R-NN`). ADRs are cited as `ADR-NNN`.
- ROADMAP headings: `## MS-NNN — <title>` and `### FEAT-NNN — <title>` (was `M<NN>`/`F<NN>`); summary keys cite the same forms.
- Filenames stay lowercase and unchanged: `prd-NNN-<slug>.md`, `adr-NNN-<slug>.md`. `ALI-NNN` already conforms and is untouched. Umbrella path templates become `docs/plans/milestone-<NNN>/feat-<NNN>.md` and `docs/reviews/milestone-<NNN>.md`.
- The sweep updates: `validate_prd.py` and its fixtures, `validate_roadmap.py` and its fixtures, `write-prd/SKILL.md`, write-prd and write-adr scenario files that cite IDs, spec 01 and spec 03 normative text, and the umbrella's examples. Historical records are exempt and never rewritten: `docs/plans/*`, results logs, and frozen scenario quotes inside rationalization tables (verbatim RED quotes keep their original spelling).
- Errata paragraphs are added to specs 01 and 03 (and a one-line citation-form note to spec 02) pointing here as the naming authority.

## Milestone Grammar (Normative)

```markdown
## MS-001 — Checkout core

- State: planning-pending
- Goal: a signed-in user pays the cart by card and sees the order paid — demoable end to end.
- Covers: PRD-001 REQ-001, PRD-001 REQ-003
```

- `State`, `Goal`, and `Covers` are required on every milestone. `Goal` states the one demoable capability increment and is placeholder-checked by spec 03's rule (stripped value case-insensitively equal to `TBD`/`TODO` is illegal, exact-only). `Covers` is a comma-separated list of fully qualified citations; no grouping syntax.
- Document order of milestone sections is the planned order. Milestone numbers are identity, not order: allocated at max(live ∪ retired) + 1, never renumbered, never reused. Reordering sections does not renumber them.
- A milestone that has never left `planning-pending`/`planned` may be deleted in a session; its number is recorded in an optional `- Retired milestones: MS-NNN, ...` line in the `## Current Workflow Status` section. Invariant: live ∪ retired = MS-001..MS-max, disjoint and contiguous. Milestones `in-progress` or beyond are never deleted.
- Unknown keys remain permitted and ignored (spec 01 rule unchanged).

## validate_roadmap.py (claimed and extended)

The validator moves to `prd-to-milestones/scripts/validate_roadmap.py`; spec 01's "parked beside the tests" note is superseded. CLI, exit codes, and hermeticity are unchanged: path in, `path:line: message` on stderr, 0/1/2, no filesystem access beyond the argument. Checks 1–11 from spec 01 stand with renamed forms; the deltas:

1. Heading forms are `## MS-[0-9]{3} — <title>` and `### FEAT-[0-9]{3} — <title>`; the near-miss rule now catches any heading whose text starts with `M`, `MS`, `F`, or `FEAT` followed by digits or a hyphen-digit tail that does not exactly match the grammar (wrong width, `000`, hyphen for em dash, wrong level).
2. Every milestone carries `State`, `Goal`, and `Covers` exactly once. `Goal` is non-empty and passes the placeholder rule. `Covers` parses as one or more `PRD-[0-9]{3} REQ-[0-9]{3}` citations, comma-separated, `000` illegal on either side.
3. Intra-file double assignment: the same `PRD-NNN REQ-NNN` citation appearing under two milestones (or twice under one) is an error. This check is hermetic and lives here, not in `check_coverage.py`.
4. Milestone tombstones: if `- Retired milestones:` is present it parses as `MS-NNN` citations, comma-separated; live ∪ retired must be disjoint and contiguous from MS-001; a numbering gap without a covering tombstone is an error (mirror of spec 03's REQ rule).
5. Summary keys cite the new forms: `Current milestone: MS-NNN — <title>` or `none`; `Active feature: FEAT-NNN — WIP` or `none`. The tuple table, feature statuses, evidence fields, and ordering checks are otherwise unchanged.

## check_coverage.py

`python3 check_coverage.py <path-to-ROADMAP.md>` — cross-artifact, read-only. It derives the project root from the ROADMAP's directory and reads every `docs/prd/` file whose name starts with `prd-`; such a file failing the strict filename grammar or REQ extraction is an environment error (exit 2), other files in the directory are ignored. Exit 0 all checks pass; exit 1 with `path:line: message` per violation; exit 2 on usage error, unreadable ROADMAP, a ROADMAP that fails milestone-grammar parsing, or a PRD file that fails REQ extraction (naming the file) — a malformed input is an environment error here because the session contract gates `validate_prd.py` and `validate_roadmap.py` first.

Checks:

1. Every live REQ in every PRD under `docs/prd/` is cited by exactly one milestone. An uncited live REQ is an error attributed to the requirement's heading line in the PRD.
2. Every citation resolves: the PRD file exists by filename grammar and the REQ is live in it. Citing a retired (tombstoned) REQ or a nonexistent PRD/REQ is an error attributed to the `Covers` line.
3. Nothing else. Duplicate citations are `validate_roadmap.py`'s job; feature-level facts are out of scope.

## prd-to-milestones Session Contract

Preconditions, checked in order: a git work tree (`git rev-parse`), else stop — this skill never runs `git init` (write-prd's rule inherited verbatim); at least one `docs/prd/prd-NNN-<slug>.md` passing `validate_prd.py`, else stop and point the human to write-prd; if `ROADMAP.md` exists it must pass `validate_roadmap.py`, else abort with the report — repairing a broken ROADMAP is its own task, never a side effect.

Session shape is propose-then-adjust: read all valid PRDs, then present the complete cut in one proposal — milestone titles, goals, coverage, and order, each with one line of sizing rationale. Sizing is goal coherence: one demoable capability increment per milestone, half-day-to-days of autonomous execution as intent; never sized by feature count (that check is spec 05's). The human adjusts conversationally; converge before writing anything.

First run (no `ROADMAP.md`): create it inside the session transaction with the scaffold below. Post-run status points at the first milestone.

```markdown
## Current Workflow Status

- Current milestone: MS-001 — <title>
- Milestone state: planning-pending
- Active feature: none
- Next action: milestone-to-features MS-001

## MS-001 — <title>
...
```

Update run (`ROADMAP.md` exists): run `check_coverage.py` to enumerate drift, then propose the delta. Unassigned live REQs fold into a not-yet-started milestone or become new milestones appended in planned order. Folding scope into a `planned` milestone resets its state to `planning-pending` and deletes its `FEAT` subsections in the same transaction — stale decompositions never survive a scope change (umbrella lifecycle erratum: `planned → planning-pending` is a legal transition, triggered only by scope change). Citations of retired REQs are removed from not-yet-started milestones; a started milestone citing a retired REQ is reported to the human and left untouched. Milestones `in-progress`, `paused`, `review-ready`, `remediating`, or `accepted` are scope-immutable to this skill: it never edits their sections, in any way. Reordering not-yet-started milestones is legal with approval. This skill writes exactly one state value, `planning-pending`, in exactly two situations: milestone creation and the fold-in reset; all other transitions belong to specs 05 and 07.

Every mutation flows through the session transaction (`scripts/session_tx.py`, reached via the `prd-to-milestones/scripts/session_tx.py` symlink): `begin`, `track ROADMAP.md` plus any backlog entries or ADR drafts (drafted via write-adr, `status: proposed`, never numbered or accepted here), write, gate, `preview`, wait for the human, `approve`/withheld/`abandon` — identical semantics to spec 03, including the summary-and-detail-in-one-transition rule: when a milestone's state or the current pointer changes, `## Current Workflow Status` and the milestone section change in the same commit. The end gate runs `validate_roadmap.py`, `check_coverage.py`, and `validate_backlog.py`/`validate_adr.py` over every manifest artifact each governs; a failing artifact is never presented for approval. Nothing is committed unreviewed.

## Verification

Deterministic lane, in `test-workflow/tests/` with fixtures under `test-workflow/fixtures/`:

- `test_validate_roadmap.py` extended: existing fixtures renamed to `MS-NNN`/`FEAT-NNN` forms; new bad classes — missing-goal, placeholder-goal, missing-covers, malformed-covers (two-digit ID, lowercase prefix, missing PRD qualifier, `000`), dup-covered-req (across and within milestones), ms-near-miss (`M02`, `MS-2`, `MS-02`, wrong level), feat-near-miss, tombstone-gap, tombstone-collision, retired-line-malformed; new good classes — tombstoned-gap legal, unknown-keys-still-ignored.
- `test_check_coverage.py` new: fixture trees each holding a ROADMAP plus `docs/prd/` — good (single PRD, multi-PRD, retired REQs correctly uncited); bad (unassigned live REQ, citation to retired REQ, citation to missing REQ, citation to missing PRD); exit-2 (malformed PRD, ROADMAP failing grammar).
- Rename-sweep regression: all pre-existing suites (`validate_prd`, `validate_backlog`, `validate_adr`, `check_adr_frozen`, `session_tx`, `bootstrap_project`) rerun green after the sweep.

Scenarios (tier 2, application type per spec 01's classification; RED baselines captured before `SKILL.md` exists, per the iron law):

1. `01-first-cut` — one valid PRD, no ROADMAP: session produces a scaffolded ROADMAP passing both tools, status pointing at MS-001, exactly one new commit containing exactly the manifest.
2. `02-fold-resets-planned` — PRD delta lands while the next milestone is `planned` with FEAT subsections: fold-in resets it to `planning-pending` and deletes the features in the same commit.
3. `03-wip-untouched` — a delta that most naturally belongs to the in-progress milestone: the WIP milestone's section is byte-identical afterward; scope lands elsewhere or in a new milestone.
4. `04-retired-cleanup` — a PRD retires a REQ cited by a not-yet-started milestone and one cited by a started milestone: the former citation is removed, the latter reported and untouched.
5. `05-multi-prd-cut` — two PRDs: total partition across both, no unassigned REQ, no double assignment.

Expected/Forbidden assertions speak only in artifacts, validator/checker exits, git state, and preview/report content (spec 01 conventions). Results log: `test-workflow/results/prd-to-milestones.md`. Gate decision recorded: this skill gates on both tools at the end gate.

## Acceptance

1. The naming sweep is complete: no `R-NN`, `M<NN>`, or `F<NN>` grammar forms remain in living normative docs, validators, fixtures, SKILL.mds, or scenarios (historical records exempt), and every pre-existing suite is green post-sweep.
2. `validate_roadmap.py` lives in `prd-to-milestones/scripts/`, enforces the extended grammar, and passes its extended suite; spec 01's parked-validator note is superseded by an erratum.
3. `check_coverage.py` exists with the listed check and exit-code behavior and passes its suite.
4. `prd-to-milestones/SKILL.md` exists only after RED baselines, and scenarios 01–05 are GREEN per the tier-2 rule, recorded in `test-workflow/results/prd-to-milestones.md`.
5. Errata are recorded: specs 01/03 naming paragraphs, spec 02 citation note, umbrella lifecycle (`planned → planning-pending`), umbrella path templates, WORKFLOW.md stub dispatch row, TESTING.md classification row.
6. `prd-to-milestones/scripts/session_tx.py` is a relative symlink to `../../scripts/session_tx.py`, making this skill the second consumer of the shared transaction.

## Out of Scope

- Feature decomposition, feature sizing, and the ">10 features split / 1–2 legal" check (spec 05).
- Execution-time transitions (`planning-pending → planned`, `in-progress` onward), milestone branches, evidence writing (specs 05/07).
- Dependency or ordering keys between milestones: document order is the only order; no `Depends:` key (YAGNI until an execution spec needs it).
- Effort estimates on milestones; the half-day-to-days figure stays intent, not grammar.
- Renaming `ALI-NNN` files or any filename casing change.
- A `Deferred`/icebox construct: deferral is a late milestone, per the total-mapping decision.
