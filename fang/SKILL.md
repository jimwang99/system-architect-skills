---
name: fang
description: Create or revise a FANG problem-framing brief through a focused interview. Use when the user explicitly requests a FANG brief or problem framing without solution design.
---

# FANG

FANG means Framing, Assumptions, Non-goals, and Goals. It records confirmed high-level agreement on the problem before solution work starts.

## Boundary

Frame the problem only: affected parties, observed conditions, impact, urgency, evidence, scope, goals, non-goals, risks, and agreement criteria. Leave features, architecture, interfaces, technologies, implementation, and execution plans for a separate task.

When the source begins with a proposed solution, recover the underlying problem. Retain the proposal only as a one-line, unevaluated solution hypothesis when its provenance matters.

Keep external facts, user reports, assumptions, conflicts, and unknowns distinct. The user is authoritative for their goals, preferences, and experience, but user confirmation does not verify an external factual claim.

## 1. Establish Evidence

Read every source in scope. Verify discoverable facts only when they materially affect the problem boundary or agreement; avoid turning framing into an unrelated research project.

Give each material factual claim a stable `E<n>` ID and one status:

- `Supported`: an inspected authoritative source supports the claim.
- `User-reported`: the user is the source for their intent, experience, or internal condition.
- `Unverified`: available evidence does not establish the claim.
- `Conflicting`: relevant sources disagree.

Record each claim as a bullet in the template: `E<n>`, status, and claim on the first line; source or provenance in a sub-bullet. Surface conflicts rather than choosing silently. Preserve assumptions and accepted unknowns as such.

## 2. Build a Provisional Brief

Read [assets/template.md](assets/template.md) and draft the strongest provisional FANG supported by current context. Draft before interviewing so the user can react to a concrete framing.

Optimize for a one-minute first pass:

- Lead with one quoted problem sentence and the decision needed.
- Default to three bullets or fewer per section and one short sentence per bullet.
- Let `Evidence and provenance` and `Open Questions` exceed that limit only for material items.
- Use bold labels and a few meaningful status or heading emojis as scan cues.
- Delete repeated context, transitions, and explanation. Put supporting detail in linked sources.

An `Aligned` brief needs substantive framing, an explicit agreement sought, at least one outcome goal with an observable success signal, and no unresolved material boundary decision. A `Draft` may use `Not yet established` and record the missing decision under `Open Questions`.

Keep every required template section. Omit `Open Questions` when no unresolved or accepted-unknown question remains. Use one `None identified` bullet for assumptions or non-goals only after the user confirms that absence.

## 3. Resolve Material Decisions

If the provisional brief has material unresolved decisions, ask all of them in one batch and wait for the answers. Keep each question non-compound and limited to one decision.

For each question, give two or three mutually exclusive options. Put the recommended option first, mark it `Recommended`, and give one short reason based on current evidence. When evidence is weak, label the choice as a working recommendation. Include an accepted-unknown option when it is a reasonable outcome and name evidence that could resolve it.

Assign each question a stable `Q<n>` ID. When resolved, merge the answer into the relevant body section and remove the question from `Open Questions`. Keep only unresolved and accepted-unknown questions there. Never renumber or reuse an ID during the working session.

Update the provisional brief after each batch response. Ask another batch only when an answer exposes a new decision that could change the framing, scope, goals, non-goals, or agreement.

## 4. Review and Confirm

Review the full brief for problem-framing completeness, internal consistency, solution leakage, and factual support. Ask another question batch only for a material boundary issue, a contradiction, or an unsupported statement presented as fact.

Present the complete reviewed brief and ask for explicit confirmation. Set `Status: Aligned` only after the user confirms the full document. If the user stops earlier or accepts unresolved material questions, deliver `Status: Draft`.

## 5. Deliver and Stop

The user's path and repository convention take priority. Otherwise write a project brief to `docs/fang/FANG-<YYYY-MM-DD>-<topic>.md`; revise an existing brief for the same problem in place. When no project folder is in scope, return the Markdown inline.

Use the user's language; default to clear English when none is implied.

After delivery, suggest one separate next-task capability that fits the result: solution exploration, research for an evidence gap, or a throwaway prototype for a risky hypothesis. Name a specific skill only when it is available. Do not start that task automatically.

Finish when the delivered status matches the confirmation state, every material fact has an evidence status, every goal has a success signal, and every unresolved decision remains visible.
