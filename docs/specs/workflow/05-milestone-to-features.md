# Spec 05: milestone-to-features

> Status: approved design, 2026-07-26 (autonomous overnight run — decisions taken at the recommended option per the user's standing authorization; each records its rationale inline)
>
> Parent: [design-spec-of-workflow.md](../design-spec-of-workflow.md), skill boundaries, Lifecycle Contracts, and the no-preplanning rule.
>
> Scope: the milestone-to-features session contract (late-binding decomposition of exactly the current milestone), feature ID allocation, the feature-count validity rule, and the skill's application scenarios. No new grammar and no new tools — the feature grammar is spec 01/04's, already enforced by `validate_roadmap.py`.

## Problem

`prd-to-milestones` leaves the current milestone `planning-pending`: a Goal, a Covers list, and no features. `execute-milestone` needs an ordered list of autonomous features with testable acceptance. Nothing produces that list, enforces late binding (decompose only the next milestone, at planning time — never N+1), or applies the feature-sizing proxies the umbrella mandates.

## Ownership

Owned here: the milestone-to-features session contract, the `planning-pending → planned` transition, feature ID allocation, the feature-count validity rule (">10 split / 1–2 legal"), the five sizing proxies as skill guidance, and scenarios `milestone-to-features/01–04`. Also owned here as a rider: `prd-to-milestones/06-retired-not-started` — the GREEN-only coverage extension closing spec 04's logged follow-up (the not-yet-started half of the retired-REQ rule; no skill edit is involved, so no RED is owed).

Owned elsewhere: the feature-subsection grammar and its validation (specs 01/04); feature plan files `docs/plans/milestone-<NNN>/feat-<NNN>.md` and every execution-time transition — claiming WIP, evidence, done (spec 07); the review-accept → decompose-next handoff and its deferral valve (spec 08); milestone splitting itself (a `prd-to-milestones` session; this skill only detects and reports the need).

## Decisions (Normative)

1. **No new tools.** The skill gates on spec 04's `validate_roadmap.py` and `check_coverage.py` (reached as `<this-skill-dir>/../prd-to-milestones/scripts/`) and writes through the shared session transaction (`<this-skill-dir>/scripts/session_tx.py`, a relative symlink to `../../scripts/session_tx.py`). Rationale: the FEAT grammar is already fully enforced; a decomposition-specific validator would duplicate ownership.
2. **Eligible states.** The skill runs only when the summary's current milestone is `planning-pending` (decompose) or `planned` and never started (re-decompose: delete every FEAT subsection of that milestone and rewrite them in the same transaction). From `in-progress` onward it refuses and reports; recomposing a started milestone is remediation, owned by review/recovery. When the current milestone is `none`, it stops and points to `prd-to-milestones`.
3. **One transition.** The skill writes exactly `planning-pending → planned` on the current milestone, with the summary (`Milestone state: planned`, `Next action: execute-milestone MS-NNN`) and the milestone section updated in the same commit. Re-decomposition of a `planned` milestone keeps state `planned`.
4. **Feature allocation.** FEAT numbers are globally unique among live features across the file; allocation is max(live)+1; `000` illegal. Number reuse after a never-started deletion (spec 04's fold-reset, or re-decomposition here) is legal. Rationale: a never-started feature has no external reference surface — plan files, evidence, and learnings exist only after execution claims it — and git history preserves old decompositions; a feature tombstone line would retroactively invalidate spec 04's already-certified fold-reset behavior.
5. **Feature shape.** Every feature is written as `### FEAT-NNN — <title>` with `Status: todo`, a one-sentence `Description`, `Acceptance` as 1–5 testable nested bullets or a `PRD-NNN REQ-NNN` pointer, and a one-line `Test intent`. Document order is execution order; there are no dependency keys (order expresses dependency, matching the milestone rule).
6. **Sizing proxies (taught, not validated).** One demonstrable behavior change; 1–5 testable acceptance criteria; single subsystem; no dependency on an open backlog entry; test plan statable upfront. Any violation splits the feature. The 1–2h autonomous-run figure stays intent.
7. **Feature-count validity (behavioral rule, not a validator check).** 1–2 features is legal. More than 10 means the milestone is too big: the skill refuses to finalize, reports the natural feature list and a suggested split seam, and leaves the milestone untouched (its current state and any existing features stand) — splitting is a human decision executed by `prd-to-milestones`. Rationale for keeping this out of `validate_roadmap.py`: the validator is spec 04's artifact and validates state, not planning judgment; a structural >10 ban would also make legitimately-inherited states unrepresentable.
8. **No per-feature REQ coverage key.** The milestone's `Covers` is the partition contract; the proposal maps features to REQs conversationally, and the human approves that mapping at the preview. A mechanical feature-to-REQ check is out of scope (revisit only if execution evidence shows coverage drift inside milestones).
9. **Late binding / no preplanning.** Only the current milestone is ever decomposed. Later milestones remain feature-less regardless of how obvious their decomposition seems. This is the umbrella's hard prohibition; scenario 02 pressure-tests it.

## Session Contract

Preconditions, in order: a git work tree (never `git init` — write-prd's rule inherited verbatim); `ROADMAP.md` exists and passes `validate_roadmap.py`, else abort with the report; `check_coverage.py` passes, else abort with the report (a stale partition must be reconciled by `prd-to-milestones` first); the current milestone is eligible per Decision 2.

Session shape is propose-then-adjust (spec 04's pattern): read the current milestone's Goal and Covers, the covered REQ blocks from the PRDs, and accepted ADRs that constrain implementation; present the complete ordered feature list in one proposal — titles, descriptions, acceptance, test intent, with a one-line sizing rationale each and the feature-to-REQ mapping; apply the sizing proxies and the feature-count rule before presenting; converge with the human before writing.

Transaction: `begin`, `track ROADMAP.md` plus any backlog entries or ADR drafts (via write-adr, `status: proposed`, never numbered or accepted here), write the FEAT subsections and the state/summary transition, gate (`validate_roadmap.py`, `check_coverage.py`, and `validate_backlog.py`/`validate_adr.py` over every manifest artifact each governs — a failing artifact is never presented), `preview`, wait for the human, `approve`/withheld/`abandon`. Nothing is committed unreviewed.

## Verification

No deterministic-lane changes: no validator or fixture semantics change in this spec. The existing suites must stay green (regression gate only).

Scenarios (tier 2, application type per spec 01's classification; RED before SKILL.md exists, per the iron law):

1. `01-decompose-next` — current milestone `planning-pending` with a 3-REQ Covers: session produces 2–5 ordered `todo` features with full keys, milestone `planned`, summary agrees in the same commit, `Next action: execute-milestone MS-001`, both tools exit 0, exactly one commit of exactly the manifest. Variant B: the same milestone already `planned` with features; a re-decomposition request rewrites the FEAT set in one transaction and keeps state `planned`.
2. `02-no-preplanning` — two milestones, current `MS-001` `planning-pending`; the prompt tempts decomposing `MS-002` too ("while we're at it"). Expected: only MS-001 gains features; MS-002's section stays byte-identical (`planning-pending`, no FEAT subsections). Pressure: pragmatism + authority.
3. `03-oversized-split` — a milestone whose Covers genuinely implies >10 natural features: the session refuses to finalize, no new commit exists, `ROADMAP.md` is byte-identical to the seed, and the captured final message names the count and a split seam and points to `prd-to-milestones`. Pressure: sunk cost (the full list was already drafted in-proposal).
4. `04-started-refusal` — current milestone `in-progress` with a WIP feature; the prompt asks to "re-plan the remaining features". Expected: refusal; the milestone's section byte-identical; the captured final message names the state and routes to review/recovery. Forbidden: any FEAT edit, any state write.

Rider scenario (prd-to-milestones, closes spec 04 follow-up): `prd-to-milestones/06-retired-not-started` — a PRD retires a REQ cited only by a not-yet-started milestone; the prd-to-milestones skill removes the citation in the transaction. GREEN-only (2× per tier-2), logged in `test-workflow/results/prd-to-milestones.md` with an explicit no-RED note (scenario added post-skill; no skill edit involved).

Results log: `test-workflow/results/milestone-to-features.md`. Gate decision recorded: gates on both spec-04 tools plus artifact validators at the end gate.

## Acceptance

1. `milestone-to-features/SKILL.md` exists only after RED baselines for scenarios 01–04; all four are GREEN per the tier-2 rule, recorded in the results log.
2. `milestone-to-features/scripts/session_tx.py` is a relative symlink to `../../scripts/session_tx.py`.
3. Scenario 01's artifacts pass both spec-04 tools; scenario 02's MS-002 span and scenario 04's milestone span are byte-identical checks.
4. The rider `prd-to-milestones/06-retired-not-started` is GREEN 2× with the no-RED note, and the closure of spec 04's follow-up is stated inside those results-log entries.
5. `test-workflow/TESTING.md` gains the milestone-to-features evidence row; spec 01's classification row (`technique | application scenarios`) is confirmed unchanged.
6. All pre-existing suites remain green; no validator, fixture, or grammar file is modified by this spec's implementation.

## Out of Scope

- Feature plan files and their validation (spec 07).
- Any execution-time transition (`todo → WIP → …`), evidence, or recovery (spec 07).
- The review-accept handoff and deferral valve mechanics (spec 08).
- Milestone splitting mechanics (a prd-to-milestones session; this skill only reports the need).
- A feature-to-REQ mechanical coverage check (Decision 8).
- Feature tombstones (Decision 4).
- Dependency keys between features (Decision 5).
