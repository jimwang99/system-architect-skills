# Doc-Driven Workflow Contract

> On any conflict, docs/specs/design-spec-of-workflow.md in the skills repository governs.

## Artifacts

| Artifact | Owns |
|---|---|
| `docs/prd/prd-NNN-<slug>.md` | Product requirements — the what. |
| `docs/adr/adr-*.md` | Architectural rationale — the why. Accepted/rejected bodies are frozen. |
| `docs/decision-backlog/<slug>.md` | Undecided questions awaiting human judgment. |
| `ROADMAP.md` | Milestone/feature state, blockers, next action. |
| `docs/plans/milestone-<NNN>/feat-<NNN>.md` | One feature's validated implementation plan. |
| `docs/reviews/milestone-<NNN>.md` | Append-only milestone review record. |
| `docs/learnings/ALI-NNN.md` | Evidence-backed plan-versus-reality divergence. |

## Dispatch

| Situation | Skill |
|---|---|
| Capture or refine product requirements; bootstrap a project | `write-prd` |
| Record an architectural decision or rejection | `write-adr` |
| Turn PRD scope into milestones | `prd-to-milestones` |
| Decompose the next milestone | `milestone-to-features` |
| Execute a milestone (human-invoked only) | `execute-milestone` |
| Review a milestone (human-invoked only) | `review-milestone` |
| Record plan-versus-reality divergence | `act-learn-improve` |

## Escalation

An architecturally significant "how" that is undoable within roughly one feature of work: decide locally, record a draft ADR, continue. Irreversible, or contradicting an accepted ADR or PRD: write a backlog entry, mark the feature `blocked(<slug>)`, stop. Contradictions always escalate regardless of estimated reversibility.

## Status

Current state and the literal next action live in `ROADMAP.md`, section `Current Workflow Status`. Recovery derives state from documents and git, never from narration. Every milestone ends with the review-milestone sweep — learnings, ADR audit, backlog triage, integration review, three-C, demo — and exactly one verdict: accept or remediate.

## Human boundaries

Humans ignite: PRD sessions, milestone planning, feature decomposition, milestone execution, milestone review, ADR acceptance/rejection. Agents never cross these boundaries on their own.

## Hard prohibitions

- Never self-start `execute-milestone` or `review-milestone`.
- Never cross a milestone boundary; stop and print the next action.
- One autonomous writer at a time; sequential features only.
- Never edit a frozen ADR body; supersede instead.
- Never pre-plan milestone N+1 while N runs.
- Never mark work done without evidence; never commit unreviewed workflow artifacts.
- Planning documents (PRD, backlog entries, ROADMAP planning states, ADR drafts) change only through a previewed, human-approved session transaction.
