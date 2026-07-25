# Spec: Doc-Driven Agent Workflow (write-prd → milestones → autonomous features → review loop)

> Status: `ready-for-agent` — approved via grilling interview 2026-07-24.
> Decision log lives in the conversation memory; this spec is the buildable synthesis.

## Problem Statement

As a solo system architect using AI agents for implementation, my judgment is consumed ad-hoc: every feature re-interviews me, decisions made mid-implementation evaporate when the session ends, and lessons learned are rediscovered instead of retained. Existing frameworks fail in opposite directions — GSD is an opaque 30-agent pipeline I can't inspect or trust; OpenSpec puts the human gate at the wrong altitude (per-change review) and lets architectural rationale get buried in per-change archives. I want to spend my judgment in a few concentrated, well-prepared sessions, let agents run features autonomously between those sessions, and have every decision and learning land in a brief, reviewable document that future agents actually read.

## Solution

A document-driven workflow implemented as six small skills plus one contract file, layered on top of the superpowers skill set:

- **Human checkpoints** (interview-driven): `write-prd` produces living PRDs, ADRs (via `write-adr`), and a decision backlog; `prd-to-milestones` draws goal-sized milestones; `milestone-to-features` decomposes only the *next* milestone into 1–2h autonomous features; `/review-milestone` runs the closing ritual and verdict.
- **Autonomous zone**: each feature is a fresh superpowers loop executing from documents alone, with per-feature commits, an independent codex review gating `done`, and a reversibility-based escalation rule for architectural surprises.
- **Learning loop**: the existing `act-learn-improve` skill (edited to be checkpoint-aware) captures divergences at feature end and batches human approval at milestone review, so the documents — and the workflow itself — improve continuously.
- **Contract**: a compact `WORKFLOW.md` (live-referenced from each project's CLAUDE.md) states the invariants every cold agent must honor before invoking anything.

The organizing principle throughout: **all human judgment is front-loaded into documents at checkpoints; agents never cross a checkpoint autonomously; everything observable lands in a document.**

## User Stories

### PRD authoring and evolution

1. As a system architect, I want a skill that interviews me one question at a time with recommended answers, so that writing a PRD extracts my judgment instead of my typing.
2. As a system architect, I want the interview to look up facts from the codebase and existing PRDs/ADRs itself, so that I am only asked for decisions, never for facts.
3. As a system architect, I want PRDs to be living documents edited in place per product area, so that agents have one authoritative place to read current requirements.
4. As a system architect, I want every PRD edit shown to me as a git diff before committing, so that incremental changes are reviewable at the size of one session.
5. As a system architect, I want PRDs to be brief by construction, so that reviewing one never becomes a chore I skip.
6. As an implementing agent, I want current requirements readable from one PRD file, so that I never reconstruct product truth from a pile of historical documents.
7. As a system architect, I want `write-prd` on first run to scaffold the `docs/` structure and add the WORKFLOW.md reference to the project's CLAUDE.md, so that opting a project into the workflow is a single skill invocation.

### Architecture decision records

8. As a system architect, I want a dedicated `write-adr` skill owning the ADR template, numbering, and status lifecycle, so that ADRs born in interviews and ADRs drafted by agents are structurally identical.
9. As a system architect, I want accepted ADRs to be immutable, so that the rationale behind already-built artifacts is never silently rewritten.
10. As a system architect, I want to reverse a decision by writing a superseding ADR, so that changing my mind is recorded as information rather than erasure.
11. As a system architect, I want rejected proposals recorded with their rejection rationale, so that agents stop re-proposing ideas I've already refused.
12. As an implementing agent, I want current architectural truth to be a trivial query (all ADRs with `status: accepted`), so that I can respect decisions without reading history.
13. As a user of `improve-codebase-architecture`, I want its ADR offers to automatically trigger `write-adr`, so that architecture-review-born ADRs match the house format without that skill being modified.

### Decision backlog and escalation

14. As a system architect, I want questions the interview cannot resolve logged to a decision backlog, so that open questions are queued rather than lost or guessed at.
15. As an implementing agent that discovers a *reversible* architectural decision mid-feature, I want to decide, record a draft ADR, and continue, so that the pipeline keeps moving where mistakes are cheap.
16. As an implementing agent that discovers an *irreversible or ADR/PRD-contradicting* decision, I want to mark the feature blocked, log a backlog entry, and take the next non-blocked feature, so that one-way doors always wait for human judgment.
17. As a system architect, I want backlog entries and draft ADRs named by slug with permanent numbers assigned only at acceptance, so that concurrent agents never race over a sequence counter.
18. As a system architect, I want resolved backlog entries deleted (with git preserving history) as their content moves into an ADR or PRD, so that the backlog directory always equals the set of open questions.

### Roadmap, milestones, and features

19. As a system architect, I want `prd-to-milestones` to draw milestones sized by goal coherence (one demoable capability increment), so that every milestone is a natural stop-and-demo point.
20. As a system architect, I want `milestone-to-features` to decompose only the next milestone, so that feature designs are always informed by the latest review rather than invalidated by it.
21. As a planning agent, I want structural sizing proxies (one demonstrable behavior change; 1–5 testable acceptance criteria; single subsystem; no open-backlog dependency; test plan statable upfront), so that "1–2 hours" is checkable at planning time instead of guessed.
22. As a planning agent, I want a >10-feature decomposition to force a milestone split and a 1–2-feature milestone to be legal, so that milestone size is validated where features actually exist.
23. As a system architect, I want every feature to belong to a milestone, so that no work ever ships without facing a review checkpoint.
24. As a system architect, I want a too-small PRD increment to become a small milestone or fold into a not-yet-started one — never injected into a WIP milestone, so that in-flight crash-recovery semantics stay intact.
25. As an implementing agent, I want each ROADMAP feature entry to carry ID, description, acceptance criteria or PRD pointer, and status, so that I can cold-start a feature from the roadmap alone.
26. As a system architect, I want feature statuses `todo | WIP | blocked(<backlog-slug>) | done`, so that a stalled or escalated feature is visibly different from an untouched one.
27. As a recovering agent, I want `WIP` to mean "started but never verified done", so that after a crash I inspect state instead of assuming it.
28. As a system architect, I want `done` to require evidence (commit hashes, test result line, codex review summary), so that completion is a verifiable claim, not an assertion.

### Autonomous execution

29. As an implementing agent, I want each feature to start a fresh superpowers loop reading only ROADMAP + PRD + accepted ADRs, so that features are executable from documents alone — and unexecutable features reveal under-specified documents.
30. As a system architect, I want per-feature commits, so that every feature has an auditable, revertable trail.
31. As a system architect, I want at most one autonomous agent writing code at any time, so that no file-based coordination machinery is ever needed.
32. As a system architect, I want to run parallel execution myself via worktrees when I choose, owning scheduling and merge, so that parallelism is a human decision with a human owner.
33. As an orchestrating agent, I want to plan feature M+1 (read-only, plan document only) while feature M executes, so that milestone wall-clock shrinks without violating single-writer.
34. As an executing agent claiming feature M+1, I want to validate its draft plan against the post-M codebase first, so that one feature of drift never silently corrupts execution.
35. As an orchestrating agent, I want a blocked feature M to force re-validation or discard of M+1's draft plan, so that pipeline flushes are explicit and bounded.
36. As a system architect, I want milestone-N+1 feature planning prohibited while N runs, so that no plan is ever built on assumptions a pending review exists to overturn.

### Per-feature independent review

37. As a system architect, I want an independent codex review of each feature diff after tests pass and before `done`, so that a different vendor's model checks work while fixing is cheapest.
38. As an implementing agent processing review findings, I want to fix in-scope correctness issues, refute false positives with recorded reasoning, and route architectural findings to rule C, so that external feedback is triaged with rigor instead of blind compliance or silent dismissal.

### Milestone review

39. As a system architect, I want `/review-milestone` invocable only by me, so that an interactive ritual can never fire into an empty room during an autonomous run.
40. As an implementing agent finishing a milestone's last feature, I want to stop and print the literal `/review-milestone` command, so that the human is reminded exactly when it is actionable — and the boundary is never crossed autonomously.
41. As a system architect, I want the review to complete its full sweep regardless of early findings, so that my verdict is made with complete information.
42. As a system architect, I want exactly two verdicts — accept (with every known issue explicitly dispositioned) or remediate (fix features prepended; only the review re-runs), so that nothing exits a review unassigned.
43. As a system architect, I want every step's findings and my verdicts appended to `docs/reviews/milestone-<NN>.md` as they happen, so that an interrupted review resumes instead of restarting, and the finished file is the permanent record.
44. As a system architect, I want the review to prompt me for each human step (demo verdict, per-ADR accept/reject, learning approvals, backlog triage, running `/improve-codebase-architecture`), so that an 8-step ritual becomes a guided session I cannot forget parts of.
45. As a system architect, I want to skip a human step by explicit recorded disposition, so that a clean half-day milestone gets a 15-minute review while a rough one gets the full 2 hours.
46. As a system architect, I want an accepted review to flow into `milestone-to-features` in-session — with a deferral valve that leaves a `planning-pending` marker, so that planning happens while context is hot, but never against my energy level.
47. As a system architect, I want accepted draft ADRs renamed, numbered, statused, and their citations updated by the agent during the review, so that mechanical work stays mechanical and race-free at the single human gate.
48. As a system architect, I want one milestone-level codex pass scoped to cross-feature integration, so that the only thing per-feature reviews structurally cannot see still gets independent eyes.

### Learning loop

49. As an implementing agent whose feature meaningfully diverged from plan, I want to write the draft learning document at feature end while evidence is still in context, so that milestone-time learnings are captured facts rather than reconstructions.
50. As a system architect, I want learning documents batched for approval at milestone review, so that reflection is captured autonomously but judged by me.
51. As a system architect, I want sizing blow-ups and reversibility misjudgments named explicitly as act-learn-improve triggers, so that the workflow's own rules are calibrated by the loop instead of hand-tuned.
52. As an autonomous agent, I want act-learn-improve's presentation step to be checkpoint-aware (draft now, present at next human checkpoint; interactively, that checkpoint is now), so that I neither stall waiting for approval nor rationalize skipping the document.

### Distribution and contract

53. As a system architect, I want every opted-in project's CLAUDE.md to carry one live-reference line to the canonical WORKFLOW.md in the skills repo, so that improving the workflow once updates every project instantly.
54. As a system architect, I want workflow edits to land only at milestone boundaries, so that the contract never changes under a milestone mid-run.
55. As a cold agent reading only WORKFLOW.md, I want to know which skill to invoke in which situation and what I must never do, so that the contract is sufficient without being a manual.
56. As a system architect, I want WORKFLOW.md to contain a flowchart flagging every human-action point, so that my manual obligations are visible at a glance rather than buried in prose.

## Implementation Decisions

These directory and file conventions are the workflow's API contract (they are what agents and skills program against, and are deliberately included despite the no-file-paths rule — they are interface, not implementation):

- **Artifact trichotomy**: PRD = living *what* (edited in place, diff-reviewed, never committed unreviewed) in `docs/prd/prd-NNN-<slug>.md`; ADR = immutable *why* (append-only) in `docs/adr/`; decision backlog = mutable queue of *undecided* in `docs/decision-backlog/<slug>.md`. Also `docs/learnings/`, `docs/reviews/`, and `ROADMAP.md` at repo root.
- **Layer boundary**: these skills own what-to-do and architecturally significant decisions; superpowers skills own how-to-do-it. No per-feature human interviews — feature agents treat PRD/ADR/acceptance criteria as the answered questionnaire.
- **ADR lifecycle**: `proposed` (mutable) → `accepted` (frozen) → `superseded` (frozen, pointer to successor); or `proposed` → `rejected` (frozen, rationale recorded). Draft files are `adr-draft-<slug>.md`; permanent numbers assigned only at acceptance.
- **Escalation (rule C)**: reversible (redoable in ~one feature of work) → decide, draft ADR, continue; irreversible or conflicting → `blocked(<backlog-slug>)`, log, next non-blocked feature.
- **Six skills**: `write-adr`, `write-prd` (uses the grilling interview protocol; scaffolds on first run), `prd-to-milestones`, `milestone-to-features` (late binding: next milestone only), `review-milestone` (`disable-model-invocation: true`; full-sweep-then-verdict; append-as-you-go review doc), and an edit to existing `act-learn-improve` (checkpoint-aware presentation; two new named triggers). `break-it-down` does not exist as a single skill — it was split.
- **write-adr SDO requirement**: its description must trigger on the *situation* of recording an architectural decision or rejection rationale (not only explicit requests), so `improve-codebase-architecture`'s ADR offers fire it automatically. That skill and `codebase-design` are not modified.
- **Concurrency model**: single code-writer; one coder + at most one planner (feature-level pipelining, in-session via subagent patterns); milestone-boundary crossing and milestone-N+1 pre-planning prohibited; human owns any worktree parallelism and its merges.
- **Review gates**: per-feature codex review (feature diff, after tests, before `done`); milestone codex pass (integration-only); completeness/correctness/coherence check and `/improve-codebase-architecture` at milestone review.
- **Distribution**: canonical WORKFLOW.md versioned in the skills repo, referenced live via `@~/.claude/skills/system-architect-skills/WORKFLOW.md` (symlink to the repo); `write-prd` scaffolds `docs/` and the import line. Compact contract (~300 words + flowchart marking `[H]` steps): invariants, dispatch table, hard prohibitions — process detail stays in the skills.
- **Rejected alternatives** (recorded so agents don't re-propose): adopting OpenSpec (wrong gate altitude; no elicitation/ADR/milestone/learning layers) or GSD (opaque, heavyweight); sqlite/lock coordination (solved by single-writer); hidden `.docs/` (invisible to default agent search tooling); separate delta files (git diff of a living PRD is the delta); global CLAUDE.md paste (wrong scope); a `workflow` mega-skill (on-demand loading cannot guarantee ambient presence).

## Testing Decisions

- **Methodology**: superpowers `writing-skills` TDD — RED (baseline scenarios without the skill, failures documented verbatim) → GREEN (skill written against observed failures) → REFACTOR (loopholes closed, rationalization tables built). The Iron Law applies to the `act-learn-improve` edit as much as to new skills. One skill fully tested and deployed before the next begins.
- **The seam** (single, highest-possible): fresh subagent + scenario in, document artifacts out. Every assertion is on observable documents or boundary behavior — the ADR file an agent produces, the status it writes, the stop-and-notify it prints, the question it asks or correctly does not ask. No inspection of agent internals; the document layer is the workflow's own definition of observable truth, so it is also the complete test surface.
- **Good tests** assert external behavior: *"given this scenario, the agent produced/refused this artifact"* — never *"the agent followed step 3."*
- **Per skill type**: discipline rules (rule C, milestone-boundary stop, review-before-done) get pressure scenarios with stacked pressures (time, sunk cost, exhaustion) and adversarial baselines; technique skills (interview flows, decomposition) get application and gap scenarios; the `write-adr` trigger gets the `improve-codebase-architecture` handoff scenario specifically. Wording micro-tests (5+ reps against a no-guidance control) before full scenario runs for behavior-shaping guidance.
- **Prior art**: superpowers `testing-skills-with-subagents` methodology; the existing `act-learn-improve` skill's structured-format enforcement as an in-repo example of a bulletproofed discipline skill.

## Out of Scope

- Multi-writer autonomous parallelism and any coordination machinery (sqlite, lockfiles, issue-assignment) — excluded by the single-writer rule until a real need overturns it.
- Remote/cloud session support — the live-reference distribution knowingly resolves only on machines with the skills installed.
- A second external reviewer (gemini) — codex only, until the learning loop shows review gaps.
- Automatically applying act-learn-improve improvement items — the skill documents; applying remains a separate human-approved phase.
- Modifying `improve-codebase-architecture`, `codebase-design`, or the `grilling` skill.
- Issue-tracker publication and triage-label integration for specs and features.
- Per-feature human interviews, per-change human review gates (the OpenSpec model), and any adoption of GSD components.

## Further Notes

- **Build order** (dependency-driven): `write-adr` → `write-prd` → `prd-to-milestones` → `milestone-to-features` → `review-milestone` → `act-learn-improve` edit → `WORKFLOW.md` last, since the contract references all of them.
- **Cadence expectation**: milestones complete in half a day to a couple of days; reviews are frequent and must collapse gracefully (~15–20 min clean, ~2 h rough).
- **Conventions adopted from OpenSpec** (as conventions, not tooling): diff-based incremental requirement review; the completeness/correctness/coherence verification triad.
- **Self-application**: the workflow's own rules were used to design it — decisions above were extracted by the grilling interview `write-prd` will embody, and this spec is the kind of artifact the workflow exists to produce.
