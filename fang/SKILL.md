---
name: fang
description: Interview the user and create or revise a FANG brief for confirmed high-level agreement on a problem before solution work. Use only when the user invokes the skill, asks for a FANG brief, or explicitly requests problem framing without solutions.
---

# FANG

FANG (Framing, Assumptions, Non-goals, Goals) is the problem-framing brief this skill produces as input for later solution-phase tasks. Use grilling — a one-question-per-turn interview defined below — to discover what the user really wants, frame the problem, and realign until the user confirms shared understanding. Stop before solution exploration.

## Keep the boundary

- Frame the problem only. Leave solutions, features, architecture, interfaces, technologies, implementation details, and execution plans out.
- If the user requests solution work, push back briefly and continue only with problem framing. Recommend a separate task without this skill after alignment.
- Constrain grilling to affected parties, observed conditions, impact, urgency, evidence, scope, goals, non-goals, risks, and agreement criteria.
- Keep evidence, assumptions, and unknowns visibly separate.
- Treat unsupported user-provided claims as unverified, even after the user confirms the framing.
- Never invent citations, measurements, owners, deadlines, or confidence.

## 1. Establish available facts

1. Read the user's idea and every source in scope.
2. Look up facts available through the environment or tools before asking the user. Do not ask the user for discoverable facts.
3. Give every material factual claim a stable evidence ID and record the claim, its source or provenance, and one status: `Verified`, `Unverified`, or `Conflicting`. Use `Verified` only when an available authoritative source supports the claim; use `Unverified` when it rests only on user input or lacks support; use `Conflicting` when sources disagree. Surface conflicts instead of silently choosing one source.

## 2. Grill for the real problem

Run the grilling interview directly inside FANG. Do not defer it to a separate task or skill.

1. Start with the highest-leverage unresolved problem-framing decision.
2. Ask exactly one non-compound question about one decision per turn and wait for the user's answer.
3. Give a recommended answer with each question, grounded in the available information.
4. Walk dependent decisions one by one. The decisions belong to the user; do not resolve them on the user's behalf.
5. If the user does not know an answer, ask whether to record it as an accepted unknown and identify what evidence could resolve it.
6. Continue until the user explicitly confirms that the high-level problem framing reflects what they want. Do not draft the FANG before that confirmation.

## 3. Draft the FANG

1. Use [assets/template.md](assets/template.md) as the output structure.
2. Remove instructional placeholders and keep every section; only `Open questions` is optional and may be omitted when no material unknowns remain. An `Aligned` FANG requires substantive `Framing` and at least one `Goal`. Write `None identified` for `Assumptions` or `Non-goals` only after the user explicitly confirms that absence. In a `Draft`, write `Not yet established` for an unresolved section and add the missing decision to `Open questions`.
3. Cite every material factual claim with its evidence ID and populate `Evidence and provenance` with the claim, source or provenance, and verification status.
4. Identify the high-level agreement the FANG must enable. If it remains inferred, label it as an assumption.
5. Phrase the problem without embedding a preferred solution. If the source contains a proposed solution, recover the underlying problem and record the proposal only as a labeled solution hypothesis when necessary for context. Do not elaborate on or evaluate it.
6. Make goals outcome-oriented and pair each with an observable success signal. State explicit non-goals.
7. Rank open questions by their potential to change the problem boundary or agreement. Give each one a stable ID `Q<n>` so the user can answer by number. Never renumber or reuse an ID after a question is resolved or dropped.

## 4. Review and realign

1. Review the draft for problem-framing completeness, internal consistency, and factual support.
2. If anything material is missing, contradictory, unsupported, or apparently incorrect, re-enter the grilling loop immediately.
3. Present one review issue at a time using the grilling rules from step 2. Do not bundle review issues or decisions.
4. Use available sources or tools to resolve factual questions before asking. When evidence and the user's belief conflict, show the conflict and ask the user how the framing should represent it.
5. Update the draft after each answer, review it again, and continue until all material issues are resolved or explicitly accepted as unknowns.
6. Ask the user to confirm the reviewed full document. Set the status to `Aligned` only after explicit confirmation. If the user stops earlier, keep `Draft` and preserve all unresolved open questions.

## 5. Deliver and stop

- When working in a project or user-designated folder, write the brief to `docs/fang/FANG-<date>-<topic>.md`, where `<date>` is the creation date as `YYYY-MM-DD` and `<topic>` is a short kebab-case slug. Revise an existing brief in place; never create a new dated file for the same problem. When no folder is in scope, return the completed Markdown inline.
- Write every heading, field, explanation, and artifact in English. Translate non-English source material while preserving meaning and retain proper names or identifiers when translation would make them inaccurate.
- Suggest the next step as a separate task that takes the FANG as input, routed by the state of the framing:
  - Default: use the `grill-with-docs` skill to discuss solutions.
  - When a candidate solution needs evidence before commitment: use the `prototype` skill to investigate it first.
  - When the topic is still too vague or broad for solution discussion: use the `research` skill to find references and synthesize a deep-dive, then return to `grill-with-docs`.
- Do not execute the suggested next step automatically.
- Do not hand off problem-framing grilling to a separate task; it is embedded in FANG. The `grill-with-docs` suggestion is for solution work only.
- Stop after delivering the confirmed FANG or the explicitly unfinished draft.
