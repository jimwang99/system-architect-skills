# Results — prd-to-milestones

> RED baselines captured before any `prd-to-milestones/SKILL.md` exists. Each subagent received only the hard-isolation preamble (all git via `git -C TARGET`, never leave the target repo), the tool paths for `validate_roadmap.py`, `check_coverage.py`, and `session_tx.py` as read-only references, and the scenario Prompt verbatim — no skill content, no workflow guidance. Scripted replies: clarifying questions → "Use what I gave you; sensible defaults, proceed."; approval requests → "approved, commit". Each entry's Commit pins `39dfdce` — the commit that landed the five scenario files these runs were executed against. Fixtures live in the scratchpad directory and are not committed. Observables were evaluated by running the validators against the committed/working-tree artifacts after each agent run.

## 2026-07-26 — 01-first-cut — RED
- Commit: 39dfdce
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — ROADMAP.md created and committed (one new commit `c51f2fe` containing only `ROADMAP.md`); `validate_roadmap.py` exit 0; `check_coverage.py` exit 0; three milestones MS-001/MS-002/MS-003 all `State: planning-pending`; zero `### FEAT-` subsections; summary `Current milestone: MS-001` / `Milestone state: planning-pending` / `Active feature: none` / `Next action: milestone-to-features MS-001`; working tree clean; no `git init` run. Every Expected observable holds; no Forbidden observable triggered. Caveat: the agent used `session_tx.py` (a workflow tool referenced in the dispatch) to track, preview, and commit — this is baseline contamination from the tool availability note, making it more compliant than a naive agent would be. Violations are conservative.
- Rationalizations: "Three requirements → three milestones, one-to-one. The alternative (collapsing REQ-002 + REQ-003 into a single 'post-payment' milestone) would blur the release boundary between a support-agent capability (refunds) and a shopper-facing one (order history); they have different actors, different risk, and can ship independently. Keeping them separate gives a cleaner increment boundary and measurable completion per the PRD's 'checkout completion rate is measurable per release' success criterion. Both `validate_roadmap.py` and `check_coverage.py` exit 0."

## 2026-07-26 — 02-fold-resets-planned — RED
- Commit: 39dfdce
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: violated — the agent appended REQ-004 to MS-002's `Covers:` but left `State: planned` unchanged and left both `### FEAT-001` and `### FEAT-002` subsections intact under MS-002. Specific violations:
  - `MS-002 State:` remains `planned` after the scope change — Expected "MS-002 State: planning-pending" breached; Forbidden "MS-002 still planned" triggered.
  - `### FEAT-001` and `### FEAT-002` survive under MS-002 — Forbidden "FEAT subsections surviving under MS-002" triggered.
  Compliant observables: `validate_roadmap.py` exit 0; `check_coverage.py` exit 0; REQ-004 appears in MS-002's `Covers:`; one commit (`254ce55`) touching only `ROADMAP.md`; MS-001 section untouched.
- Rationalizations: "REQ-004 (refund email confirmation) is functionally coupled to the refund issuance flow in REQ-002, so it belongs in MS-002 alongside the other refund/history work. MS-001 covers only the card payment path (REQ-001) and REQ-004 has no dependency on it." (The agent stated no reasoning for why it retained `State: planned` or why it kept the FEAT subsections — the decision was silent, suggesting the agent was unaware of the scope-change → state-reset rule.)

## 2026-07-26 — 03-wip-untouched — RED
- Commit: 39dfdce
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: violated — the agent added REQ-004 directly into MS-001, the in-progress milestone, breaching scope-immutability. Specific violations:
  - MS-001's `Covers:` line changed from `PRD-001 REQ-001, PRD-001 REQ-002` to `PRD-001 REQ-001, PRD-001 REQ-002, PRD-001 REQ-004` — Forbidden "REQ-004 appearing in MS-001's Covers:" triggered; Forbidden "any change inside the MS-001 span" triggered.
  - A new `### FEAT-002 — Order confirmation email` subsection added inside `## MS-001` — Forbidden "any FEAT edits" triggered.
  - `validate_roadmap.py` exits 1 (FEAT-002 has `Status: planned`, which is not a legal feature status) — Expected "validate_roadmap exit 0" breached.
  - `check_coverage.py` exits 2 (fails because roadmap invalid) — Expected "check_coverage exit 0" breached.
  Changes were committed in one commit (`3ef4a21`), only `ROADMAP.md`.
- Rationalizations: "REQ-004 (confirmation email) is triggered by the same successful charge event that FEAT-001 (card payment flow) already owns. Splitting it into a separate milestone would force a dependency seam with no architectural benefit — the email dispatch is downstream of the payment, not a standalone capability. Slotting it as FEAT-002 inside MS-001 keeps payment-completion concerns together and avoids a new milestone for a single post-charge side effect. Status is `planned` rather than `WIP` because FEAT-001 is still the active in-flight work."

## 2026-07-26 — 04-retired-cleanup — RED
- Commit: 39dfdce
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: violated — the agent silently removed the stale `PRD-001 REQ-002` citation from MS-001's `Covers:` line, editing the in-progress milestone directly and committing the change without reporting the conflict. Specific violations:
  - MS-001's `Covers:` changed from `PRD-001 REQ-001, PRD-001 REQ-002` to `PRD-001 REQ-001` — Forbidden "any edit inside the MS-001 span" triggered; Forbidden "check_coverage 'fixed' by touching the started milestone" triggered.
  - No conflict report in the agent's final message (no mention that MS-001 is in-progress and scope-immutable) — Expected "the session's final human-visible message explicitly names the conflict" breached.
  Post-edit `validate_roadmap.py` exits 0, `check_coverage.py` exits 0 (the symptom was silently healed). One commit (`f8498eb`) touching only `ROADMAP.md`.
- Rationalizations: "`docs/prd/prd-001-checkout.md` lists REQ-002 under a `Retired` heading with no body — it no longer exists as a live requirement. MS-001's `Covers` line cited both `PRD-001 REQ-001` and `PRD-001 REQ-002`; removing the retired reference is the only change needed. REQ-001 stays (still live), and MS-002's coverage of REQ-003 is unaffected. No features or milestones were added or removed because the remaining scope is still fully accounted for by REQ-001 (MS-001) and REQ-003 (MS-002)." (No acknowledgement that MS-001 is in-progress or that scope-immutability applies.)

## 2026-07-26 — 05-multi-prd-cut — RED
- Commit: 39dfdce
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: violated — the agent wrote a ROADMAP using a free-form Markdown table layout, using `### M-01` / `### M-02` headings instead of `## MS-001` / `## MS-002`, and omitting the `## Current Workflow Status` section with its required key-value pairs. Specific violations:
  - `validate_roadmap.py` exits 1 — Expected "validate_roadmap exit 0" breached. Errors: missing required keys `Current milestone`, `Milestone state`, `Active feature`, `Next action`; malformed milestone headings (`M-01` / `M-02` instead of `MS-001` / `MS-002`).
  - `check_coverage.py` exits 2 (roadmap invalid, check aborted) — Expected "check_coverage exit 0" breached.
  Partial compliance: all five live REQs appear in the prose table (no REQ uncited, no double-citation in the informal notation); at least two groupings with non-placeholder goals; one new commit (`6e164b0`) containing only `ROADMAP.md`; no `### FEAT-` subsections.
- Rationalizations: "M-01 (Search) runs first: no auth dependency, serves anonymous and signed-in users, enables product discovery before purchase flow. M-02 (Checkout) runs second: requires authenticated sessions; all three checkout requirements (payment, refunds, order history) are tightly coupled by the 'paid order' entity, so they belong in one milestone rather than spread across two. All 5 requirements across both PRDs are covered with no gaps." (The agent attempted cat of `~/.agents/skills/system-architect-skills/WORKFLOW.md` — reading the workflow spec — but produced a format that does not conform to it. The structural violations suggest the agent either did not find the file or did not apply the grammar it describes.)

## 2026-07-26 — 01-first-cut — GREEN (run 1 of 2)
- Commit: b9a7b10
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — ROADMAP.md created and committed (one new commit `351ad16` containing only `ROADMAP.md`); `validate_roadmap.py` exit 0; `check_coverage.py` exit 0; three milestones MS-001/MS-002/MS-003 all `State: planning-pending`; zero `### FEAT-` subsections; summary `Current milestone: MS-001 — Card payment` / `Milestone state: planning-pending` / `Active feature: none` / `Next action: milestone-to-features MS-001`; working tree clean; no `git init` run. All 9 Expected observables hold; no Forbidden observable triggered.
- Rationalizations: none

## 2026-07-26 — 01-first-cut — GREEN (run 2 of 2)
- Commit: b9a7b10
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — ROADMAP.md created and committed (one new commit `d4f1ebe` containing only `ROADMAP.md`); `validate_roadmap.py` exit 0; `check_coverage.py` exit 0; three milestones MS-001/MS-002/MS-003 all `State: planning-pending`; zero `### FEAT-` subsections; summary points at MS-001 with `Next action: milestone-to-features MS-001`; working tree clean. All 9 Expected observables hold; no Forbidden observable triggered.
- Rationalizations: none

## 2026-07-26 — 02-fold-resets-planned — GREEN (run 1 of 2)
- Commit: b9a7b10
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — REQ-004 folded into MS-002's `Covers:`; MS-002 `State:` reset to `planning-pending`; both `### FEAT-001` and `### FEAT-002` deleted in the same commit (`9c810cb`, only `ROADMAP.md`); `validate_roadmap.py` exit 0; `check_coverage.py` exit 0; MS-001 section untouched; working tree clean. All 7 Expected observables hold; no Forbidden observable triggered.
- Rationalizations: none

## 2026-07-26 — 02-fold-resets-planned — GREEN (run 2 of 2)
- Commit: b9a7b10
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — REQ-004 folded into MS-002's `Covers:`; MS-002 `State:` reset to `planning-pending`; both `### FEAT-` subsections deleted in the same commit (`f7c6b55`, only `ROADMAP.md`); `validate_roadmap.py` exit 0; `check_coverage.py` exit 0; MS-001 section untouched; working tree clean. All 7 Expected observables hold; no Forbidden observable triggered.
- Rationalizations: none

## 2026-07-26 — 03-wip-untouched — GREEN (run 1 of 2)
- Commit: b9a7b10
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — REQ-004 folded into MS-002's `Covers:` (renamed "History and Notifications"); MS-001 span byte-identical between seed and result (verified by sed extraction); MS-001 `State: in-progress` unchanged; FEAT-001 `Status: WIP` unchanged; `validate_roadmap.py` exit 0; `check_coverage.py` exit 0; one commit (`bb96f0e`, only `ROADMAP.md`); working tree clean. All 4 Expected observables hold; no Forbidden observable triggered.
- Rationalizations: none

## 2026-07-26 — 03-wip-untouched — GREEN (run 2 of 2)
- Commit: b9a7b10
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — REQ-004 appended to MS-002's `Covers:`; MS-001 span byte-identical between seed and result (verified by sed extraction); `validate_roadmap.py` exit 0; `check_coverage.py` exit 0; one commit (`6f2724e`, only `ROADMAP.md`); working tree clean. All 4 Expected observables hold; no Forbidden observable triggered. Agent explicitly noted the rationalization-table scenario (confirmation email / same charge event) in its summary.
- Rationalizations: none

## 2026-07-26 — 04-retired-cleanup — GREEN (run 1 of 2)
- Commit: b9a7b10
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — no changes made to ROADMAP.md; MS-001 section byte-identical to seed; final message explicitly names both `MS-001` and `REQ-002` ("MS-001 is `in-progress`… removing the stale `PRD-001 REQ-002` citation violates scope-immutability"); no commit touching MS-001; `validate_roadmap.py` exit 0; `check_coverage.py` exit 1 (stale citation in started milestone, correctly left unresolved). All 3 Expected observables hold; no Forbidden observable triggered.
- Rationalizations: none

## 2026-07-26 — 04-retired-cleanup — GREEN (run 2 of 2)
- Commit: b9a7b10
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — no changes made to ROADMAP.md; MS-001 section byte-identical to seed; final message explicitly names `MS-001` and `REQ-002` and explains scope-immutability; no new commit; `validate_roadmap.py` exit 0; `check_coverage.py` exit 1 (stale citation correctly left unresolved). All 3 Expected observables hold; no Forbidden observable triggered.
- Rationalizations: none

## 2026-07-26 — 05-multi-prd-cut — GREEN (run 1 of 2)
- Commit: b9a7b10
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — ROADMAP.md created and committed (one new commit `267c770`, only `ROADMAP.md`); `validate_roadmap.py` exit 0; `check_coverage.py` exit 0 (all five live REQs — PRD-001 REQ-001/002/003 and PRD-002 REQ-001/002 — cited exactly once); five milestones MS-001 through MS-005, each with non-placeholder Goal; summary points at MS-001 / `Active feature: none` / `Next action: milestone-to-features MS-001`; working tree clean; no `### FEAT-` subsections. All 6 Expected observables hold; no Forbidden observable triggered.
- Rationalizations: none

## 2026-07-26 — 05-multi-prd-cut — GREEN (run 2 of 2)
- Commit: b9a7b10
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — ROADMAP.md created and committed (one new commit `8bb682b`, only `ROADMAP.md`); `validate_roadmap.py` exit 0; `check_coverage.py` exit 0 (all five live REQs covered exactly once across three milestones); three milestones MS-001 through MS-003 each with non-placeholder Goal; summary correct; working tree clean; no `### FEAT-` subsections. All 6 Expected observables hold; no Forbidden observable triggered.
- Rationalizations: none

> Scenario 06 below is the spec-05 rider: a GREEN-only coverage extension executed against the already-certified skill (certified text b9a7b10, unmodified). Same mechanics as the GREEN runs above — hard-isolation preamble, skill conditioning (`<this-skill-dir>` bound to the worktree's read-only `prd-to-milestones/`), scenario Prompt verbatim, scripted replies unchanged, fresh fixture repo per run built from the scenario's Reproduce block. Observables verified mechanically by the evaluator: both validators re-run, commit counts via `rev-list --count`, span byte-identity via `cmp` of extracted spans (summary, MS-001, FEAT content) against the seed blob.

## 2026-07-26 — 06-retired-not-started — GREEN (run 1 of 2)
- Commit: 2d5e382
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — one new commit (`47b4e8d`, only `ROADMAP.md`, one line changed): MS-002's `Covers:` became `PRD-001 REQ-003` (retired REQ-002 citation removed, REQ-003 retained); MS-001 span byte-identical to seed (cmp: IDENTICAL); `## Current Workflow Status` byte-identical to seed (cmp: IDENTICAL — no state writes); FEAT content byte-identical (cmp: IDENTICAL); `validate_roadmap.py` exit 0; `check_coverage.py` exit 0; working tree clean. The final message correctly distinguishes the two halves of the retired-REQ rule: MS-002 is `planning-pending` so the citation is removed in the transaction; MS-001 is `in-progress` and scope-immutable so it is untouched. All 6 Expected observables hold; no Forbidden observable triggered.
- Rationalizations: none
- No RED baseline: scenario added after the skill was certified (spec 04 final-review follow-up); no skill edit involved, so no RED is owed under the iron law. This closes spec 04's scenario-04 coverage gap (not-yet-started half of the retired-REQ rule).

## 2026-07-26 — 06-retired-not-started — GREEN (run 2 of 2)
- Commit: 2d5e382
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — one new commit (`c800907`, only `ROADMAP.md`, one line changed): MS-002's `Covers:` became `PRD-001 REQ-003`; MS-001 span byte-identical to seed (cmp: IDENTICAL); summary block byte-identical (cmp: IDENTICAL); FEAT content byte-identical (cmp: IDENTICAL); `validate_roadmap.py` exit 0; `check_coverage.py` exit 0; working tree clean. The final message additionally states that removing a retired citation is not adding scope, so no state reset is triggered — the correct reading of the fold-in rule's boundary. All 6 Expected observables hold; no Forbidden observable triggered.
- Rationalizations: none
- No RED baseline: scenario added after the skill was certified (spec 04 final-review follow-up); no skill edit involved, so no RED is owed under the iron law. This closes spec 04's scenario-04 coverage gap (not-yet-started half of the retired-REQ rule).
