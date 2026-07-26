## Current Workflow Status

- Current milestone: MS-002 — Parser
- Milestone state: paused
- Active feature: none
- Blocker: session-store choice needs human judgment
- Next action: human: resolve docs/decision-backlog/session-store.md

## MS-001 — Setup

- State: accepted
- Goal: increment 60 works end to end.
- Covers: PRD-001 REQ-060

### FEAT-001 — Scaffold

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

## MS-002 — Parser

- State: paused
- Goal: increment 61 works end to end.
- Covers: PRD-001 REQ-061

### FEAT-002 — Tokenizer

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

### FEAT-003 — Parser core

- Status: blocked(session-store)
- Description: build the AST from tokens.
- Acceptance: golden files match.
- Test intent: golden-file comparison tests.

## MS-003 — CLI

- State: planned
- Goal: increment 62 works end to end.
- Covers: PRD-001 REQ-062

### FEAT-004 — Renderer

- Status: todo
- Description: render AST to text.
- Acceptance: round-trip is lossless.
- Test intent: property test on round-trip.
