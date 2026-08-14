# FANG

FANG (Framing, Assumptions, Non-goals, Goals) is a skill that turns rough ideas into a problem statement brief through a grilling interview.

## Why

AI agents need a formal, agreed problem statement before solution work starts. Without one, agents jump to implementation on a problem nobody confirmed. FANG uses grilling — a one-question-per-turn interview — to align the human and the agent on the problem itself, and records the result in a reviewable brief.

## How

1. Kick off with `/fang` (Claude Code) or `$fang` (Codex), together with your initial ideas.
2. Answer the grilling questions one at a time. Each question comes with a recommended answer.
3. Keep the discussion high-level: the problem, who it affects, goals, non-goals, scope. Do not go into implementation details; leave those to a later phase without this skill.
4. Review the delivered brief in `docs/fang/`. The agent re-enters grilling until you confirm the framing, then marks the brief `Aligned`.

## What

- **Inputs:** your initial ideas (plus any source material in scope) and a grilling session with the agent.
- **Output:** `docs/fang/FANG-<date>-<topic>.md` in the project (or inline when no folder is in scope), following [assets/template.md](assets/template.md): framing, assumptions, non-goals, goals with success signals, and evidence provenance, plus open questions when unknowns remain.
