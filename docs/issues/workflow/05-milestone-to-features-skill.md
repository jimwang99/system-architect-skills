# 05 — milestone-to-features skill

**What to build:** Decomposition of exactly one milestone — the next one — into features an agent can execute autonomously. Each feature must pass the structural sizing proxies (one demonstrable behavior change; 1–5 testable acceptance criteria; single subsystem; no dependency on an open backlog entry; test plan statable upfront); violations force a split. A decomposition yielding more than 10 features escalates as "milestone too big — split it"; 1–2 features is legal. This skill defines the ROADMAP feature-entry format: ID, one-line description, acceptance criteria or PRD pointer, status (`todo | WIP | blocked(<backlog-slug>) | done`), and the evidence line required at `done` (commits, tests, codex review summary).

**Blocked by:** 04 — prd-to-milestones skill (consumes the milestone format it defines).

**Status:** ready-for-agent

- [ ] RED baselines captured: agent asked to plan features without the skill (expected failures: time-guess sizing, eager decomposition of later milestones, no acceptance criteria)
- [ ] Late-binding pressure scenario ("plan the whole roadmap while we're at it"): only the next milestone is decomposed
- [ ] Sizing scenario: an oversized candidate feature is split against the proxies, not waved through on a time estimate
- [ ] Validation scenario: >10-feature decomposition escalates a milestone split; a 2-feature milestone passes
- [ ] Feature entries carry ID, description, acceptance criteria or PRD pointer, and `todo` status; the `done` evidence-line format is defined
- [ ] REFACTOR: loopholes closed; full suite passes
