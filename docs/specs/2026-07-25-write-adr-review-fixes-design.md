# Design: write-adr Review-Fix Cycle

> Status: approved design, 2026-07-25.
>
> Inputs: subagent review of range 3de1c30..9df6e30 ("R" findings) and `codex-review.md` ("C" findings). Normative references: [spec 02](workflow/02-write-adr.md), [spec 01](workflow/01-testing-and-conformance.md). The original implementation plan (`docs/plans/2026-07-25-write-adr.md`) is history and stays untouched; this cycle's plan supersedes it where they conflict, matching the spec-01 fix-cycle precedent.

## Problem

Both reviews converge on the same verdict: the validators, fixtures, and RED→REFACTOR→GREEN loop are structurally sound, but `check_adr_frozen.py` has two demonstrated fail-open paths, the recorded evidence violates the repository's own commit-pinning and tier-2 rules, two scenarios omit lifecycle mechanics spec 02 requires them to prove, and the skill is non-portable because its runtime validators live outside the skill directory.

## Decisions (settled with the user, 2026-07-25)

1. **RED remedy — fresh baselines for all six scenarios.** CORRECTION entries supersede the six `abcaf11`-pinned RED entries; fresh no-skill baselines are captured against committed scenario files. Re-pinning was rejected: the original runs preceded the scenario commit, so they stay invalid under spec 01 no matter what SHA a correction names.
2. **Tier-2 — the spec wins.** All six scenarios need 2 consecutive compliant runs at the final skill revision. The original plan's single-run relaxation for application scenarios was a plan error, not a spec carve-out.
3. **SKILL.md size — consolidate to ~1000–1100 words, single file.** Collapse the rule/rationalization/red-flag triple-statement of the same counters while keeping every observed counter's substance. A `references/` split was explored and rejected: the oversized content is the pressure armor, and discipline content must already be in context when pressure hits — an agent rationalizing "just fix the typo" does not voluntarily open a reference file. Revisit (with a spec amendment) only if consolidation cannot reach ~1100 without thinning counters.
4. **Validator relocation — deferred.** The skill's runtime invocation path (`<this-skill-dir>/../test-workflow/...`) dangles anywhere outside this repo, so the validators are runtime dependencies that ultimately belong with the skill (as a move, not a copy — two copies of a normative grammar checker drift silently). But `test-workflow/validators/` holds several validators across skills, and the user chose to relocate them all in one future batch rather than move this pair piecemeal now. This cycle changes nothing about validator location; the portability limitation stands recorded here as the batch migration's motivation.
5. **Fenced code blocks — body checks skip them.** A fence containing `## Decision` or a `#` line is content, not structure; spec 02's body grammar gets a one-line clarification. This is the only grammar relaxation in the cycle; every other validator change tightens.

## Finding Inventory

IDs: `C<n>` = codex-review finding n; `R<n>` = subagent review Important issue n; `Rm<n>` = subagent review Minor issue n; `C-dev` = codex's "additional plan deviation"; `R-rec` = subagent review recommendation.

| ID | Finding | Disposition |
|---|---|---|
| C1 / R1 | `check_adr_frozen.py` trusts worktree status; defrost + body edit exits 0 | Fix, phase 1: find freeze point unconditionally; exit 0 only if no freeze point AND worktree not frozen; defrost regression test |
| C2 | Line normalization hides trailing-blank-line and CRLF body changes | Fix, phase 1: byte-exact body comparison; decoded text only for diagnostics; tests for both hidden-change classes |
| C3 / R2 | Six RED entries pin `abcaf11`, which lacks the scenarios | Fix, phases 2+4: CORRECTION entries, then fresh REDs per decision 1 |
| C4 / R3 | TESTING.md claims tier-2 on single-run application GREENs; 01/03 GREENs predate the final skill revision | Fix, phases 2+6+7: trim claim now, re-earn per decision 2, restore row pinned to new evidence |
| C5 | Scenarios 02/03 omit supersession flip, mutable-reference repoint, and full-restore proof | Fix, phase 3: rewrite both per spec 02's verification plan |
| C6 | `DATE_RE` accepts `2026-02-30`; H1 excluded from order check; delimiter tolerance | Fix, phase 1: `date.fromisoformat`, H1 in order check, first line exactly `---`; one bad fixture each |
| C7 / Rm5 | Env errors exit 1 (or traceback) instead of the exit-2 contract | Fix, phase 1: exit 2 + one-line stderr in both CLIs; subprocess tests. Undecodable content stays exit 1 — UTF-8 is part of the grammar |
| C8 | Scenario setup blocks are comment placeholders, not reproducible | Fix, phase 3: fully executable self-contained setup blocks in all six scenarios |
| R4 | Spec's rename-across-a-merge case untested and undocumented | Fix, phase 1: scratch-repo test; observed outcome documented in the test |
| Rm6 | `check_body` counts headings inside code fences | Fix, phase 1 per decision 5; good fixture with a fence |
| Rm9 | Spec's "note any ROADMAP feature `blocked(<slug>)`" dropped from SKILL.md Prepare | Fix, phase 5 |
| Rm10 | `- None — <reason>` alternatives path has no good fixture | Fix, phase 1 |
| Rm12 | `saw_proposed` counts proposed versions after the freeze point | Fix, phase 1: only ancestors strictly before the freeze point |
| C-dev / Rm8 | SKILL.md 1,401 words vs <900 plan target; scripted-reply harness mechanics heavy | Fix, phase 5 per decision 3 |
| — | Skill non-portable: validators outside the skill directory | Deferred per decision 4: batch migration of all `test-workflow/` validators, a future cycle |
| R-rec | Shared `adr_common.py` | Rejected by both reviews and this design: the frozen checker must parse historical, possibly pre-grammar revisions; the two-parser split is deliberate |

## Phases

Serial, one branch. Deterministic work first, evidence last, so every scenario run happens exactly once against the final revision of everything.

**Phase 1 — validator fixes, TDD.** Every fix lands as failing test → fix → green, in place under `test-workflow/validators/`.

`check_adr_frozen.py`: (a) fail-closed entry path per C1 — walk history and locate the freeze point before consulting worktree status; (b) byte-exact body comparison per C2 — freeze-point body bytes from raw `git show` output vs worktree file bytes, delimiter lines located byte-wise tolerating `\r\n`, any body-byte difference fails, frontmatter-only supersession still passes; (c) `saw_proposed` restricted to commits strictly before the freeze point per Rm12; (d) missing path / not-a-repo → exit 2, concise stderr, no traceback, per C7; (e) rename-across-a-merge scratch-repo test per R4 with the observed `--follow` outcome recorded in the test — fail-closed semantics make either outcome safe, but it must be documented, not assumed.

`validate_adr.py`: (f) `datetime.date.fromisoformat` for `created`/`decided` (bad fixture `2026-02-30`); (g) H1 must precede all four sections — included in the order check (bad fixture); (h) first line must be exactly `---`, no whitespace tolerance (bad fixture); (i) missing/unreadable path → exit 2, undecodable content stays a violation (subprocess tests); (j) fenced code blocks skipped by all body checks (good fixture embedding `## Decision` in a fence), with the decision-5 one-line clarification added to spec 02's body grammar in the same commit; (k) good fixture exercising `- None — <reason>`.

**Phase 2 — evidence truth-up.** Immediate, before any reruns, so the log stops overstating on the first commit that touches it: one CORRECTION entry naming the six superseded RED entries (wrong pin; runs preceded the scenario commit), one CORRECTION recording why the existing application GREENs do not establish tier-2 (single runs; 01/03 additionally pinned to a pre-final skill revision), and TESTING.md's `write-adr/01-06` claim trimmed until phase 7 re-earns it.

**Phase 3 — scenarios.** Rewrite 02: seed gains an accepted `adr-002-sync-transport.md` that the draft `supersedes:`, plus mutable references to the draft filename in a plan file and in a proposed ADR body; Expected asserts the reciprocal flip (`status: superseded`, `superseded-by:` naming the successor, body byte-identical via `check_adr_frozen.py` exit 0), the repointed references, backlog deletion, and exactly one commit. Rewrite 03 to decline that same full transition, asserting every touched path restored and `git status --short` empty. All six scenarios get fully executable, self-contained setup blocks (heredocs writing exact file contents; scenario 05 builds a genuine draft→accept lineage whose accept commit touches frontmatter only). Commit before any run — spec 01's commit-before-run rule.

**Phase 4 — fresh RED baselines.** Six no-skill runs (fresh subagent per scenario, `model: sonnet`, prompt = scenario Prompt + scratch path + "Work only inside that directory. Do not invoke any skills."), observables asserted from repo state only, rationalizations recorded verbatim, entries pinned to the actual HEAD containing the scenarios. New rationalizations become phase-5 input.

**Phase 5 — SKILL.md.** One commit carrying: the Prepare step's missing "note any ROADMAP feature currently `blocked(<slug>)`" restored (spec 02 Prepare, consistent with "leave status as-is — noting is not flipping"); consolidation per decision 3, folding in any phase-4 rationalizations. The word-count target in this cycle's plan is ~1000–1100 with the recorded rationale for exceeding the original <900.

**Phase 6 — GREEN runs.** All six scenarios × 2 consecutive compliant runs against the final skill revision, dispatched per the phase-4 recipe plus "First read and follow <repo>/write-adr/SKILL.md." Any violation: capture the rationalization verbatim, extend the table (REFACTOR commit), reset that scenario's count, rerun. Entries appended and committed per batch so every entry's `Commit` contains what it names.

**Phase 7 — close-out.** Restore the TESTING.md row citing the new evidence; run both validator suites; sweep both reviews' findings against the final diff and record the disposition of each.

## Out of Scope

- Rewriting `docs/plans/2026-07-25-write-adr.md` (append-only history; this cycle's plan records the corrections).
- Relocating any validator script (decision 4: one future batch for all of `test-workflow/validators/`).
- A shared `adr_common.py` (see inventory).
- An erratum mechanism for frozen bodies, tier-3 runs beyond TESTING.md's rerun policy, and everything spec 02 already excludes.
