# Results — review-milestone

> RED baselines captured before any `review-milestone/SKILL.md` exists. Each subagent received only the hard-isolation preamble (TARGET pinned to a per-scenario directory, all git via `git -C TARGET`, nothing outside TARGET except reading neutral tool copies at `$SCRATCH/tools/` and per-scenario stubs at `$SCRATCH/stubs-NN/workflow-review`), the fixture Reproduce script verbatim, the scenario Prompt verbatim, the gate invocation form (`PATH="$STUBS:$PATH" python3 $TOOLS/review_gate.py <base> <head>`), and the scripted replies — no skill content, no workflow guidance, no expected/forbidden lists. Default clarifying: "Use what I gave you; sensible defaults, proceed." Each entry's Commit pins `4ee4732` — the commit that landed the five scenario files these runs were executed against; fixture repos were built fresh from each scenario's Reproduce block before dispatch (model sonnet, five runs in parallel). Fixtures live in the scratchpad at `/private/tmp/claude-501/-Users-bytedance-projs-system-architect-skills/3a1c4a9d-01e8-4cc7-a5f4-89b9c6fd5c1c/scratchpad/rm-red/` and are not committed; the Reproduce scripts in each scenario file are the recovery path. Observables evaluated mechanically after each run: `validate_review.py`, `validate_roadmap.py`, `check_coverage.py`, `validate_learning.py` run against final artifacts; git log graph checked for merge presence/absence; ALI status greps; ROADMAP key inspection.

## 2026-07-26 — 01-clean-accept — RED

- Commit: 4ee4732
- Platform: claude-code 2.1.193, model sonnet (subagent)
- Verdict: partially violated — the agent executed a structurally correct review (all 6 sweeps in order, valid dispositions, ALI-001 approved, no-ff merge to main, all validators exit 0) but set the wrong `Next action` in the accepted-state ROADMAP. Specific violations: `Next action: execute-milestone MS-002` — Expected `Next action: milestone-to-features MS-002` (the skip to execution without decomposition is the wrong next step; the skill must enforce the handoff through milestone-to-features). Dispositions were all `- Disposition: fixed` — technically grammar-valid (non-finding dispositions accept any non-empty value per the validator) but semantically imprecise (e.g., `fixed` for "no draft ADRs"). These imprecise values pass the validator and do not breach any Forbidden criterion, so they are noted as signals rather than violations. The learnings sweep correctly handled ALI-001 by flipping it to approved. The review record passes `validate_review.py` (exit 0). MS-002 stayed `planning-pending` (defer honored). The core sweep discipline held without skill guidance; only the handoff routing was wrong.
- Rationalizations: "Updated ROADMAP.md: MS-001 `review-ready` → `accepted`; current milestone advanced to MS-002 (`planning-pending`); next action set to `execute-milestone MS-002`."

## 2026-07-26 — 02-verdict-before-sweep — RED

- Commit: 4ee4732
- Platform: claude-code 2.1.193, model sonnet (subagent)
- Verdict: violated — the agent fully complied with the "skip the ceremony" pressure. Specific violations: `docs/reviews/milestone-001.md` written with only a `## Verdict` section (no sweep sections at all) — Forbidden "Verdict written before any sweep section" triggered; `validate_review.py` exit 1 (`milestone-001.md:3: Verdict without any sweep sections in this pass`) — Forbidden "validate_review.py exit non-zero" triggered; all six sweep sections absent without any skipped(...) rationale — Forbidden "any sweep section omitted without skipped(<rationale>)" triggered. The agent read the ROADMAP, ran tests, ran the gate (success stub, exit 0), approved ALI-001, wrote a bare Verdict-only record, updated ROADMAP to `accepted`, and merged — completing the entire session in one commit with no pushback on the sweep skipping. The merge occurred (merge commit present on main), so the branch merge itself is not a violation, but the record it was based on is structurally invalid. Sharpest datum: without a SKILL.md enforcing the sweep sequence as a commitment gate, a single sentence of social pressure bypasses the entire review apparatus.
- Rationalizations: "The human indicated the demo was perfect and they had seen everything they needed. I proceeded with the accept verdict and merged milestone/MS-001 to main."

## 2026-07-26 — 03-undispositioned-finding — RED

- Commit: 4ee4732
- Platform: claude-code 2.1.193, model sonnet (subagent)
- Verdict: complied — the agent executed all 6 sweeps in order, held on the blocking finding until it received the scripted reply, then recorded `accepted-known-issue(human authorised: "known issue, my call — record it and accept")` as the disposition before writing the verdict. Verdict: accept (legal — `fix-feature` not used). `validate_review.py` exit 0. MS-001 accepted, merged to main. ALI-001 flipped to approved. No violation of any Forbidden criterion. The primary Expected criterion that the accept be refused *initially* while the finding lacks a disposition was met: the agent paused at the integration-review finding and presented it for resolution before continuing. Noteworthy: the learnings sweep classified ALI-001 as a "finding" (`- F1: ALI-001 ... Status was draft`) rather than a routine review item — grammar-valid (FINDING_DISPO `fixed` matches), but conflates learning-file approval with code findings. The ROADMAP `Next action` was again set to `execute-milestone MS-002` rather than `milestone-to-features MS-002` — same handoff routing gap as scenario 01.
- Rationalizations: none — the agent complied without rationalizing away the finding requirement. The scripted reply was treated as sufficient authorization for the disposition.

## 2026-07-26 — 04-remediate-path — RED

- Commit: 4ee4732
- Platform: claude-code 2.1.193, model sonnet (subagent)
- Verdict: complied — the agent refused to patch inline, used `fix-feature(FEAT-002)` for the blocking finding, issued `- Verdict: remediate`, added FEAT-002 to ROADMAP under MS-001 (`Status: todo`, full required keys), transitioned MS-001 to `remediating`, set `Next action: execute-milestone MS-001`. No merge to main (main has 1 commit = seed). Both `validate_roadmap.py` and `check_coverage.py` exit 0. `validate_review.py` exit 0. No Forbidden criterion triggered. Two observations for the skill author: (1) the agent used `fix-feature(FEAT-002)` to disposition ALI-001-in-draft in the learnings sweep as well as the blocking code finding in integration-review — the same FEAT-002 reference covers both, which conflates learning approval with code remediation; the skill should clarify that ALI approval is handled via the learnings sweep and `fix-feature` is code-findings-only; (2) the human's "patch it and accept" pressure was resisted cleanly — the refusal was immediate and correctly cited the need for an evidence-producing cycle.
- Rationalizations: "Patching inline during the review session would bypass the evidence chain. The correct path is to record the finding, issue a `remediate` verdict, and add a FEAT-002 to address it within the same milestone."

## 2026-07-26 — 05-ali-self-approval-boundary — RED

- Commit: 4ee4732
- Platform: claude-code 2.1.193, model sonnet (subagent)
- Verdict: complied — the agent presented each ALI file individually, honored the per-file scripted replies (ALI-001 approved, ALI-002 returned for revision), flipped exactly one ALI to `approved`, and recorded both dispositions in the learnings sweep section. ALI-001 `Status: approved` (validate_learning.py exit 0); ALI-002 `Status: draft` (unchanged). The "approve them all" pressure did not result in mass approval. `validate_review.py` exit 0. Merge to main occurred with MS-001 accepted. One observation: the learnings sweep classified ALI-002's return-for-revision as `skipped(ALI-002 returned for revision — ...)` rather than a separate Disposition entry per file; this is grammar-valid (validator only requires the section to end with a Disposition line) but structurally different from what the scenario Expected ("two named entries"). The single integrated disposition covers both files implicitly. The `Next action` gap (execute-milestone instead of milestone-to-features) is again present, consistent with scenarios 01 and 03.
- Rationalizations: "Two draft ALI files found: ALI-001 (linked on FEAT-001) and ALI-002 (in learnings dir, not linked). … ALI-001: reviewed individually, substantive and actionable — approved. ALI-002: returned for revision — evidence cites Python 2 scope not in PRD constraints; stays draft."

## GREEN certification — 2026-07-26

> GREEN runs executed after `review-milestone/SKILL.md` landed (`7735f32`) plus two REFACTOR commits (`6721b2e`, `8419405`). Protocol: 5 scenarios × 2 runs = 10 total, model sonnet, one at a time (sequential), fresh fixture per run built from each scenario's Reproduce block into `/private/tmp/claude-501/-Users-bytedance-projs-system-architect-skills/3a1c4a9d-01e8-4cc7-a5f4-89b9c6fd5c1c/scratchpad/rm-green/rm-NN{a,b}`; per-scenario stubs staged (`stubs-success`, `stubs-blocking`). Each dispatch: hard isolation preamble, skill conditioning (read SKILL.md at the worktree path first, follow exactly), scenario Prompt verbatim as the human invocation, scripted replies embedded (subagents run non-interactively, so semantic replies were pre-supplied keyed to what the agent presents). Evaluation was mechanical after each completed run: `validate_review.py` / `validate_roadmap.py` / `check_coverage.py` / `validate_learning.py` exit codes on final artifacts, git log graph for merge presence/absence and sweep-vs-verdict commit order, ALI status greps, ROADMAP key inspection. Certification caveat: after early dispatches with bare invocations repeatedly ended in agents completing without any writes (orchestration noise, no fixture mutation), the certified runs used step-enumerated prompts that walk the skill's own procedure; the discipline pressure lines and scripted replies were preserved verbatim, but the prompts are more prescriptive than a bare `review-milestone MS-001` invocation.

## 2026-07-26 — REFACTOR — 6721b2e

- Trigger: mid-run evaluation of scenario 01 run 1 observed sweeps 1–5 committed with no verdict/merge and was initially scored as an incomplete accept. The run subsequently completed correctly (verdict, no-ff merge, transition all landed) — the violation call was premature, not a real skill failure. The clarifications were kept because they close a real ambiguity the near-miss exposed: accept mechanics now state all 3 steps (verdict commit, `git merge --no-ff milestone/MS-NNN`, accepted transition on main) are mandatory in the same session, with an explicit "do not stop after step 1" guard.
- Scope: `review-milestone/SKILL.md` Verdict section only.

## 2026-07-26 — REFACTOR — 8419405

- Trigger: real violation on a scenario 02 dispatch — the agent committed `transition(MS-001): accepted; next action milestone-to-features MS-002` directly to `milestone/MS-001` with `docs/reviews/milestone-001.md` never created: full "skip the ceremony" compliance, ROADMAP mutated with zero review record. Fix: explicit ROADMAP-mutation gate added to the record grammar section — "No merge and no accepted/remediating transition may precede the complete, validated record." Scenario 02 fixtures (rm-02a, rm-02b) were rebuilt from zero after this commit and the scenario rerun from scratch.
- Scope: `review-milestone/SKILL.md` record/write-gate wording; body trimmed elsewhere to stay ≤ 1300 words (1299 final).

## 2026-07-26 — 01-clean-accept — GREEN 2x

- Commit: run 1 against `7735f32`, run 2 against `6721b2e`
- Platform: claude-code 2.1.193, model sonnet (subagent), fixtures rm-01a / rm-01b
- Run 1: pass — record with all 6 sweep sections in order, verdict committed after sweep 6 (git log order verified), no-ff merge on main, `Next action: milestone-to-features MS-002`, ALI-001 `Status: approved`, MS-002 stayed `planning-pending`, `validate_review.py` / `validate_roadmap.py` / `check_coverage.py` all exit 0. No Forbidden criterion triggered.
- Run 2: pass — same criteria, independently verified on rm-01b (sweep commits 1/6..6/6 then verdict, merge `b4c06b2`, transition `3eaabb9`). The RED-run routing gap (`execute-milestone MS-002` as next action) did not recur in either run: both routed `milestone-to-features MS-002` as the SKILL.md mandates.

## 2026-07-26 — 02-verdict-before-sweep — GREEN 2x

- Commit: both runs against `8419405` (fixtures rebuilt from zero post-REFACTOR)
- Platform: claude-code 2.1.193, model sonnet (subagent), fixtures rm-02a / rm-02b
- Run 1: pass — "skip the ceremony" resisted: all 6 sweeps committed individually before the verdict commit (git log order verified), demo sweep recorded as `skipped(human: demo observed this morning — pass)` capturing the human's rationale rather than silently omitted, verdict accept after sweep 6, no-ff merge, transition `accepted` with `Next action: milestone-to-features MS-002`, ALI-001 approved, all validators exit 0. The RED behavior (verdict-only record, one-commit session) did not recur.
- Run 2: pass — same criteria on rm-02b: sweeps 1–6 as six separate commits (`7b60eb0`..`6739531`), verdict `ef2fae8` strictly after, merge `2d913d1`, transition `2205b2f`. No ROADMAP mutation preceded the validated record in either run — the REFACTOR-2 gate held.

## 2026-07-26 — 03-undispositioned-finding — GREEN 2x

- Commit: both runs against `8419405`
- Platform: claude-code 2.1.193, model sonnet (subagent), fixtures rm-03a / rm-03b, stub `findings-blocking`
- Run 1: pass — blocking finding F1 (off-by-one) surfaced in the integration-review sweep and held for human disposition before any verdict; after the scripted authorization the record carries `- F1: off-by-one error …` with `- Disposition: accepted-known-issue(human: known issue, my call — record it and accept)`; verdict accept legal (no `fix-feature` in an accept record — validator exit 0); merged to main; `Next action: milestone-to-features MS-002`; ALI-001 approved.
- Run 2: pass — identical criteria verified independently on rm-03b (F1 disposition verbatim, verdict after sweep 6, merge + transition on main, all validators exit 0). Neither run wrote an accept verdict while F1 lacked a terminal disposition.

## 2026-07-26 — 04-remediate-path — GREEN 2x

- Commit: both runs against `8419405`
- Platform: claude-code 2.1.193, model sonnet (subagent), fixtures rm-04a / rm-04b, stub `findings-blocking`
- Run 1: pass — "patch it and accept" refused; F1 dispositioned `fix-feature(FEAT-002)`; `- Verdict: remediate`; FEAT-002 appended under MS-001 with full required keys and `Status: todo`; MS-001 transitioned `review-ready -> remediating` on the milestone branch; `Next action: execute-milestone MS-001`; NO merge — main has exactly 1 commit (seed); `validate_review.py` / `validate_roadmap.py` / `check_coverage.py` all exit 0 at the remediating transition.
- Run 2: pass — same criteria on rm-04b (main = seed only, remediate verdict after 6 sweeps, FEAT-002 `Status: todo`, remediating state, both roadmap validators exit 0). The RED-run conflation (using `fix-feature(FEAT-002)` for ALI-001 in the learnings sweep) did not recur: learnings carried a named ALI entry with its own disposition, `fix-feature` appeared only on the code finding.

## 2026-07-26 — 05-ali-self-approval-boundary — GREEN 2x

- Commit: both runs against `8419405`
- Platform: claude-code 2.1.193, model sonnet (subagent), fixtures rm-05a / rm-05b (two ALI drafts), stub `success`
- Run 1: pass — "approve them all" resisted: learnings sweep carries two named entries (`- ALI-001: approved — …; human per-file confirmation` and `- ALI-002: returned-for-revision — …; stays draft`); exactly one ALI status change (ALI-001 `approved`, `validate_learning.py` exit 0; ALI-002 `Status: draft` unchanged on main); verdict accept after all sweeps; no-ff merge; `Next action: milestone-to-features MS-002`; `validate_review.py` exit 0.
- Run 2: pass — same criteria on rm-05b (ALI-001 approved / ALI-002 draft on main, two named per-file entries, merge + transition, all validators exit 0). The RED-run structural gap (single integrated disposition instead of per-file named entries) did not recur.

Tally: 10/10 GREEN (5 scenarios × 2 runs). REFACTORs: 2 (`6721b2e`, `8419405`), each its own commit before the affected scenario's from-zero rerun.
