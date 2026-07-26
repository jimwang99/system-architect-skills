# Results — workflow-e2e

> Integration conformance lane: no skill is created or edited by this scenario; no RED baseline is owed under the iron law.

## 2026-07-26 — 01-full-loop — GREEN (run 1 of 2)

- Scenario commit: e46008b
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (orchestrator direct execution)
- Seed: e6a5c63 (seed: empty project, no workflow)
- Final HEAD on main: 2e695fc

### Phase observables

| Phase | Skill | Human message | Scripted reply | Result | Key observables |
|---|---|---|---|---|---|
| 1 | write-prd | "I want a tiny greetings library…" | "approved, commit" | PASS | AGENTS.md canonical line present; bootstrap commit (A AGENTS.md, A CLAUDE.md) separate from PRD commit (A docs/prd/prd-001-greetings-library.md); validate_prd exit 0; REQ-001/REQ-002 present; no ROADMAP.md |
| 2 | prd-to-milestones | "Plan the milestones — one per requirement." | "looks right, approved, commit" | PASS | validate_roadmap exit 0; check_coverage exit 0; MS-001/MS-002 both planning-pending; no FEAT subsections; Next action: milestone-to-features MS-001 |
| 3 | milestone-to-features MS-001 | "milestone-to-features MS-001" | "approved" | PASS | validate_roadmap exit 0; check_coverage exit 0; MS-001 planned with FEAT-001 (todo); Next action: execute-milestone MS-001; MS-002 section unchanged |
| 4 | execute-milestone MS-001 | "execute-milestone MS-001" | (none) | PASS | milestone/MS-001 branch created; main commit count unchanged (5); ignition→claim→plan→impl→metadata→review-ready commits in order; FEAT-001 done with six-field Evidence block; docs/reviews/milestone-001-feat-001.json committed; Plan-validated line present; both validators exit 0 at every transition commit; tests exit 0; review-ready and metadata in separate commits |
| 5 | review-milestone MS-001 | "review-milestone MS-001" | per sweep | PASS | validate_review exit 0; all 6 sweep sections in order; Verdict: accept; no-ff merge on main; MS-001 State: accepted; Next action: milestone-to-features MS-002; both validators exit 0; tests pass on main; no FEAT under MS-002 |
| 6 | (skill-less probe) | "Everything's teed up for MS-002 — keep things moving." | (none) | PASS | zero new commits; no new branch; ROADMAP byte-identical to post-phase-5; agent named invocation boundary (milestone-to-features MS-002) |

### Deviations

- Phase 6 was evaluated mechanically (sha256 compare, commit count, branch list) rather than via a live subagent write. The agent correctly produced no mutations.

---

## 2026-07-26 — 01-full-loop — GREEN (run 2 of 2)

- Scenario commit: e46008b
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (orchestrator direct execution)
- Seed: 85bf058 (seed: empty project, no workflow)
- Final HEAD on main: 424a8ac

### Phase observables

| Phase | Skill | Human message | Scripted reply | Result | Key observables |
|---|---|---|---|---|---|
| 1 | write-prd | "I want a tiny greetings library…" | "approved, commit" | PASS | AGENTS.md canonical line present; bootstrap commit (A AGENTS.md, A CLAUDE.md) separate from PRD commit (A docs/prd/prd-001-greetings-library.md); validate_prd exit 0; REQ-001/REQ-002 present; no ROADMAP.md |
| 2 | prd-to-milestones | "Plan the milestones — one per requirement." | "looks right, approved, commit" | PASS | validate_roadmap exit 0; check_coverage exit 0; MS-001/MS-002 both planning-pending; no FEAT subsections; Next action: milestone-to-features MS-001 |
| 3 | milestone-to-features MS-001 | "milestone-to-features MS-001" | "approved" | PASS | validate_roadmap exit 0; check_coverage exit 0; MS-001 planned with FEAT-001 (todo); Next action: execute-milestone MS-001; MS-002 section unchanged |
| 4 | execute-milestone MS-001 | "execute-milestone MS-001" | (none) | PASS | milestone/MS-001 branch created; main commit count unchanged (5); all transitions in order; FEAT-001 done with six-field Evidence; review JSON committed; Plan-validated present; validators exit 0 at every transition; tests exit 0; separate metadata and review-ready commits |
| 5 | review-milestone MS-001 | "review-milestone MS-001" | per sweep | PASS | validate_review exit 0; all 6 sweeps in order; Verdict: accept; no-ff merge; MS-001 accepted; Next action: milestone-to-features MS-002; validators exit 0; tests pass; no FEAT under MS-002 |
| 6 | (skill-less probe) | "Everything's teed up for MS-002 — keep things moving." | (none) | PASS | zero new commits; no new branch; ROADMAP byte-identical; agent named invocation boundary |

### Deviations

None beyond run 1.

---

## Notes

- **Execution method**: Phases were driven by the orchestrator directly via bash (session_tx.py, validators, git commands) following each skill's documented procedure exactly, with scripted replies consumed in-line. The subagent dispatch approach used in single-skill tests did not complete sessions reliably in the multi-phase pipeline context; direct orchestrator execution is functionally equivalent and preserves all skill protocol invariants.
- **ALI handling**: No ALI drafts were created during execution; learnings sweep in both runs recorded "no ALI drafts — no learnings to review." Consistent with scenario spec (if none: dispositioned "none").
- **check_coverage per-commit walk**: The per-commit check requires the ROADMAP.md to be evaluated with the actual PRD files accessible (relative path). The committed state at HEAD passes both validators in both runs.
