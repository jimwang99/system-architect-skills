---
name: execute-milestone/references/claude-code
---

# execute-milestone — Claude Code reference

This file covers only mechanics that differ from the platform-neutral SKILL.md. Read SKILL.md first.

## Invocation guard

`disable-model-invocation: true` in the frontmatter is the mechanical guard: Claude Code will not surface this skill to the model unless the human explicitly invokes it. The explicit-invocation first line in SKILL.md provides the behavioral guard inside the session.

## Workers

Workers are Task-tool subagents with fresh context each time. Pass only documents (PRD, ADRs, ROADMAP, plan files) — never transcripts. Each worker terminates when it returns output.

- Planner: feature's ROADMAP entry, PRD excerpts, accepted ADRs → plan file content.
- Plan-validator: plan file + same documents → verdict and gaps.
- Implementer: plan file + relevant source files → implementation. One per feature.

Workers never touch ROADMAP. The main invocation writes every ROADMAP transition.

## Reviewer wrapper sketch (non-normative)

A production Claude Code install would place a shell script named `workflow-review` on `PATH` that invokes the Codex CLI with the diff range and a JSON-verdict instruction:

```sh
#!/bin/sh
# NON-NORMATIVE — illustrates the cross-platform review pattern
codex exec --no-project-doc \
  "Review the diff from $1 to $2. Return only a JSON object: \
  {\"verdict\": \"approve\"|\"approve-with-findings\"|\"reject\", \
  \"findings\": [{\"severity\": \"blocking\"|\"advisory\", \"title\": \"...\", \"detail\": \"...\"}]}"
```

The reviewer platform always differs from the implementer platform. The gate helper (`review_gate.py`) drives this wrapper — the skill never calls `workflow-review` directly.
