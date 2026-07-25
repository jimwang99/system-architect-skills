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
