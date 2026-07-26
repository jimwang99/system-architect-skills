# Design Spec: Doc-Driven Agent Workflow

> Status: approved umbrella design, 2026-07-24
>
> Scope: cross-skill contracts only. Each focused subsystem requires its own
> design, implementation plan, and verification cycle.

## Problem

A solo system architect should spend judgment at deliberate checkpoints, not
repeat the same decisions during every feature. Between checkpoints, agents
should execute from durable documents, stop safely when those documents are
insufficient, and leave enough evidence for another session or agent to resume.

The workflow must work in both Claude Code and Codex. Portability means the same
artifacts, lifecycle transitions, safety boundaries, and observable outcomes.
It does not require identical prompts, transcripts, or native tool calls.

The initial distribution target is one user's local environments. Team
packaging and public distribution wait until the workflow has matured.

## Design Principles

1. Human judgment happens at explicit checkpoints.
2. Documents carry decisions across sessions; conversation memory does not.
3. One artifact owns each kind of truth.
4. `ROADMAP.md` is the human-facing operational status ledger.
5. Autonomous execution is sequential and single-writer.
6. Every completion claim carries evidence.
7. Claude Code and Codex share semantic skills and use native mechanics only
   where their capabilities differ.
8. Recovery derives state from documents and Git; it never trusts narration.

## Architecture

```text
                    +-----------+
                    | write-adr |
                    +-----^-----+
                          |
[H] write-prd -> [H] prd-to-milestones
                          |
                          v
               [H] milestone-to-features
                          |
                          v
               [H] execute-milestone
                          |
             sequential autonomous features
                          |
              +-----------+-----------+
              |                       |
          complete               blocked/failed
              |                       |
              v                       v
     [H] review-milestone     [H] recovery checkpoint
              |
              +----> next milestone
```

`[H]` marks human ignition or judgment. Agents never cross those boundaries
autonomously.

### Skill boundaries

| Skill | Responsibility |
|---|---|
| `write-adr` | Own the ADR format, numbering, and immutable lifecycle. |
| `write-prd` | Interview for requirements, edit living PRDs, and bootstrap projects. |
| `prd-to-milestones` | Turn PRD scope into goal-coherent, demonstrable milestones. |
| `milestone-to-features` | Decompose only the next milestone into autonomous features. |
| `execute-milestone` | Run sequential features until review-ready or a recovery checkpoint. |
| `review-milestone` | Guide the human review, disposition every finding, and accept or remediate. |
| `act-learn-improve` | Capture meaningful plan-versus-reality divergence for checkpoint review. |

No `what-is-next` skill is planned. `ROADMAP.md` must make the current state and
literal next action understandable without another workflow layer.

## Repository and Skill Layout

Every skill remains a top-level directory so the existing repository symlinks
continue to work:

```text
system-architect-skills/
├── write-prd/
│   ├── SKILL.md
│   └── scripts/                   # skill-owned validators and tools
├── execute-milestone/
│   ├── SKILL.md
│   └── references/
│       ├── claude-code.md
│       └── codex.md
├── scripts/                       # cross-skill workflow tools (session_tx.py)
├── test-workflow/
│   ├── TESTING.md
│   ├── tests/
│   ├── fixtures/
│   ├── scenarios/
│   │   └── <skill-name>/
│   └── results/
└── ...
```

`SKILL.md` owns shared semantics. A skill gets platform reference files only
when invocation, delegation, permission, or reviewer mechanics differ. There
are no parallel adapter trees and no duplicated skill implementations.
Production validators and helpers live in each skill's `scripts/` directory;
cross-skill workflow tools live at the repo-root `scripts/`. Workflow testing
artifacts (deterministic tests, fixtures, scenarios, results) live in the
top-level `test-workflow/` directory; future non-workflow test families get
sibling `test-*` directories.

The personal installation remains:

```text
~/.agents/skills/system-architect-skills -> this repository
~/.claude/skills/system-architect-skills -> this repository
```

## Artifact Ownership

| Artifact | Authority |
|---|---|
| `docs/prd/prd-NNN-<slug>.md` | Current product requirements: the "what". |
| `docs/adr/adr-*.md` | Architectural rationale: the "why". |
| `docs/decision-backlog/<slug>.md` | Unresolved questions requiring human judgment. |
| `ROADMAP.md` | Planned order, milestone and feature state, blockers, and next action. |
| `docs/plans/milestone-<NNN>/feat-<NNN>.md` | Validated implementation plan for one feature. |
| `docs/reviews/milestone-<NNN>.md` | Append-only review progress and final verdict. |
| `docs/learnings/ALI-NNN.md` | Evidence-backed plan-versus-reality divergence. |

PRDs are living documents edited in place; every PRD diff is shown to the human
and committed only after approval. ADR decision bodies become immutable when
accepted or rejected. Backlog entries exist only while unresolved. Plans
describe how to implement one feature and must be revalidated against the
current code before execution.

## `ROADMAP.md` Contract

`ROADMAP.md` combines planned scope and current workflow state. Its first
section is always a concise status view:

```markdown
## Current Workflow Status

- Current milestone: MS-003 — Authentication
- Milestone state: paused
- Active feature: FEAT-004 — WIP
- Checkpoint: recovery
- Blocker: reviewer unavailable
- Next action: invoke `execute-milestone MS-003`
```

The remainder defines milestones and their ordered features. Every feature
includes an ID, description, acceptance criteria or PRD pointer, test intent,
status, and evidence when done.

Every state-changing skill updates the current-status section and the relevant
detailed entry in the same recorded transition. Conformance tests must assert
that the two views agree. `Next action` uses the host-neutral form
`skill-name arguments`, or names a command or human task when no skill applies.
It never attempts to record the hash of the commit that contains itself.

## Lifecycle Contracts

### ADR

```text
draft/proposed ----> accepted ----> superseded
       |
       +-----------> rejected
```

Drafts use slug names and claim no permanent number. Human acceptance assigns
the next number. Accepted and rejected decision bodies are frozen. Supersession
may change only lifecycle metadata and add the successor pointer.

### Feature

```text
todo ----> WIP ----> done
             |
             +----> blocked(<backlog-slug>)
             |
             +----> failed(<reason>)

blocked/failed --[H recovery]--> todo
```

- `blocked` means missing human judgment and always links to a backlog entry.
- `failed` means a bounded execution failure, exhausted fix budget, or scope
  escape. It links to a draft learning, not a decision backlog entry.
- A temporary external outage with valid work preserved leaves the feature
  `WIP` and pauses the milestone.
- Strict sequencing prohibits starting a later feature after `blocked` or
  `failed`.
- `done` requires implementation commits, green tests, reciprocal external
  review, and a final metadata commit recording evidence.

Done evidence includes the feature base, implementation commit range, test
result, reviewer identity, reviewer verdict, and the disposition of blocking
findings.

### Milestone

```text
planning-pending -> planned -> in-progress -> review-ready -> accepted
       ^               |           |                |
       |               |           v                v
       +--[scope change]+        paused         remediating
                                   |                |
                                   +-> in-progress  +-> review-ready
```

`review-ready` requires every planned feature to be `done`. Blocked and failed
features create recovery checkpoints, not early milestone reviews. A milestone
branch is the implementation and review unit; it merges to `main` only after
human acceptance. A scope change folded into a planned milestone resets it to
planning-pending and deletes its feature entries (spec 04).

## Milestone Execution Contract

`execute-milestone` runs one milestone from explicit human ignition until
`review-ready` or a recovery checkpoint:

```text
[H] invoke
    -> validate ROADMAP, Git, PRD, and accepted ADRs
    -> create or resume milestone branch
    -> claim next sequential feature as WIP
    -> create and independently validate its plan
    -> implement with one code writer
    -> run tests
    -> run reciprocal external review
    -> record evidence and mark done
    -> repeat, or stop at a boundary
```

The initial design has no feature pipelining. Feature N+1 is not planned while
feature N executes. This removes plan invalidation and pipeline-flush machinery;
performance evidence may justify revisiting it later.

Delegation is flat. The main invocation owns the milestone loop and dispatches
fresh bounded workers. Workers never create another orchestration layer.
Interactive gates inside implementation skills are answered only from approved
documents or routed through the classification contract below.

### Cross-platform execution

- By default the host platform's native workers plan and implement, and the
  other platform provides external review.
- `execute-milestone` may select the harness per stage: planning and
  implementation can run on different platforms (for example, plan on Claude
  Code and implement with Codex workers) while the semantic skillset stays the
  same. Detailed design belongs to the execute-milestone focused spec.
- The reviewer platform always differs from the implementer platform.
  Reciprocity follows the implementer, not the orchestrating host.
- The reviewer is fresh, read-only, and receives the exact feature diff plus
  review instructions and a structured verdict schema.
- Platform adapters may use different tools but must produce the same
  artifacts, state transitions, and stop behavior.

`execute-milestone` and `review-milestone` are mechanically user-only in Claude
through the user's local skill visibility configuration. In Codex, their shared
skills begin with explicit-invocation guards, and pressure scenarios verify
that agents do not self-start either workflow.

## Question and Failure Classification

Classify a surprise before deciding whether execution can continue:

| Class | Action |
|---|---|
| Implementation choice | Decide locally; create no workflow artifact. |
| Product requirement gap | Add a backlog entry; block only if execution cannot continue. |
| Reversible architectural decision | Decide, draft an ADR, and continue. |
| Irreversible or conflicting architectural decision | Add a backlog entry, mark blocked, and stop. |
| Temporary external outage with valid work | Leave WIP, pause, and resume at the failed gate. |
| Invalid implementation, budget exhaustion, or scope escape | Preserve evidence, revert the feature-owned range, mark failed, draft a learning, and stop. |

A reversible architectural decision is one that can be undone within roughly
one feature of work. Contradictions with an accepted ADR or PRD always require
human judgment regardless of estimated reversibility.

## Review and Recovery

Per-feature review happens after tests and before `done`. Correctness findings
are fixed; false positives may be refuted only with recorded evidence;
architectural findings use the classification table.

Milestone review includes a reciprocal external pass over the complete
milestone branch diff, scoped to cross-feature integration that per-feature
reviews cannot observe. An accept verdict requires every blocking integration
finding to be fixed or refuted with recorded evidence.

Reviewer transport failure receives one retry. A second timeout,
authentication failure, or malformed result pauses the milestone with the
feature still `WIP`. The gate never silently passes and valid work is not
destroyed.

Reinvoking `execute-milestone` is the recovery path. Recovery compares
`ROADMAP.md`, the milestone branch, the feature plan, commits, tests, and review
evidence, then resumes at the first unproven gate. Uncommitted work is preserved
as an inspectable patch before any reset or revert.

`review-milestone` is human-invoked and append-as-you-go. It completes the full
review sweep before one of two verdicts:

- `accept`: all findings are dispositioned, the milestone branch merges, and
  the next milestone may be decomposed.
- `remediate`: fix features are added, execution returns to the milestone
  branch, and the milestone review later reruns.

Every interruption records the exact next action in `ROADMAP.md`.

## Project Bootstrap

The canonical ambient contract is `WORKFLOW.md` in this repository. A target
project's `AGENTS.md` contains:

```markdown
## Doc-driven workflow

Before any workflow task, read and follow
@~/.agents/skills/system-architect-skills/WORKFLOW.md.
```

Claude Code can consume the same instructions through `@AGENTS.md` in
`CLAUDE.md` or through an existing equivalent symlink between the two files.
`write-prd` preserves either arrangement and never overwrites existing project
instructions.

`WORKFLOW.md` stays compact: artifact ownership, situation-to-skill dispatch,
current-status location, human boundaries, and hard prohibitions. Detailed
procedure stays in skills. A minimal valid stub must exist before `write-prd`
ships so bootstrap never installs a broken reference.

## Verification Contract

Shared scenarios run in both Claude Code and Codex. Each run is normalized to:

```text
- artifacts and required content
- ROADMAP summary and detailed state
- Git branch, commit ranges, index, and worktree
- reviewer target and structured verdict
- literal next action or stop boundary
```

Tests assert observable state, never internal reasoning or "followed step N."
Baseline and failed runs additionally preserve the agent's stated reasoning
verbatim in the per-skill results log; rationalizations are refactor input,
never assertion targets.

Every focused skill uses RED -> GREEN -> REFACTOR:

1. Capture failures without the skill.
2. Run the scenario with the skill in Claude Code.
3. Run it with the skill in Codex.
4. Close observed loopholes.
5. Re-run both environments.

Two lanes are mandatory:

- Deterministic fixture tests stub reviewer success, findings, timeout,
  authentication failure, and malformed output.
- Live conformance tests use real Claude and Codex sessions, including
  reciprocal review.

`test-workflow/TESTING.md` records verified Claude Code, Codex, and
Superpowers versions.
Dependency upgrades must rerun adapter conformance, recovery,
explicit-ignition, and empty-human-session scenarios before support is claimed.

## Focused Design Sequence

Each item gets its own brainstormed spec under `docs/specs/workflow/` before
implementation:

1. Testing and cross-platform conformance.
2. `write-adr`.
3. `write-prd` and project bootstrap.
4. `prd-to-milestones`.
5. `milestone-to-features`.
6. `act-learn-improve` checkpoint integration.
7. `execute-milestone`, including both platform references and per-stage
   harness selection.
8. `review-milestone`.
9. Final `WORKFLOW.md` contract and end-to-end conformance.

## Out of Scope

- Team or public packaging, marketplaces, and automated upgrades.
- Multi-writer autonomous execution.
- Feature pipelining and milestone-N+1 preplanning.
- Hosted/cloud execution adapters.
- A deterministic workflow controller application.
- A `what-is-next` skill.
- Automatically applying learning recommendations.
- Per-feature human interviews.

## Platform References

- [Agent Skills specification](https://agentskills.io/specification)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Claude Code subagents](https://code.claude.com/docs/en/sub-agents)
- [Claude Code project memory and `AGENTS.md` interoperability](https://code.claude.com/docs/en/memory)
- [Claude Agent SDK structured outputs](https://code.claude.com/docs/en/agent-sdk/structured-outputs)
- [OpenAI skill authoring](https://developers.openai.com/plugins/build/skills)
- [Codex `AGENTS.md` guidance](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
