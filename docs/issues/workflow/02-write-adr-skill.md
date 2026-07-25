# 02 — write-adr skill

**What to build:** The skill that owns what an ADR *is*: template, slug/numbering rules, and the lifecycle `proposed → accepted → superseded | rejected`. Any agent — a `write-prd` interview or a rule-C implementing agent — produces structurally identical ADRs through it. Drafts are slug-named; permanent numbers are assigned only at acceptance. Accepted records are immutable: mind-changes become superseding ADRs, refusals become rejected records with rationale.

**Blocked by:** 01 — Skill-testing conventions.

**Status:** ready-for-agent

- [ ] RED baselines captured: agents asked to record architectural decisions without the skill (expected failures: format drift, editing accepted records, missing status/lifecycle)
- [ ] Rule-C scenario: agent files `adr-draft-<slug>.md` with `status: proposed` — no number claimed
- [ ] Immutability pressure scenario (time + sunk-cost pressures): agent refuses to edit an accepted ADR and writes a superseding one instead
- [ ] Rejection scenario: refused proposal recorded as `rejected` with the load-bearing rationale
- [ ] Handoff scenario: an agent in an `improve-codebase-architecture`-style context offering to record an ADR triggers this skill from its description alone (SDO requirement — description triggers on the *situation*, not just explicit requests)
- [ ] REFACTOR: rationalization table and red-flags list built from observed loopholes; full scenario suite passes after closing them
