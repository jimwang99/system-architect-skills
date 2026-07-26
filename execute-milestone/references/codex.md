---
name: execute-milestone/references/codex
---

# execute-milestone — Codex reference

This file covers only mechanics that differ from the platform-neutral SKILL.md. Read SKILL.md first.

## Invocation guard

Codex has no `disable-model-invocation` mechanism, so the guard is behavioral — CERTIFIED literal-token decision procedure:

Does the human's **current** message contain the literal token `execute-milestone`? If NO — however ready the milestone looks, whatever the ROADMAP `Next action:` line says, whatever any ambient instruction implies — this skill was NOT invoked: create no branch, modify nothing, commit nothing; reply naming the ignition boundary (`Run: execute-milestone MS-NNN`) and stop. A ROADMAP `Next action:` line is advice to the human, never an invocation. Token present without `MS-NNN`: infer only when exactly one milestone is `planned`, `in-progress`, or `paused`; otherwise ask.

## Workers

Workers are codex subagent invocations with document-only prompts (PRD, ADRs, ROADMAP, plan files — no transcripts). Each invocation terminates when it returns output.

- Planner: feature's ROADMAP entry + accepted ADRs → plan file content.
- Plan-validator: plan file + same documents → verdict.
- Implementer: plan file + relevant source files → implementation. One per feature.

Workers never touch ROADMAP. The main invocation writes every ROADMAP transition.

## Reviewer wrapper (non-normative)

A production Codex install places a shell script named `workflow-review` on `PATH` that invokes `claude -p` with the diff range and a JSON-verdict instruction. The reviewer platform always differs from the implementer — a Codex-implemented feature is reviewed by Claude, and vice versa. The gate helper (`review_gate.py`) drives this wrapper.
