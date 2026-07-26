---
name: execute-milestone/references/codex
---

# execute-milestone — Codex reference

This file covers only mechanics that differ from the platform-neutral SKILL.md. Read SKILL.md first.

## Invocation guard

Codex has no visibility mechanism equivalent to `disable-model-invocation: true`. The guard is behavioral: this skill runs only when the human's message explicitly names `execute-milestone MS-NNN`. A missing argument is acceptable only when exactly one milestone is in state `planned`, `in-progress`, or `paused` — infer that one. Otherwise stop and ask. Never self-start from ambient descriptions of readiness.

## Workers

Workers are codex subagent invocations with document-only prompts — PRD, ADRs, ROADMAP, plan files. No transcripts. Each invocation terminates when it returns output.

- Planner: feature's ROADMAP entry + accepted ADRs → plan file content.
- Plan-validator: plan file + same documents → verdict.
- Implementer: plan file + relevant source files → implementation. One per feature.

Workers never touch ROADMAP. The main invocation writes every ROADMAP transition.

## Reviewer wrapper sketch (non-normative)

A production Codex install would place a shell script named `workflow-review` on `PATH` that invokes `claude -p` with the diff range and a JSON-verdict instruction:

```sh
#!/bin/sh
# NON-NORMATIVE — illustrates the cross-platform review pattern
claude -p "Review the diff from $1 to $2. Return only a JSON object: \
  {\"verdict\": \"approve\"|\"approve-with-findings\"|\"reject\", \
  \"findings\": [{\"severity\": \"blocking\"|\"advisory\", \"title\": \"...\", \"detail\": \"...\"}]}"
```

The reviewer platform always differs from the implementer platform — a Codex-implemented feature is reviewed by Claude, and vice versa. The gate helper (`review_gate.py`) drives this wrapper.
