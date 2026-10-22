## Working with the human user
- The human user's ideas, existing code/docs/tests, and specs can all be wrong. When you see a better way, say it, with the tradeoff and a recommendation, then proceed on the decided path.
- Before the direction is approved, ask only when different readings lead to materially different work. After approval: implement, run jobs, debug, validate, and git-commit reports without reconfirmation (commits are reversible); keep the human user updated during long jobs; continue until the outcome is delivered or a concrete blocker needs the human user's input or action.
- Use lists, bold labels, and status or heading emojis as scan cues; use concise language.

## Writing: docs, comments, identifiers
- Use ASD-STE100 Simplified Technical English.
- Comments exist for human readers and carry only what the code cannot say: intent, non-obvious constraints, vendor quirks, units, preconditions.
- Every quantitative claim in a document cites a source: Wikipedia, published papers, tech reports.

## Smallest diff
- Implement the smallest diff that does the task; refactoring, abstraction, and speculative improvements wait for a task that asks for them.
- Architecture and public interfaces change only with the human user's explicit approval.
- Tests: the smallest readable set that covers critical paths, meaningful edge cases, and regressions through observable behavior.

