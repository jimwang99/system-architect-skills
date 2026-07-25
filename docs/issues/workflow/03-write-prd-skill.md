# 03 — write-prd skill

**What to build:** The PRD interview. Invoked in a project, it runs the grilling protocol — one question at a time, recommended answer per question, facts looked up from the codebase and existing PRDs/ADRs rather than asked — and produces or edits a living, per-area PRD. Every edit is shown as a git diff and committed only on the human's approval. Architectural decisions surfacing mid-interview route through `write-adr`; unresolvable questions become slug-named decision-backlog entries. On first run in a project, it scaffolds the `docs/` tree and adds the WORKFLOW.md live-reference line to the project's CLAUDE.md (the referenced path is fixed now; ticket 08 populates the file).

**Blocked by:** 02 — write-adr skill.

**Status:** ready-for-agent

- [ ] RED baselines captured: agent asked to write a PRD without the skill (expected failures: no interview or multi-question barrage, bloated document, decisions guessed instead of asked, unreviewed commit)
- [ ] Interview scenario: questions arrive one at a time with a recommended answer; facts found in the fixture codebase are never asked
- [ ] Incremental scenario: existing PRD edited in place; diff presented before commit; no scenario ends with an unreviewed commit
- [ ] Escalation scenario: an architectural decision invokes `write-adr`; an unresolved question lands as a backlog entry — neither is silently decided
- [ ] First-run scenario in a bare fixture project: `docs/` structure and the CLAUDE.md import line are created
- [ ] Brevity is enforced structurally by the PRD template, verified on scenario output
- [ ] REFACTOR: loopholes closed; full suite passes
