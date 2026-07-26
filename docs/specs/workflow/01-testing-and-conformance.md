# Spec 01: Testing and Cross-Platform Conformance

> Status: approved design, 2026-07-24
>
> Parent: [design-spec-of-workflow.md](../design-spec-of-workflow.md), Verification Contract section.
>
> Scope: the testing conventions, validator framework, and conformance mechanics that every later focused spec runs on.

## Problem

Skills are markdown, but what they cause is testable: an agent conditioned on a skill produces observable state — artifacts, git positions, stop boundaries — that can be asserted without trusting narration. Two kinds of checks apply. Artifact structure is deterministic and belongs to machine validators. Agent behavior is probabilistic and belongs to scenario evals run with and without the skill under test.

This spec owns the conventions for both so later focused specs bring only their own scenarios and validators, never their own harness.

## Ownership

Owned here: directory layout, validator conventions, the machine-checkable `ROADMAP.md` grammar and its validator (the proving case), scenario file format, skill-type classification, the three-tier cost ladder, RED evidence discipline, reviewer stub outcomes, the results log format, and the `TESTING.md` format.

Owned elsewhere: per-skill scenarios (each focused spec), the concrete reviewer command name (`execute-milestone` spec), and validators for ADRs, plans, reviews, and learnings (the specs that own those artifacts).

## Directory Layout

```text
test-workflow/
├── TESTING.md                     # verified versions + rerun triggers
├── tests/
│   ├── test_<tool>.py             # deterministic suites for the production tools
│   └── validate_roadmap.py        # proving case; parked here until a skill owns ROADMAP
├── fixtures/
│   └── <artifact>/                # good/ and bad/<violation-class>/ sets
├── scenarios/
│   └── <skill-name>/
│       └── <NN>-<slug>.md         # one scenario per file
└── results/
    └── <skill-name>.md            # compact append-only log per skill
```

- Production tools live with their owner (revised 2026-07-25): each skill's validators and helpers in `<skill>/scripts/` (e.g. `write-adr/scripts/validate_adr.py`), cross-skill workflow tools at repo-root `scripts/` (e.g. `scripts/session_tx.py`, reached from a consuming skill via a relative symlink in its `scripts/`). `test-workflow/` holds only test artifacts. Earlier revisions kept every validator under `test-workflow/validators/` so skill directories stayed pure; that was reversed once production tools accumulated under a test-named tree and `write-hardware-spec/scripts/` had already broken the purity convention.
- Future test families for non-workflow skills get sibling `test-*` directories; nothing in this spec applies to them.
- The whole repository is symlinked into `~/.claude/skills/` and `~/.agents/skills/`; test artifacts are inert there because platforms read only `SKILL.md` unless a skill references another file.

## Validator Framework

- One validator is one Python file, stdlib only, compatible with the system Python 3.9.
- CLI contract: `python3 <owning-skill>/scripts/validate_<artifact>.py <path>`; exit 0 on pass, nonzero on failure with one line-referenced error per violation on stderr. `validate_roadmap.py` is owned by prd-to-milestones (spec 04) at `prd-to-milestones/scripts/`.
- Validators check structure only. Prose quality, judgment calls, and boundary behavior stay with agent scenarios.
- Dual-use: test lanes assert with validators, and skills run the same validator as a self-check gate in the step that writes the artifact. The recommended default is to gate; each focused spec records its skill's decision.
- Validators take the artifact path as their only required argument so they run identically inside a target project, a test fixture, and either platform.

## ROADMAP Validator (Proving Case)

`validate_roadmap.py` enforces the grammar below and these cross-checks:

1. The `## Current Workflow Status` section exists exactly once, is first, and carries every required key; required keys appear exactly once per entry throughout the file.
2. Every feature status is drawn from `todo | WIP | done | blocked(<backlog-slug>) | failed(<reason>)`; feature IDs are unique across the file.
3. Every milestone state is drawn from `planning-pending | planned | in-progress | paused | review-ready | remediating | accepted`, or `none` in the summary only; milestone IDs are unique across the file.
4. Two-view agreement: the summary's `(Current milestone, Milestone state, Active feature)` tuple is one of the legal tuples in the grammar section; the named milestone section exists with matching state; and, when not `none`, the active feature exists under the current milestone with status `WIP`.
5. Every `done` feature carries all six evidence fields with legal values: `Tests` begins `pass`, `Verdict` is `approve` or `approve-with-findings`, and `Findings` is `none` or lists every blocking finding as `fixed` or `refuted(<evidence>)`. Evidence contradicting `done` fails validation even with all six fields present.
6. Strict sequencing: within a milestone, feature statuses in document order match `done*`, then at most one of `WIP | blocked(...) | failed(...)`, then `todo*`. At most one feature is `WIP` across the entire file.
7. Milestone ordering: every milestone before the current one is `accepted`; every milestone after it is `planning-pending` or `planned`; when the current milestone is `none`, no milestone is in a mid-flight state.
8. `review-ready` and `accepted` milestones contain only `done` features.
9. `blocked(<slug>)` slugs are format-checked only (lowercase alphanumerics and hyphens); whether `docs/decision-backlog/<slug>.md` exists is a workflow-skill concern, because validators must run identically on fixtures outside any project. `failed(<reason>)` features carry a `Learning:` key of the form `docs/learnings/ALI-NNN.md`; the path format is checked, not the file's existence.
10. `Next action` is non-empty and is not a placeholder (`TBD`, `TODO`).
11. Structural strictness: any heading whose text is grammar-shaped but malformed — `MS`, `FEAT`, `M`, or `F` followed by digits at heading levels `#{1,6}`, not exactly matching `## MS-NNN — <title>` or `### FEAT-NNN — <title>` — is an error. Non-grammar-shaped sections (e.g. `## Notes`) are permitted and ignored, parallel to unknown keys.

## ROADMAP.md Grammar (Normative)

```markdown
## Current Workflow Status

- Current milestone: MS-003 — Authentication      (or `none`)
- Milestone state: in-progress                    (or `none`)
- Active feature: FEAT-004 — WIP                  (or `none`)
- Checkpoint: recovery                            (optional)
- Blocker: reviewer unavailable                   (optional)
- Next action: execute-milestone MS-003

## MS-003 — Authentication

- State: in-progress

### FEAT-004 — Session tokens

- Status: WIP
- Description: one sentence of scope.
- Acceptance: criteria, or a PRD pointer.
- Test intent: what proves this feature.
- Learning: docs/learnings/ALI-007.md          (required iff failed)
- Evidence:                                    (required iff done)
  - Base: <commit>
  - Commits: <range>
  - Tests: pass — <summary>
  - Reviewer: <identity>
  - Verdict: approve | approve-with-findings
  - Findings: none | <each blocking finding: fixed | refuted(<evidence>)>
```

Milestone sections repeat per milestone in planned order; feature subsections repeat per feature in execution order. Keys are literal; unknown keys are permitted and ignored by the validator. Headings are strict where grammar-shaped: a repeated `## Current Workflow Status` section and any near-miss `MS`/`FEAT`/`M`/`F` heading are validation errors; other sections are ignored.

The summary tuple `(Current milestone, Milestone state, Active feature)` must be one of:

| Current milestone | Milestone state | Active feature |
|---|---|---|
| `none` | `none` | `none` |
| `MS-NNN` | `planning-pending`, `planned` | `none` |
| `MS-NNN` | `in-progress`, `remediating` | one `WIP` feature, or `none` between features |
| `MS-NNN` | `paused` | the preserved `WIP` feature, or `none` |
| `MS-NNN` | `review-ready`, `accepted` | `none` |

Erratum (2026-07-25): IDs follow spec 04's naming scheme (PREFIX-NNN, three digits); milestone sections additionally require Goal and Covers keys and may retire milestone numbers — spec 04 is the naming and milestone-grammar authority.

## Scenario Conventions

One scenario is one markdown file with frontmatter (`skill`, `type`, `tier`) and five fixed sections:

1. `## Setup` — fixture repository state, stated as artifacts and git positions.
2. `## Prompt` — given to the agent verbatim.
3. `## Pressures` — which of time, sunk cost, authority, exhaustion, social, pragmatism are stacked. Discipline scenarios stack three or more.
4. `## Expected` — observables that must hold afterward.
5. `## Forbidden` — observables that must not.

Expected and Forbidden speak only in artifacts, validator results, git state, and stop boundary or next action, and — for skills whose contract includes showing a preview or naming report facts — the content of the run's preview and final message (spec 02's report observables are the precedent). "Agent followed step N" is never a valid assertion.

### Skill-Type Classification

| Skill | Type | Owes |
|---|---|---|
| `write-adr` | reference + two discipline rules | application scenarios; pressure tests: frozen-body immutability, no self-acceptance (spec 02 identified the authority boundary as distinct) |
| `write-prd` | technique + one discipline rule | application and gap scenarios; pressure test: never commit unreviewed |
| `prd-to-milestones` | technique | application scenarios |
| `milestone-to-features` | technique | application scenarios |
| `execute-milestone` | discipline | multi-pressure suite: sequencing, classification escape, silent gate pass, recovery trust, self-ignition |
| `review-milestone` | discipline | pressure suite: full sweep before verdict, disposition of every finding |
| `act-learn-improve` | pattern | recognition scenarios: meaningful divergence vs noise, and when not to write a learning |

Pressure-test budget concentrates on the two discipline skills; pressure-testing reference material is waste.

### Three-Tier Cost Ladder

```text
tier 1  wording micro-tests    5+ fresh subagent reps vs a no-guidance control
tier 2  pressure scenarios     Claude Code subagents; the REFACTOR inner loop
tier 3  cross-platform gate    Claude Code + `codex exec`; ship gate + upgrade rerun
```

- Tier 1 verifies a behavior-shaping wording lands before any full scenario spends tokens on it. Decision rule: the no-guidance control must fail in at least 3 of 5 reps, otherwise the guidance is not written; a candidate wording passes at 5 of 5 compliant reps; anything in between means tighten the wording and re-run 5 fresh reps.
- Tier 2 is where RED-GREEN-REFACTOR iterates. A scenario is GREEN after 2 consecutive compliant runs that surface no new rationalization; any violation returns the skill to REFACTOR and resets the count.
- Tier 3 runs only when every tier-2 scenario is GREEN, and again on dependency upgrades. Each scenario runs once per platform; any failure demotes the skill to tier 2, and after the fix tier 3 reruns in full — a lucky single run never ships a skill because tier-3 entry itself requires tier-2 GREEN. Codex runs are documented `codex exec` one-liners per scenario, not a runner.

### RED Discipline

- The baseline run happens before the skill is written. No skill, and no edit to a skill, without a captured failing scenario first.
- Every violated run's rationalizations are quoted verbatim in the results log. They are the raw material for the skill's rationalization table and red-flags list — refactor input, never assertion targets.

### Reviewer Stubs

The deterministic lane stubs the external reviewer with a fake command the fixture places on `PATH`, covering five outcomes: success, findings, timeout, authentication failure, malformed output. Reviewer invocation in `execute-milestone` must therefore route through a single overridable command; its name is pinned by the `execute-milestone` spec.

## Results Log

One file per skill under `test-workflow/results/`, append-only, one short entry per run:

```markdown
## 2026-07-24 — 02-blocked-then-skip — RED
- Commit: 1056ce3
- Platform: claude-code 2.1.193, model claude-fable-5
- Verdict: violated — started F05 while F04 blocked
- Rationalizations: "sequencing is about dependencies, not ritual"
```

Phases are `RED`, `GREEN`, `REFACTOR`, `TIER1`, or `CORRECTION`. A `TIER1` entry records a wording-gate outcome: the scenario field names the gate, the verdict records the candidate tally (pass = 5/5 compliant), and the entry names the RED baselines that discharge the control condition when full-scenario baselines substitute for micro-controls. `Commit` is the repository HEAD at run time and pins the exact scenario and skill revision the entry proves something about — editing either file later does not silently re-scope old results. A scenario file is therefore committed before its first recorded run; an entry whose `Commit` does not contain the scenario and skill it names is invalid. Entries are never rewritten; a mistake is corrected by appending a `CORRECTION` entry that names the superseded entries. `Platform` records both the harness version and the model identity. No transcript dumps; quotes and verdicts only.

## TESTING.md

`test-workflow/TESTING.md` holds a verified-version table (Claude Code, Codex CLI, Superpowers) with the date and scenario sets that passed, plus the umbrella's rerun triggers: dependency upgrades rerun adapter conformance, recovery, explicit-ignition, and empty-human-session scenarios before support is claimed.

## Acceptance

This spec's implementation is done when:

1. `validate_roadmap.py` exists, passes a good fixture set, and fails one fixture per violation class above with a line-referenced error.
2. The scenario convention is proven end-to-end on one toy scenario against an existing skill: RED baseline captured and GREEN evidence recorded per the scenario's tier rule (tier 2: two consecutive compliant runs), all in the results log.
3. `TESTING.md` is seeded with the currently verified versions.

## Out of Scope

- A scenario runner or any CI integration.
- Full transcript archives.
- Validators that judge prose quality.
- Per-skill scenario suites (each later focused spec owns its own).
