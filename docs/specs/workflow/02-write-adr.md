# Spec 02: write-adr

> Status: approved design, 2026-07-25 (revised same day after external review)
>
> Parent: [design-spec-of-workflow.md](../design-spec-of-workflow.md), skill-boundaries table and ADR lifecycle contract.
>
> Verification conventions: [01-testing-and-conformance.md](01-testing-and-conformance.md).

## Problem

The workflow needs one owner for architectural rationale: a skill that lets humans and agents draft decision records, lets only humans authorize freezing them, and makes the frozen record trustworthy enough that nobody re-litigates a settled question. ADRs are the "why"; PRDs stay the "what"; the decision backlog holds the "undecided". This spec pins the ADR file grammar, the lifecycle transitions, and their validation.

The lifecycle rationale ships inside `write-adr/SKILL.md`, not only here: old records explain existing artifacts, reversals carry learning as superseding records, rejected records prevent re-litigating, and stable identifiers keep citations from rotting silently.

## Ownership

Owned here: the ADR file grammar (naming, frontmatter, body), the four lifecycle operations and their transition mechanics, the backlog-resolution handoff at acceptance, `validate_adr.py`, `check_adr_frozen.py`, and the write-adr verification scenarios.

Owned elsewhere: the interview that elicits decisions (`write-prd`), the classification of when an agent may decide locally versus must block (umbrella table, `execute-milestone`), backlog entry creation (whichever skill hits the question), and migration of pre-existing ADRs (none exist; out of scope).

## Skill Shape

One directory, `write-adr/SKILL.md`, superpowers house style. No platform reference files (ADR authoring has no platform-divergent mechanics) and no helper scripts (the numbering scan is a one-liner; prose suffices).

The frontmatter description triggers on situations only, never workflow: recording an architectural decision or a rejection rationale, superseding a prior decision, an agent hitting an architectural "how" choice mid-feature, or another skill or session offering to record an architectural decision. Descriptions do not establish automatic skill-to-skill invocation; the requirement is that the situation wording covers those offers, so environments that make them (for example an installed improve-codebase-architecture skill) trigger this skill naturally.

### Authority model: authorizer vs executor

The human is the sole *authorizer* of accept and reject transitions. The agent may be the mechanical *executor*, but only after an explicit human instruction naming the draft. There are two distinct authorizations in every transition:

1. The initial instruction ("accept adr-draft-x") authorizes *preparing* the transition: preflight plus an uncommitted preview.
2. The post-diff confirmation authorizes *committing* it. The lifecycle status does not change until that commit exists.

If the human declines the preview, the skill restores exactly the paths it changed and preserves all unrelated work. Agents never initiate accept or reject, never assign numbers, and never edit a frozen body. An agent acting alone ends at presenting a draft for human decision. These are the skill's two discipline rules — frozen-body immutability and no self-acceptance — and both get pressure scenarios.

### Operations

| Operation | Authorizer | Executor | Effect |
|---|---|---|---|
| Draft | none needed | agent or human | Create `docs/adr/adr-draft-<slug>.md`, status `proposed`. |
| Accept | human | agent (mechanical) or human | Preflight, number, rename, freeze, resolve backlog, flip superseded ADR, one commit. |
| Reject | human | agent (mechanical) or human | Preflight, rename to `adr-rejected-<slug>.md`, freeze, one commit. |
| Supersede | via Draft + Accept | — | A new draft carries `supersedes:`; the old ADR flips inside the new one's acceptance. |

## ADR File Grammar (Normative)

All ADRs live in `docs/adr/` of the target project. Filenames by lifecycle stage:

```text
adr-draft-<slug>.md       proposed
adr-NNN-<slug>.md         accepted or superseded (NNN = zero-padded 3 digits)
adr-rejected-<slug>.md    rejected
```

Slugs are kebab-case (`[a-z0-9-]`, starting alphanumeric) everywhere they appear — filenames and `resolves:` values alike. Numbers exist for citation and only accepted decisions get cited; rejected records stay findable by slug. `NNN` is assigned exclusively at human-authorized acceptance as max-existing + 1 (`001` when none exist). Numbers are never reused: deleting or renaming a numbered ADR is illegal (the only legal change to one is supersession's frontmatter edit), so the filename scan is a sound allocator, and acceptance aborts on any destination or number collision at preflight. The number appears only in the filename; the body H1 is the decision title alone, so acceptance changes file identity and frontmatter but never the body.

### Frontmatter grammar (line-oriented, not YAML)

Python 3.9 stdlib has no YAML parser, so the frontmatter is a closed line-oriented format: the file's first line is exactly `---`; each following line until the closing `---` is `key: value` with a single-line scalar value; UTF-8; no quoting, comments, continuation, or multiline values; the closing delimiter line tolerates surrounding whitespace (historical tolerance, retained). Normative keys:

```markdown
---
status: proposed | accepted | rejected | superseded
created: YYYY-MM-DD
decided: YYYY-MM-DD              (required iff status is not proposed)
resolves: <backlog-slug>         (optional)
supersedes: adr-NNN-<slug>.md    (optional, set on the successor)
superseded-by: adr-MMM-<slug>.md (required iff status is superseded)
---
```

Duplicate normative keys are errors. Unknown keys are errors unless prefixed `x-` (reserved for extensions). This deliberately diverges from the ROADMAP grammar's unknown-keys-ignored rule: ROADMAP is written by many skills and tolerates extension, while ADR frontmatter is a closed schema owned by this skill, and silently ignoring a misspelling like `supersede:` would corrupt decision history.

### Body

```markdown
# <Decision title>

## Context

## Decision

## Alternatives Considered

- **<alternative>** — rejected because <one line>.

## Consequences
```

The H1 and the four sections each appear exactly once, in that order. Context, Decision, and Consequences are non-empty. Alternatives Considered contains at least one alternative bullet with an inline why-rejected, or the explicit entry `- None — <reason>`. Fenced code blocks (three or more backticks) are content, not structure: fence interiors are invisible to heading and alternative-bullet recognition, and a section whose only content is a code block is non-empty.

## Lifecycle Mechanics

```text
proposed --[H accept]--> accepted --[H accept of successor]--> superseded
    |
    +----[H reject]----> rejected
```

### Acceptance (request → preflight → preview → confirm → one commit)

**Preflight** — every check must pass or the transition stops with an actionable error and no changes:

- The named draft exists with `status: proposed` and passes `validate_adr.py`.
- The computed destination filename and number collide with nothing in `docs/adr/`.
- If `resolves:` is set, `docs/decision-backlog/<slug>.md` exists.
- If `supersedes:` is set, the target exists with `status: accepted`.
- No touched path (draft, destination, superseded target, backlog entry, files to repoint) has unrelated uncommitted changes.
- Reference scan: every hit on the draft filename is classified. Hits in mutable artifacts (ROADMAP, plans, backlog) and in proposed ADR bodies will be repointed; a hit inside a frozen ADR body aborts the transition — frozen bodies are never edited, and frozen ADRs should never have cited a draft in the first place.

**Prepare (uncommitted)**: assign number; `git mv` draft to `adr-NNN-<slug>.md`; set `status: accepted` and `decided: <today>`; delete the resolved backlog entry and report — in the preview and the final message, never as a ROADMAP edit — any ROADMAP feature currently `blocked(<slug>)` on the resolved slug (ROADMAP stays byte-identical through the transition); flip the superseded target's frontmatter only (`status: superseded`, `superseded-by: <this file>`); repoint the classified mutable references.

**Preview and confirm**: show the complete diff. The human's explicit confirmation authorizes a single commit containing the whole transition; declining restores exactly the touched paths. The body is frozen from that commit onward.

### Rejection

Same request → preflight (draft exists, valid, rejected-name path free, no unrelated changes) → prepare (rename to `adr-rejected-<slug>.md`, set `status: rejected` and `decided`) → preview → confirm → one commit. Body frozen from that commit. Rejection never touches the backlog: rejecting one proposal does not answer the underlying question, so any `resolves:` slug stays open.

### Supersession

Only expressible as acceptance of a successor. The frontmatter-only edit to the superseded ADR is the single legal post-freeze modification. There is no supersede-without-successor, and supersession means a later decision changes or reverses the earlier one — never cosmetics. A typo in a frozen body simply stands; the correct action is none.

## Validation

Two scripts with deliberately different contracts, both under `write-adr/scripts/`. Both CLIs exit 0 on pass, 1 on violations (line-referenced on stderr), and 2 on usage or environment errors (bad arguments, missing file, or — for the frozen check — not a git repository).

### `validate_adr.py <path>` — hermetic, structure only

1. Frontmatter parses per the line-oriented grammar; `status` legal; duplicate normative keys rejected; unknown keys rejected unless `x-`-prefixed.
2. Filename pattern agrees with status: `adr-draft-*` ↔ proposed; `adr-NNN-*` ↔ accepted or superseded; `adr-rejected-*` ↔ rejected; slugs kebab-case.
3. `NNN` is zero-padded three digits and unique within the file's directory.
4. `created` and (when present) `decided` are ISO dates; `decided` present iff status is not proposed.
5. `superseded-by` present iff status is superseded.
6. Body: H1 and the four sections exactly once, in the mandated order; Context, Decision, Consequences non-empty.
7. Alternatives Considered: at least one `- **…** — …` bullet or the explicit `- None — <reason>`; every alternative bullet carries an inline rejection reason.
8. `resolves:` value, when present, is a kebab-case slug.
9. Pointer integrity: `supersedes:` and `superseded-by:` values must match the numbered filename grammar, and the referenced counterpart must exist in the same directory — a missing counterpart is an error, not a skip. Status rules: a proposed file's `supersedes:` target must be `accepted` (the flip happens at this draft's acceptance); an accepted or superseded file's `supersedes:` target must be `superseded` with a reciprocal `superseded-by:` naming this file; a `superseded-by:` target must be `accepted` or `superseded`, never proposed or rejected, and must name this record in its `supersedes:`. Fixtures that exercise pointers ship their counterpart files.

### `check_adr_frozen.py <path>` — git-aware immutability check

Deliberately outside the hermetic contract (human-chosen over a body-hash design: committed history cannot be silently recomputed the way an embedded hash can). Requires the file to be inside a git repository.

Supported history model, stated explicitly: a full (non-shallow) clone, with the file's history reachable by single-path rename tracking (`git log --follow`), which is similarity-based and limited on non-linear history per git's documentation. Within that model:

1. Walk the file's history following renames; find the earliest commit in which its frontmatter status is accepted, rejected, or superseded — the freeze point.
2. Worktree status proposed and no freeze point → exit 0 (nothing is frozen yet).
3. Worktree status frozen but no provable freeze point → **exit 1, fail closed**: shallow history, delete-and-recreate, or failed rename detection are corruption or unverifiability, never success.
4. Freeze point found: compare the body (content below the closing frontmatter delimiter) at the freeze point against the worktree. Any difference → exit 1 with a line-referenced report. Frontmatter differences are ignored (supersession is legal).

Its tests build tiny scratch git repositories (the pattern the spec-01 toy scenario proved) covering: clean frozen file passes; post-freeze body edit fails; supersession frontmatter edit passes; rename-at-acceptance followed; delete-and-recreate at the same path fails closed; frozen status with truncated (shallow-like) history fails closed; rename across a merge commit exercised and its outcome documented.

## Verification Plan

Per spec 01's classification (updated alongside this spec), write-adr is reference material plus two discipline rules. Scenarios live in `test-workflow/scenarios/write-adr/`, results append to `test-workflow/results/write-adr.md`, tier ladder and RED discipline apply — baselines are captured before `SKILL.md` is written.

- Application: an executing agent hits a realistic architectural surprise mid-feature; expected observables — a draft file that passes `validate_adr.py`, feature work continues or blocks per the escalation rule, no number claimed.
- Application: human-authorized acceptance on a fixture repo; expected observables — preflight passes, rename + number + `decided`, backlog entry deleted, superseded ADR flipped frontmatter-only, mutable references repointed, exactly one commit, and a declined-preview variant restoring all touched paths.
- Application (abort path): acceptance attempted while a frozen ADR body cites the draft; expected observables — transition aborted with an actionable error, zero files changed.
- Pressure (immutability): "just fix a typo in this accepted ADR" under time and pragmatism pressure; expected observables — body byte-identical, `check_adr_frozen.py` exits 0, and no superseding draft created for a cosmetic change.
- Pressure (self-acceptance): finished draft, blocked feature, empty room; expected observables — file still `adr-draft-*`, status still `proposed`, no number assigned, feature still blocked.

## Acceptance

This spec's implementation is done when:

1. `write-adr/SKILL.md` exists in house style with the lifecycle rationale and authority model inline and a situation-only description.
2. `validate_adr.py` passes a good fixture per lifecycle stage (pointer fixtures shipping their counterparts) and fails one fixture per violation class above with line-referenced errors, via a stdlib unittest file per spec-01 conventions.
3. `check_adr_frozen.py` passes its scratch-repo test matrix, including the fail-closed cases.
4. All application scenarios (including the abort and declined-preview paths) and both pressure scenarios are GREEN per the tier-2 rule, with RED baselines and verbatim rationalizations in the results log.

## Out of Scope

- The elicitation interview (`write-prd`).
- Deciding when agents decide versus block (umbrella classification, `execute-milestone`).
- Backlog entry creation and format.
- An erratum mechanism for frozen bodies (strict immutability chosen instead; typos stand).
- Git-less authoring environments (e.g. Obsidian vaults) — vaults are read-only consumption copies synced from the git repo; every lifecycle transition requires git (decided 2026-07-25 after an impact analysis: the execution machinery is essentially git-bound, and hash-based freeze fallbacks were declined).
- Tier-3 cross-platform runs beyond what TESTING.md's rerun policy requires at ship time.
- Migrating or renumbering any existing ADRs.
