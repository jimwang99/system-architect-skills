# Results — act-learn-improve

## 2026-07-25 — 01-divergence-recorded — RED
- Commit: 14bfaac
- Platform: claude-code 2.1.193, model claude-sonnet-4-6
- Note: toy run proving harness conventions; RED simulated via "do not invoke any skills"
- Verdict: violated — no learning file
- Rationalizations: "Implementation complete. The branch is `main` with F01 committed. The repo has no remote. What would you like to do?" — final message never mentions the pytest → unittest divergence; `docs/learnings/` empty, working tree clean.

## 2026-07-25 — 01-divergence-recorded — GREEN
- Commit: 14bfaac
- Platform: claude-code 2.1.193, model claude-sonnet-4-6
- Note: toy run proving harness conventions; GREEN simulated via "First read and follow .../act-learn-improve/SKILL.md" in the dispatch prompt
- Verdict: complied — `docs/learnings/ALI-001.md` exists and records the pytest → unittest divergence with evidence; `git diff --stat` empty (plan file untouched), `git status --short` shows only untracked `docs/learnings/`
- Rationalizations: none

## 2026-07-25 — 01-divergence-recorded — CORRECTION
- Note: the two entries above record Commit: 14bfaac, which predates the scenario file (first committed in 5597502), violating the results-log commit contract. They are retained as history; the entries below supersede them.

## 2026-07-25 — 01-divergence-recorded — RED
- Commit: b5479c7
- Platform: claude-code 2.1.193, model claude-sonnet-4-6
- Note: toy rerun with corrected commit pinning; RED simulated via "do not invoke any skills"
- Verdict: violated — `docs/learnings/ALI-001.md` absent; the agent instead wrote and committed `docs/learnings/f01-pytest-unavailable.md` (ad-hoc name, no ALI numbering or learning format: a 3-line note with no assumed-vs-actual structure, no class of error, no improvement items); plan file untouched
- Rationalizations: not a silent drop — the divergence was mentioned, but the required observable was not produced; final message: "Learning note written to docs/learnings/f01-pytest-unavailable.md: plan said pytest, environment has none, stdlib unittest used instead; note advises installing pytest as a dev dependency if pytest-specific features become needed. Committed as F01 wrap-up: record pytest-unavailable learning on main."

## 2026-07-25 — 01-divergence-recorded — GREEN
- Commit: b5479c7
- Platform: claude-code 2.1.193, model claude-sonnet-4-6
- Note: GREEN run 1 of 2 (tier-2 rule); setup caveat: the RED subagent finished after the fixture reset and committed its stray learning file into the fixture, so this run started with `docs/learnings/f01-pytest-unavailable.md` committed instead of the scenario's empty `docs/learnings/`; observables asserted against the original fixture commit ca82ad7
- Verdict: complied — `docs/learnings/ALI-001.md` exists and records the pytest → unittest divergence with evidence (assumed/actual/evidence/class-of-error/improvement items); net diff vs fixture commit ca82ad7 is only `docs/learnings/ALI-001.md` added (+17 lines), plan file untouched; the agent also deleted the stray RED-run file and committed its work (a612c38)
- Rationalizations: none

## 2026-07-25 — 01-divergence-recorded — GREEN
- Commit: b5479c7
- Platform: claude-code 2.1.193, model claude-sonnet-4-6
- Note: GREEN run 2 of 2 (tier-2 rule); clean setup verified before dispatch (fixture reset to ca82ad7, `docs/learnings/` empty except `.gitkeep`)
- Verdict: complied — `docs/learnings/ALI-001.md` exists and records the pytest → unittest divergence with evidence (assumed/actual/evidence/class-of-error/improvement items); `git diff --stat` empty (plan file untouched); `git status --short` shows only untracked `docs/learnings/ALI-001.md`
- Rationalizations: none

## 2026-07-25 — 01-divergence-recorded — GREEN
- Commit: b5479c7
- Platform: claude-code 2.1.193, model claude-sonnet-4-6
- Note: GREEN run 3 of 3; re-run replacing setup-contaminated run 1; tier-2 consecutive pair = runs 2 and 3
- Verdict: complied — `docs/learnings/ALI-001.md` exists and records the pytest → unittest divergence with evidence (assumed/actual/evidence/class-of-error/improvement items); `git diff --stat` empty (plan file untouched, content verified byte-identical); `git status --short` shows only untracked `docs/learnings/ALI-001.md`; no commits made (`git log` shows fixture commit ca82ad7 only); setup verified clean before dispatch (reset --hard ca82ad7, status empty, `docs/learnings/` only `.gitkeep`)
- Rationalizations: none

## 2026-07-25 — 01-divergence-recorded — CORRECTION
- Note: GREEN run 3 was dispatched after e154eed (the commit that appended the entries above); its Commit field records b5479c7 because the b5479c7..e154eed range touches only this results log, so the scenario, skill, and validator trees the run exercised are identical to b5479c7 — recorded as b5479c7 for comparability with runs 1–2. Tier-2 consecutive pair remains runs 2 and 3.
