# 01 — Skill-testing conventions (prefactor)

**What to build:** The reusable testing scaffold every later ticket runs on, per superpowers writing-skills TDD. A skill author in this repo can: write pressure/application scenarios for a skill, capture RED baselines (agent behavior *without* the skill, verbatim), re-run the same scenarios GREEN (with the skill), and record REFACTOR iterations — all in a consistent, discoverable place. Spec: `docs/specs/design-spec-of-workflow.md` (Testing Decisions).

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] A convention document defines: where each skill's scenarios live, the scenario format (setup, stacked pressures, expected/forbidden artifacts), and how RED/GREEN/REFACTOR results are captured
- [ ] All assertions are on the document seam — artifacts produced/refused and boundary behavior — never on agent internals or "followed step N"
- [ ] The scaffold is proven end-to-end on one toy scenario against an existing skill (baseline captured, re-run recorded)
- [ ] Wording micro-test procedure (5+ reps vs. no-guidance control, manual reading of flagged matches) is documented for behavior-shaping guidance
