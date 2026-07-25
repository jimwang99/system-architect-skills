# 06 — review-milestone skill

**What to build:** The guided milestone-review ritual, invocable only by the human (`disable-model-invocation: true`). It runs the full sweep regardless of early findings — demo verdict, completeness/correctness/coherence check, integration-scoped codex pass, `/improve-codebase-architecture` prompt, per-draft-ADR verdicts, learning-document approvals, backlog triage — appending every finding and every human verdict to the milestone's review document *as they happen*, so an interrupted session resumes without re-asking. It ends in exactly one of two verdicts: **accept** (every known issue explicitly dispositioned; flows into `milestone-to-features` in-session, with a deferral valve that leaves a `planning-pending` marker) or **remediate** (fix features prepended; only the review re-runs after). Human steps are individually skippable by explicit recorded disposition, so a clean milestone reviews in minutes.

**Blocked by:** 02 — write-adr skill (draft-ADR verdict mechanics); 05 — milestone-to-features skill (feature entries and statuses under review, and the accept-flow target).

**Status:** ready-for-agent

- [ ] RED baselines captured: agent asked to run a milestone review without the skill (expected failures: steps forgotten, verdicts unrecorded, findings without disposition)
- [ ] Fail-fast pressure scenario: demo fails at step 1; the sweep still completes and the verdict is made with full findings
- [ ] Resume scenario: session interrupted mid-review; re-invocation continues from the first unrecorded step and never re-asks a recorded verdict
- [ ] Disposition discipline: no scenario ends with an unassigned finding; skipped human steps appear as explicit recorded dispositions
- [ ] ADR acceptance mechanics: draft renamed, next number assigned, status set, citations updated — only on the human's accept verdict
- [ ] Deferral scenario: declining in-session planning leaves the `planning-pending` marker; no scenario shows the agent self-deferring
- [ ] Remediate scenario: fix features prepended to the roadmap; re-run repeats the review only, not the milestone
- [ ] REFACTOR: loopholes closed; full suite passes
