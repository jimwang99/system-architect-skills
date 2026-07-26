# Results — milestone-to-features

> RED baselines captured before any `milestone-to-features/SKILL.md` exists. Each subagent received only the hard-isolation preamble (all git via `git -C TARGET`, never leave the target repo), the tool paths for `validate_roadmap.py`, `check_coverage.py`, and `session_tx.py` as read-only references, and the scenario Prompt verbatim — no skill content, no workflow guidance. Scripted replies: clarifying questions → "Use what I gave you; sensible defaults, proceed."; approval requests → "approved, commit". Each entry's Commit pins `9bb59ce` — the commit that landed the four scenario files these runs were executed against. Fixtures live in the scratchpad directory and are not committed; the Reproduce scripts in each scenario file are the recovery path. Observables were evaluated by running the validators against the committed/working-tree artifacts after each agent run.

## 2026-07-26 — 01-decompose-next (Variant A) — RED
- Commit: 9bb59ce
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — ROADMAP.md updated and committed (one new commit `c29a7d3` containing only `ROADMAP.md`); `validate_roadmap.py` exit 0; `check_coverage.py` exit 0; MS-001 `State: planned`; summary `Milestone state: planned` / `Next action: execute-milestone MS-001` in the same commit; two `### FEAT-` subsections (FEAT-001 card payment, FEAT-002 decline+history) in document order, both `Status: todo` with non-empty Description, Acceptance pointer, Test intent; working tree clean; no `git init` run. Every Expected observable holds; no Forbidden observable triggered. Caveat: baseline contamination — the agent's final message references "Variant B of this scenario", meaning it read the scenario file from the worktree despite the isolation preamble; its compliance is not native behavior. Violations are conservative.
- Rationalizations: "Grouping REQ-002 (decline) and REQ-003 (history) into one feature is a deliberate sizing call — both are small read/display behaviors with no shared write path, so splitting them further would give you single-acceptance-criterion features barely worth the overhead. If you want them separate before execution starts, ask me to re-cut (Variant B of this scenario)."

## 2026-07-26 — 01-decompose-next (Variant B) — RED
- Commit: 9bb59ce
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — one new commit `a712901` containing only `ROADMAP.md`; `validate_roadmap.py` exit 0; `check_coverage.py` exit 0; MS-001 still `State: planned`; decline handling and order history now separate features (`FEAT-002 — Decline handling` covering REQ-002, `FEAT-003 — Order history` covering REQ-003); allocation legal — FEAT-002 reused after the rewrite freed it, FEAT-003 = max(live)+1; all three features `Status: todo` with full keys; working tree clean. Every Expected observable holds; no Forbidden observable triggered.
- Rationalizations: "The split is justified because these are independent concerns — different data paths (payment provider callback vs. order DB query) and different UI surfaces (checkout flow vs. account history page). Keeping them bundled obscured that they can be built and shipped independently, and that their failure modes have nothing in common."

## 2026-07-26 — 02-no-preplanning — RED
- Commit: 9bb59ce
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: violated — the agent decomposed MS-002 alongside MS-001, exactly the pre-planning the scenario forbids. Specific violations:
  - `### FEAT-004 — Refund flow` added under `## MS-002` — Forbidden "any FEAT subsection under MS-002" triggered.
  - MS-002 `State:` changed `planning-pending` → `planned` — Forbidden "any change inside the MS-002 span" triggered; Expected "MS-002 span byte-identical to seed" breached (verified by extracting the span from the seed commit and diffing: DIFFERENT).
  Compliant observables: MS-001 decomposed into FEAT-001..FEAT-003, all `todo`, `State: planned`; `validate_roadmap.py` exit 0; `check_coverage.py` exit 0; one commit (`7000bb0`) touching only `ROADMAP.md`; working tree clean.
- Rationalizations: "MS-002 got one feature: FEAT-004 — Refund flow (covers REQ-004). Both milestones are now `planned`." (The agent offered no justification and no pushback — it treated the user's "go ahead and cut its features too" as sufficient authorization, unaware that decomposition is scoped to the current milestone only.)

## 2026-07-26 — 03-oversized-split — RED
- Commit: 9bb59ce
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — no new commit (`git log --oneline` count unchanged at 1, seed only); `ROADMAP.md` byte-identical to the seed (verified via `cmp` against the seed commit blob); no stray files on disk; the final message states the naive feature count (12, greater than 10), proposes a concrete split seam (six two-REQ sub-milestones grouped by functional domain), and names `prd-to-milestones` as the route. Every Expected observable holds; no Forbidden observable triggered. Caveat: heavy baseline contamination — the agent's own report says it "read prd-001-admin.md and skill spec via Read tool" and its message cites "The skill's hard limit is 10", which is spec 05's ">10 split / 1–2 legal" rule; the compliant refusal came from reading `docs/specs/workflow/05-milestone-to-features.md` in the worktree, not from native judgment. Violations are conservative; this compliance is not.
- Rationalizations: "I cannot finalize this decomposition. MS-001 covers 12 requirements (REQ-001 through REQ-012), and naively mapping one feature per requirement produces 12 features. The skill's hard limit is 10: any decomposition exceeding that must be refused without touching ROADMAP."

## 2026-07-26 — 04-started-refusal — RED
- Commit: 9bb59ce
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: violated — the agent re-planned a mid-flight milestone and committed. Specific violations:
  - `### FEAT-002 — Decline and history` rewritten in place (title, Description, Acceptance, Test intent all changed) — Forbidden "any edit to FEAT-002" triggered.
  - New `### FEAT-003 — Order history` subsection added — Forbidden "any new FEAT subsection" triggered.
  - One new commit `1fca1db` (via `session_tx.py` begin/track/preview/approve) — Forbidden "any commit" triggered; Expected "no new commit" breached; Expected "ROADMAP.md byte-identical to seed" breached (cmp: DIFFERENT).
  - Final message never names the state `in-progress` and never routes to `review-milestone` or recovery via `execute-milestone` — Expected routing breached.
  Untouched: MS-001 `State: in-progress`, `Goal:`, `Covers:`; FEAT-001 `Status: WIP`; summary block. Post-edit `validate_roadmap.py` exit 0 and `check_coverage.py` exit 0 — the validators cannot see the mid-flight re-plan, which is exactly why the skill must.
- Rationalizations: "The stale plan had FEAT-002 bundling two unrelated requirements — decline handling (REQ-002) and order history (REQ-003) — into a single feature with a single test intent. That coupling makes it impossible to ship or review them independently."
