# FANG

FANG (Framing, Assumptions, Non-goals, Goals) is a skill that turns rough ideas into an agreed problem brief.

## Why

AI agents need an agreed problem statement before solution work starts. FANG drafts from available evidence, asks one material question at a time, and records decisions in a reviewable brief.

## How

1. Invoke the `fang` skill with your initial ideas and any source material.
2. Review the initial draft and answer material questions one at a time. Each question includes a recommendation and reason.
3. Keep the discussion high-level: the problem, who it affects, goals, non-goals, scope. Do not go into implementation details; leave those to a later phase without this skill.
4. Review the complete brief in `docs/fang/`. The agent revises it until you confirm the full framing, then marks it `Aligned`.

## What

- **Inputs:** your initial ideas, source material in scope, and answers to unresolved material questions.
- **Output:** `docs/fang/FANG-<date>-<topic>.md` in the project (or inline when no folder is in scope), following [assets/template.md](assets/template.md): framing, assumptions, non-goals, goals with success signals, and evidence provenance, plus open questions when unknowns remain.
