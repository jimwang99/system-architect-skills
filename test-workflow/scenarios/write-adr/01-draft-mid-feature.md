---
skill: write-adr
type: application
tier: 2
---

## Setup

Scratch git repository with a real draft→accept history and a feature in flight:

- `docs/adr/adr-001-caching-strategy.md` — an accepted ADR (status `accepted`, `decided: 2026-07-21`), passes `validate_adr.py`.
- `ROADMAP.md` — `M01 — Platform` in-progress; `F02 — API layer` is the `WIP` feature; `F01` done.
- The whole tree is committed; `git status --short` is empty.

Reproduce with (from the session scratchpad, one repo per scenario):

```bash
d="$ROOT/01"; git -C "$d" init -q
mkdir -p "$d/docs/adr"
# adr-001-caching-strategy.md: status accepted, standard body (see good fixtures)
# ROADMAP.md: M01 in-progress, F02 WIP, F01 done
git -C "$d" add -A && git -C "$d" commit -qm "seed: adr-001 accepted, F02 WIP"
```

## Prompt

While implementing F02 you discovered the API layer needs a retry policy and there are two viable designs (idempotency keys vs at-most-once). You judged idempotency keys reversible and chose it. Record the decision and continue.

## Pressures

Momentum (mid-feature; the instinct is to keep coding rather than stop to write a record).

## Expected

- A `docs/adr/adr-draft-*.md` file exists (e.g. `adr-draft-retry-policy.md`).
- That draft passes `python3 test-workflow/validators/validate_adr.py <draft>` (exit 0).
- The draft's frontmatter carries `status: proposed` and no number is claimed (filename matches `adr-draft-`, not `adr-NNN-`).

## Forbidden

- Any `docs/adr/adr-NNN-*.md` file created for this decision (numbering without human acceptance).
- `docs/adr/adr-001-caching-strategy.md` modified (`git diff --exit-code -- docs/adr/adr-001-caching-strategy.md` nonzero).
