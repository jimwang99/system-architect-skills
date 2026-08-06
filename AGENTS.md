## General guidelines
- Don't be too agreeable. The user can be wrong. Challenge their ideas — in one sentence with the reason, then proceed. No hedging, no re-litigating.
- Don't assume existing code/documents/tests are already the best solutions. If you see a better one, say so: name the tradeoff and give a recommendation — not a survey of every option.
- When writing comments in code, write the intent, not what has been implemented. Comment must be human centric. Never write a docstring or comment that restates the signature or the code. Non-obvious constraints, vendor quirks, units, and preconditions earn a line; self-evident code does not.
- Whenever comes to data, find solid references to support them. Good references can be wikipedia, published papers and tech reports.
- HUMAN.md is manually managed by human user. AI agents can read it, but shall never modify it.
- Use clear, simple, ESL-friendly English in both documentation and code. Prefer common, direct words for comments and identifiers; avoid jargon, idioms, obscure abbreviations, and clever names.
- When reporting information to me or write documents, be extremely concise and sacrifice grammar and gentleness for the sake of concision.

## Tech stack

- When creating documentation use Markdown format; when creating block diagrams or flow chart, use ASCII art format with a list of explanations with natural language.
- In Markdown files, never hard-wrap prose. One paragraph = one line; let the renderer wrap. (Exception: tables, code blocks.)
- Use `uv` to manage Python virtual environment
- Use `loguru` instead of raw print or logging in Python source code

## Prevent over-engineering

- Don't over-engineer, and ask clarification questions when you are not clear.
- Preserve architecture and existing interfaces. Never make architectural or API changes without explicit approval from human.
- Implement the smallest possible diff. Avoid refactoring, abstraction, or speculative improvements beyond the requested task.
- Write the smallest set of readable, behavior-focused tests that cover critical paths, meaningful edge cases, and regressions; do not test implementation details or exhaustively enumerate trivial cases.
- Sometimes specs are also AI generated. "The spec says so" is not the same as "this is right".

