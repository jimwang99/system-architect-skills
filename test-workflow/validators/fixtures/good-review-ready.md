## Current Workflow Status

- Current milestone: M02 — Parser
- Milestone state: review-ready
- Active feature: none
- Next action: human: run review-milestone M02

## M01 — Setup

- State: accepted

### F01 — Scaffold

- Status: done
- Description: scaffold the project.
- Acceptance: repo builds.
- Test intent: smoke test.
- Evidence:
  - Base: aaa1111
  - Commits: aaa1111..bbb2222
  - Tests: pass — 12/12
  - Reviewer: codex-cli 0.145.0
  - Verdict: approve
  - Findings: none

## M02 — Parser

- State: review-ready

### F02 — Tokenizer

- Status: done
- Description: split input into tokens.
- Acceptance: tokens match spec table.
- Test intent: table-driven unit tests.
- Evidence:
  - Base: bbb2222
  - Commits: bbb2222..ccc3333
  - Tests: pass — 20/20
  - Reviewer: codex-cli 0.145.0
  - Verdict: approve-with-findings
  - Findings: naming nit: fixed

### F03 — Parser core

- Status: done
- Description: build the AST from tokens.
- Acceptance: golden files match.
- Test intent: golden-file comparison tests.
- Evidence:
  - Base: ccc3333
  - Commits: ccc3333..ddd4444
  - Tests: pass — 20/20
  - Reviewer: codex-cli 0.145.0
  - Verdict: approve-with-findings
  - Findings: naming nit: fixed

## M03 — CLI

- State: planned

### F04 — Renderer

- Status: todo
- Description: render AST to text.
- Acceptance: round-trip is lossless.
- Test intent: property test on round-trip.
