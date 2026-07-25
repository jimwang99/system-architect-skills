# 04 — prd-to-milestones skill

**What to build:** PRD → milestone list in ROADMAP.md, via a short human-facing planning session. Milestones are sized by goal coherence — one demonstrable capability increment with a demo statement, roughly half a day to a couple of days of autonomous run as intent — never by feature count, because features do not exist yet (late binding is ticket 05's job). Handles the small-PRD-delta path: a deliberately small milestone, or folding into a not-yet-started milestone; never injects scope into a WIP milestone.

**Blocked by:** 03 — write-prd skill (consumes the PRD format it defines).

**Status:** ready-for-agent

- [ ] RED baselines captured: agent asked to break a PRD into a roadmap without the skill (expected failures: eager decomposition into features, feature-count-sized milestones, no demo statements)
- [ ] Decomposition scenario: milestones carry goal + demo statement; no feature lists are produced
- [ ] Small-delta scenario: agent proposes small-milestone vs. fold-into-planned options and asks the human; the WIP milestone is never modified
- [ ] ROADMAP.md milestone-section format is defined by this skill and produced consistently across scenarios
- [ ] REFACTOR: loopholes closed; full suite passes
