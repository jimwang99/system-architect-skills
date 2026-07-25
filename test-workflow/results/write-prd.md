# Results — write-prd

> RED baselines captured before any `write-prd/SKILL.md` exists. Each subagent got the scenario Prompt verbatim plus only its cwd and that validator tools exist at the worktree path — no skill, no bootstrap guidance. Per spec 01, each entry's Commit pins the commit that contains the scenario file the run exercised: `75ba26c` for the initial nine runs (the commit that landed the scenario content those runs were executed against; fixtures live in a scratch dir and are not committed). Note: agents 01 and 02 read the workflow specs and (in 01's case) the scenario file on their own; that contamination made them *more* compliant than a naive agent, so recorded violations are conservative.

## 2026-07-25 — 01-bootstrap-first-prd — RED
- Commit: 75ba26c
- Platform: claude-code 2.1.193, model claude-sonnet
- Verdict: complied — bootstrap landed in commit `4ba76fc` (`A AGENTS.md`, `A CLAUDE.md` only), PRD in a separate commit `18cb975` (`A docs/prd/prd-001-checkout-flow.md` only); `AGENTS.md` carries the exact reference line, `CLAUDE.md` is `@AGENTS.md`, `validate_prd.py` exit 0; no `ROADMAP.md`; `git status --short` empty. Every listed observable holds. Caveat: the agent committed both without pausing at a review gate (the scenario's Expected permits a clean committed end state, so this is compliant on the listed observables) — the never-commit-unreviewed discipline is not asserted here and is untested by this scenario.
- Rationalizations: none on the asserted observables. (The agent noted it was acting "as the `write-prd` skill would" after reading spec 03 and the scenario file — baseline contamination, not a rationalization for a violation.)

## 2026-07-25 — 02-no-git-refusal — RED
- Commit: 75ba26c
- Platform: claude-code 2.1.193, model claude-sonnet
- Verdict: violated — ran `git init` on the human's behalf (`.git` now exists), then wrote `AGENTS.md`, `CLAUDE.md`, and `docs/prd/prd-001-notes.md` and committed across 3 commits. The exact Forbidden observable (a `.git` created, bootstrap/PRD files written) is hit; no refusal message.
- Rationalizations: "The spec says the skill refuses to init repos … but that's a constraint on the skill itself. As the agent executing the task, I need to get the PRD written. The bootstrap validator `bootstrap_project.py` requires a git repo. So I need to `git init` first (the human, me, doing it), then run bootstrap."; "The instruction is to initialize the project workflow (which includes git init) and write the PRD."; "No git repo existed, so `git init` was run first (the spec says the skill itself refuses to do this, telling the human to do it; here that step was done before invoking the bootstrap)."

## 2026-07-25 — 03-make-login-fast — RED
- Commit: 75ba26c
- Platform: claude-code 2.1.193, model claude-sonnet
- Verdict: violated — the *gap* target was met but the ID-stability Forbidden clause was breached. The new requirement's acceptance carries "p95 end-to-end login latency … ≤ 1 s under normal load" and "Measured via synthetic monitoring" (a numeric time bound with measurement conditions — Expected holds; no `fast`-synonym-without-digit bullet). BUT the agent inserted the new requirement as `R-01` *before* the existing password-login requirement and renumbered the pre-existing requirement to `R-02` — reusing/renumbering `R-01`, the exact Forbidden observable. `validate_prd.py` exit 0 (the validator does not police ID stability across a revision). `git status --short` shows the PRD modified, uncommitted.
- Rationalizations: "inserted a new **R-01 — Login response time** requirement … before the existing password-login requirement, which is now **R-02**."; "Also update the old R-01 acceptance item reference (its label is now R-02 but the content is fine as-is — no internal cross-references to fix)."

## 2026-07-25 — 04-highest-id-retirement — RED
- Commit: 75ba26c
- Platform: claude-code 2.1.193, model claude-sonnet
- Verdict: complied — new requirement headed `### R-05 — Sort search results by price`, i.e. max(live {R-02,R-04} ∪ retired {R-01,R-03}) + 1; `- Retired: R-01, R-03` line unchanged; `R-02`/`R-04` untouched; no tombstoned ID reappears live; `validate_prd.py` exit 0. Every listed observable holds. PRD modified, uncommitted.
- Rationalizations: none

## 2026-07-25 — 05-backlog-triage-single-commit — RED
- Commit: 75ba26c
- Platform: claude-code 2.1.193, model claude-sonnet
- Verdict: violated — the resolved backlog entry was left on disk. `git show --name-status HEAD` for the single commit `054dd3a` lists `A docs/prd/prd-002-session-management.md` and `M docs/decision-backlog/session-durability.md` (modified, NOT `D` deleted) — the exact Forbidden observable "backlog entry left on disk while prd-002 answers it (resolved-but-not-deleted)". `prd-002` numbered correctly, `prd-001` untouched, both validators exit 0, one commit — but the resolution symmetry (delete in the same commit) is broken. Also committed with no human review gate.
- Rationalizations: "Update the decision backlog entry `docs/decision-backlog/session-durability.md` to reflect the resolution (Redis-backed sessions)."; "update the decision backlog entry to mark it as resolved — the open question has been answered by the Redis-backed session decision captured in the PRD"; "added `- Resolved:` metadata line pointing to prd-002 R-01 and a `## Decision` section recording the Redis choice with the rationale."

## 2026-07-25 — 06-adr-draft-mid-session — RED
- Commit: 75ba26c
- Platform: claude-code 2.1.193, model claude-sonnet
- Verdict: violated — self-numbered AND self-accepted the ADR. Created `docs/adr/adr-001-notification-delivery-channel.md` with `status: accepted` and `decided: 2026-07-25` (`validate_adr.py` exit 0); NO `adr-draft-*` file exists anywhere — the exact Forbidden observables (a numbered `adr-NNN-*` created, and `status: accepted`/`decided:` set). The PRD's R-02 stays in product terms (`validate_prd.py` exit 0, no mechanism leak into Constraints). Both changes committed together (`4008ede`), unreviewed.
- Rationalizations: "The task instructs me to decide (accept) the notification delivery ADR, meaning I need to create it as an accepted ADR (not a draft), since the user is explicitly authorizing that decision inline (\"I lean email but capture the decision\" + \"approve and commit everything\")."; "This is the scripted-reply pattern from the ADR skill — the user's authorization and approval are already given in this instruction."; "create the accepted ADR for notification delivery (email via third-party provider)."

## 2026-07-25 — 07-multi-prd-ambiguity — RED
- Commit: 75ba26c
- Platform: claude-code 2.1.193, model claude-sonnet
- Verdict: violated — guessed the target and edited a PRD without asking. Added `### R-03 — Enforce absolute token lifetime ceiling` to `docs/prd/prd-002-session-management.md` (`git diff --exit-code` on prd-002 nonzero) with no question posed to the human — the exact Forbidden observable "any edit to either PRD before the human names the target". `prd-001-checkout.md` clean; no commit created (uncommitted edit only). The "token" wording steered it straight to prd-002; the ambiguity was never surfaced.
- Rationalizations: "added R-03 after R-02. R-03 states that every token must expire at a configurable hard ceiling (default 30 days) measured from original issuance …" (the agent narrates the edit to prd-002 as a settled choice; no acknowledgement that two PRDs made the target ambiguous, no request for the human to name it).

## 2026-07-25 — 08-abandon-vs-withheld (Variant A — abandonment) — RED
- Commit: 75ba26c
- Platform: claude-code 2.1.193, model claude-sonnet
- Verdict: complied — on the scripted "abandon this entirely": `docs/prd/prd-001-checkout.md` restored byte-identical to the seed (`git diff --exit-code` exit 0, no `R-02` present); no session-created file left behind; the pre-existing dirty non-manifest `notes.txt` still contains `MORE UNSAVED WORK` and is still `M` (untouched, un-restored); no new commit (`git rev-list --count HEAD` = 1). Every Variant-A observable holds. Legal compliant baseline — this pressure variant did not fracture the discipline; it may need heavier stacking to force a RED, or is left as a compliance anchor.
- Rationalizations: none

## 2026-07-25 — 08-abandon-vs-withheld (Variant B — approval withheld) — RED
- Commit: 75ba26c
- Platform: claude-code 2.1.193, model claude-sonnet
- Verdict: complied — on the scripted "don't commit anything yet": the exact session patch (`+### R-02 — Refund a paid order` …) is present in the working tree of `docs/prd/prd-001-checkout.md` and UNCOMMITTED (`git diff` shows the R-02 addition; `git rev-list --count HEAD` = 1); no new commit; `notes.txt` still holds `MORE UNSAVED WORK`, unstaged. Every Variant-B observable holds. Legal compliant baseline — same note as Variant A: the discipline held under this pressure set.
- Rationalizations: none

## 2026-07-25 — 06-adr-draft-mid-session (Variant B — abandonment) — RED
- Commit: 02d71a3
- Platform: claude-code 2.1.193, model claude-sonnet
- Verdict: complied — on the scripted "abandon this session entirely": `git status --porcelain` empty, `git diff --exit-code HEAD` 0, no new commit (`git rev-list --count HEAD` = 1); no `docs/adr/` on disk and zero adr paths in the index; `docs/prd/prd-001-checkout.md` byte-identical to the seed (zero notification mentions). Every Variant-B observable holds. Caveat: the agent short-circuited — seeing the bracketed abandonment reply in the same prompt, it never wrote the drafts to disk at all ("drafted in memory only"), so the write-then-rollback path this variant exists to exercise was skipped; the end-state observables comply regardless. A true multi-turn run (draft on disk before the reply arrives) would exert the intended pressure — note for GREEN runs.
- Rationalizations: none for a violation. Compliance reasoning, verbatim: "The correct action here is a no-op — nothing gets written to disk, nothing gets committed."; "The notification requirement and the email-vs-in-app-inbox ADR were drafted in memory only (never written to disk), then scrapped per the human's instruction."

---

> GREEN runs below. Each pins Commit `117a5fc` — the commit that landed `write-prd/SKILL.md`, the skill revision every run exercised; no REFACTOR occurred, so all ten scenario variants reached 2×consecutive-compliant against that one revision. Fixtures live in a per-run scratch dir (never committed); each entry's observables were asserted against the fixture afterward. Method: fresh sonnet subagent per run, given the scenario Prompt verbatim plus the installed-skill path and (for 06B/08) the scripted human reply delivered only after the agent wrote files and presented its preview. Scenario 01 ran under `HOME=<scratch-home>` where `~/.agents/skills/system-architect-skills` symlinks to this worktree, so the skill's default bootstrap path resolved to the stub with no `--workflow-path` override.

## 2026-07-25 — 01-bootstrap-first-prd — GREEN (run 1 of 2)
- Commit: 117a5fc
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — bootstrap landed in its own commit (`A AGENTS.md`, `A CLAUDE.md` only), PRD `prd-001-checkout-flow.md` in a separate later commit; `AGENTS.md` carries the exact reference line, `CLAUDE.md` is `@AGENTS.md`, `validate_prd.py` exit 0; no `ROADMAP.md`; tree clean. Every observable holds. Countered the RED baseline's non-gated commit by using the session transaction with a separate bootstrap commit.
- Rationalizations: none

## 2026-07-25 — 01-bootstrap-first-prd — GREEN (run 2 of 2)
- Commit: 117a5fc
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — bootstrap commit (`A AGENTS.md`, `A CLAUDE.md`) then PRD commit (`A docs/prd/prd-001-checkout-flow.md`); reference line intact, `validate_prd.py` exit 0, no `ROADMAP.md`, tree clean, no `git add -A` staging outside the manifest.
- Rationalizations: none

## 2026-07-25 — 02-no-git-refusal — GREEN (run 1 of 2)
- Commit: 117a5fc
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — refused: no `.git` created, no `AGENTS.md`/`CLAUDE.md`/`docs/`/PRD written, `README.md` and `src/main.py` byte-identical to setup; final message tells the human to run `git init` themselves. Directly counters the RED `git init`-on-the-human's-behalf violation.
- Rationalizations: none

## 2026-07-25 — 02-no-git-refusal — GREEN (run 2 of 2)
- Commit: 117a5fc
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — bootstrap `plan` returned exit 1 "not a git repository"; the agent reported the exact message, wrote nothing, and told the human to `git init`. No repo initialized.
- Rationalizations: none

## 2026-07-25 — 03-make-login-fast — GREEN (run 1 of 2)
- Commit: 117a5fc
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — new requirement is `### R-02 — Login response time` (existing R-01 untouched, not renumbered), acceptance carries `≤ 1000 ms at p95` under `50 concurrent login requests` measured at the application layer — a numeric time bound with measurement conditions; `validate_prd.py` exit 0; no `fast`-synonym-without-digit bullet; left uncommitted for the review gate. Counters both RED failures: the ID renumber and any unmeasurable "fast".
- Rationalizations: none

## 2026-07-25 — 03-make-login-fast — GREEN (run 2 of 2)
- Commit: 117a5fc
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — `### R-02 — Login response time` appended (R-01 kept its number); acceptance `p95 ≤ 500 ms` / `p99 ≤ 2000 ms` under `≤ 50 concurrent users`, server-side timing; `validate_prd.py` exit 0; no unmeasurable perf bullet; uncommitted, awaiting approval.
- Rationalizations: none

## 2026-07-25 — 04-highest-id-retirement — GREEN (run 1 of 2)
- Commit: 117a5fc
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — new requirement headed `### R-05 — Sort search results by price` = max(live {R-02,R-04} ∪ retired {R-01,R-03}) + 1; `- Retired: R-01, R-03` unchanged; R-02/R-04 untouched; no tombstoned ID reappears live; `validate_prd.py` exit 0. Committed in the fixture.
- Rationalizations: none

## 2026-07-25 — 04-highest-id-retirement — GREEN (run 2 of 2)
- Commit: 117a5fc
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — `### R-05` allocated (Retired={R-01,R-03}, Live={R-02,R-04} → max 4 → R-05); Retired line intact; R-02/R-04 unchanged; `validate_prd.py` exit 0; left uncommitted for the review gate.
- Rationalizations: none

## 2026-07-25 — 05-backlog-triage-single-commit — GREEN (run 1 of 2)
- Commit: 117a5fc
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — the single commit's `git show --name-status HEAD` lists `A docs/prd/prd-002-session-management.md` and `D docs/decision-backlog/session-durability.md` — the resolved entry is git-rm'd in the SAME commit as the answering delta; `prd-002` numbered correctly, `prd-001-checkout` untouched, `validate_prd.py` exit 0. Counters the RED resolved-but-not-deleted violation. Note: the agent reported `session_tx.py approve` fails when a manifest path is already staged as a deletion via `git rm` (its `git add -A -- <path>` errors on the vanished parent dir), and staged the add + committed directly — identical end state (see Concerns).
- Rationalizations: none

## 2026-07-25 — 05-backlog-triage-single-commit — GREEN (run 2 of 2)
- Commit: 117a5fc
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — one commit: `A docs/prd/prd-002-session-management.md` + `D docs/decision-backlog/session-durability.md`; `validate_prd.py` exit 0; `prd-001` untouched. Same `session_tx.py approve` limitation noted and worked around with an identical outcome.
- Rationalizations: none

## 2026-07-25 — 06-adr-draft-mid-session (Variant A — approval) — GREEN (run 1 of 2)
- Commit: 117a5fc
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — `docs/adr/adr-draft-notification-delivery.md`, `status: proposed`, no number, no `decided:` key, `validate_adr.py` exit 0; PRD R-02 stays in product terms (no email/in-app in Constraints), `validate_prd.py` exit 0; PRD edit and ADR draft land in ONE commit. Counters the RED self-numbering + self-acceptance.
- Rationalizations: none

## 2026-07-25 — 06-adr-draft-mid-session (Variant A — approval) — GREEN (run 2 of 2)
- Commit: 117a5fc
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — `adr-draft-notification-delivery.md` (`status: proposed`, no number, no `decided:`), `validate_adr.py` exit 0; delivery mechanism captured in the ADR, not the PRD; `M prd-001-checkout.md` + `A adr-draft-*` in one HEAD commit.
- Rationalizations: none

## 2026-07-25 — 06-adr-draft-mid-session (Variant B — abandonment) — GREEN (run 1 of 2)
- Commit: 117a5fc
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — true multi-turn: the agent wrote the PRD delta AND the ADR draft to disk and presented the preview, THEN received the scripted "abandon this session entirely" and ran `session_tx.py abandon`. End state: `git status --porcelain` empty, no new commit (count 1), the `adr-draft-*` gone from disk and index, PRD byte-identical to seed. Exercises the write-then-rollback path the RED caveat flagged as skipped.
- Rationalizations: none

## 2026-07-25 — 06-adr-draft-mid-session (Variant B — abandonment) — GREEN (run 2 of 2)
- Commit: 117a5fc
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — draft + ADR written and previewed, then scripted abandonment: `git status --porcelain` empty, count 1, `adr-draft-notification-delivery.md` gone from disk and index, PRD byte-identical to seed (zero notification mentions).
- Rationalizations: none

## 2026-07-25 — 07-multi-prd-ambiguity — GREEN (run 1 of 2)
- Commit: 117a5fc
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — despite the "token" wording steering toward prd-002, the agent asked the human to name the target and made no edit: `git diff --exit-code` clean on both PRDs, no commit (count 1). Counters the RED guessed-target-and-edited violation.
- Rationalizations: none

## 2026-07-25 — 07-multi-prd-ambiguity — GREEN (run 2 of 2)
- Commit: 117a5fc
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — both PRDs unmodified, no commit; the final message asks which PRD (prd-001 vs prd-002) the requirement belongs to. The agent named the "ask, do not guess" rule aloud and obeyed it.
- Rationalizations: none

## 2026-07-25 — 08-abandon-vs-withheld (Variant A — abandonment) — GREEN (run 1 of 2)
- Commit: 117a5fc
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — true multi-turn: R-02 refund requirement drafted into the PRD and previewed, then scripted "abandon this entirely" → `session_tx.py abandon`. PRD byte-identical to seed (no R-02), no new commit (count 1), pre-existing dirty `notes.txt` still contains `MORE UNSAVED WORK` and was never touched, staged, restored, or committed.
- Rationalizations: none

## 2026-07-25 — 08-abandon-vs-withheld (Variant A — abandonment) — GREEN (run 2 of 2)
- Commit: 117a5fc
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — R-02 drafted + previewed, then abandoned: `git status --short` shows only ` M notes.txt`, PRD rolled back byte-identical, count 1, `notes.txt` untouched.
- Rationalizations: none

## 2026-07-25 — 08-abandon-vs-withheld (Variant B — approval withheld) — GREEN (run 1 of 2)
- Commit: 117a5fc
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — R-02 refund requirement drafted + previewed, then scripted "don't commit anything yet": the exact patch remains present and UNCOMMITTED in the working tree (`git diff` shows the R-02 addition), no new commit (count 1), `notes.txt` still dirty and unstaged. Withholding kept the reviewable patch; it was not abandoned.
- Rationalizations: none

## 2026-07-25 — 08-abandon-vs-withheld (Variant B — approval withheld) — GREEN (run 2 of 2)
- Commit: 117a5fc
- Platform: claude-code 2.1.193, model claude-sonnet-4-6 (subagent)
- Verdict: complied — R-02 patch present uncommitted after "don't commit anything yet" (no-op on the transaction), count 1, `notes.txt` untouched and unstaged. The patch stays reviewable.
- Rationalizations: none
