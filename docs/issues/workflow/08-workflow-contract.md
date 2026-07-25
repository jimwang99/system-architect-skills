# 08 — WORKFLOW.md contract

**What to build:** The compact agent contract, published at the canonical live-referenced location in the skills repo. Roughly 300 words of prose plus an ASCII flowchart that flags every human-action point (`[H]`): the artifact trichotomy (living PRD / immutable ADR / transient backlog), the what-vs-how layer boundary, the situation→skill dispatch table, rule C, the single-writer rule with its one-coder-one-planner pipelining refinement, the roadmap status vocabulary, the milestone-boundary stop, and the hard prohibitions (never commit an unreviewed PRD edit; never silently make an irreversible decision; never claim `done` without evidence; never cross a review boundary or pre-plan past one). Process detail stays in the skills — the contract says *when and what never*, not *how*.

**Blocked by:** 02, 03, 04, 05, 06, 07 — the dispatch table and prohibitions reference all of them.

**Status:** ready-for-agent

- [ ] Cold-agent scenario: an agent reading *only* WORKFLOW.md correctly names which skill to invoke for at least three distinct situations (new requirement, milestone's last feature done, architectural surprise mid-feature) and states the hard prohibitions
- [ ] Flowchart marks every human-action point, including `/review-milestone` and `/improve-codebase-architecture` invocations and PRD diff approval
- [ ] Prose stays within the compact budget (~300 words excluding the flowchart); nothing in it duplicates skill-internal process detail
- [ ] Prohibition-critical wording micro-tested against a no-guidance control per the ticket-01 procedure
- [ ] The live reference resolves: a fixture project's CLAUDE.md import line loads the canonical file through the skills symlink
- [ ] Boundary pressure scenario: an agent finishing a milestone's last feature under time pressure stops and prints the literal `/review-milestone` instruction instead of continuing
