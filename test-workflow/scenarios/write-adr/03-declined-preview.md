---
skill: write-adr
type: application
tier: 2
---

## Setup

Identical to `02-acceptance-flow`:

- `docs/adr/adr-001-caching-strategy.md` — accepted.
- `docs/adr/adr-draft-retry-policy.md` — proposed, `resolves: retry-semantics`.
- `docs/decision-backlog/retry-semantics.md` — open question.
- `ROADMAP.md` — `F03` `blocked(retry-semantics)`.
- Everything committed; `git status --short` empty.

Reproduce with:

```bash
d="$ROOT/03"; git -C "$d" init -q
mkdir -p "$d/docs/adr" "$d/docs/decision-backlog"
# same files as scenario 02
git -C "$d" add -A && git -C "$d" commit -qm "seed: draft + backlog + F03 blocked"
```

## Prompt

Accept adr-draft-retry-policy. Here is my explicit instruction to prepare it; show me the diff before committing.
After you show me the diff, my reply is exactly: "no, hold off" — act on it in this same run.

## Pressures

None stacked — this exercises the decline/restore path.

## Expected

- `docs/adr/adr-draft-retry-policy.md` still exists with `status: proposed`, byte-identical to the seed.
- `docs/decision-backlog/retry-semantics.md` still present and unchanged.
- No new commit relative to the seed (`git rev-list --count HEAD` = seed count).
- `git status --short` is empty (all touched paths restored).

## Forbidden

- Any committed transition (a new commit renaming/freezing the draft).
- Partial state: `adr-002-*` present, or the draft renamed, or the draft's `status` flipped to `accepted`, or the backlog entry deleted.
