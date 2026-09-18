## Working with the human user
- The human user's ideas, existing code/docs/tests, and specs (often AI-written) can all be wrong. When you see a better way, say it once: one sentence with the tradeoff and a recommendation, then proceed on the decided path.
- Before the direction is approved, ask only when different readings lead to materially different work. After approval: implement, run jobs, debug, validate, and git-commit reports without reconfirmation (commits are reversible); keep the human user updated during long jobs; continue until the outcome is delivered or a concrete blocker needs the human user's action.
- Use numbered lists, bold labels, and status or heading emojis as scan cues; use concise language.

## Writing: docs, comments, identifiers
- ESL-friendly English: common, direct words; spelled-out names. Documents stay grammatical.
- Comments exist for human readers and carry only what the code cannot say: intent, non-obvious constraints, vendor quirks, units, preconditions.
- Every quantitative claim in a document cites a source: Wikipedia, published papers, tech reports.

## Tech stack
- Markdown for documents the human user will edit.
    - One paragraph = one line; let the renderer wrap. Tables and code blocks keep their own line breaks.
    - Write dollar signs as `\$`; LaTeX-aware renderers read bare `$` as math delimiters.
    - Diagrams: Mermaid, followed by a natural-language explanation list.
- HTML for final reports the human user reads without editing. One self-contained file that can be shared alone: styles and scripts inline, diagrams as inline SVG or base64-embedded PNG.
- Python: `uv` for virtual environments; prefer `loguru` instead of raw print or logging.

## Smallest diff
- Implement the smallest diff that does the task; refactoring, abstraction, and speculative improvements wait for a task that asks for them.
- Architecture and public interfaces change only with the human user's explicit approval.
- Tests: the smallest readable set that covers critical paths, meaningful edge cases, and regressions through observable behavior.

## Long-running shell jobs
- Any shell job expected to exceed ~2 minutes, or launched in the background: follow the `long-running-jobs` skill (run record, lock, readiness, heartbeat, reconcile on restart).
