# 07 — act-learn-improve checkpoint-aware edit

**What to build:** An edit to the existing `act-learn-improve` skill so it works in the autonomous zone. Today its cycle mandates presenting the learning document to the human and looping until approval — a synchronous gate that an autonomous agent can neither pass nor legitimately skip. After the edit: the agent finishes the learning document as a draft when the divergence is fresh, and presents it at the next human checkpoint; in an interactive session, that checkpoint is now (current behavior preserved). Two divergence classes from the workflow's own rules are added as named triggers: feature sizing blow-ups (ran far over, split mid-flight, escalated) and rule-C reversibility misjudgments. The Iron Law applies: this is an edit to an existing skill, so it gets the same RED-first treatment as a new one.

**Blocked by:** 01 — Skill-testing conventions. (Independent of 02–06; can run in parallel with the main chain.)

**Status:** ready-for-agent

- [ ] RED baselines captured: autonomous scenario (feature complete, meaningful divergence, no human available) run against the *current* skill — documents verbatim whether the agent stalls awaiting approval or rationalizes skipping the document
- [ ] Autonomous scenario after edit: draft learning document written at feature end; presentation deferred to the next checkpoint; no stall, no skip
- [ ] Interactive regression scenario: in a live session the document is still presented immediately and revised until approved — existing behavior unchanged
- [ ] Trigger scenarios: a sizing blow-up and a reversibility misjudgment each cause the skill to fire; the structured format (assumption → reality → evidence → class of error → prioritized improvement items) is intact in both
- [ ] REFACTOR: loopholes closed; full suite passes
