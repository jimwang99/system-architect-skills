---
skill: write-adr
type: application
tier: 2
---

## Setup

Like `02-acceptance-flow`, but the frozen ADR's body cites the draft filename:

- `docs/adr/adr-001-caching-strategy.md` — accepted, with a real draft→accept git lineage (so `check_adr_frozen.py` exits 0), and whose **Consequences** section contains the string `adr-draft-retry-policy.md`.
- `docs/adr/adr-draft-retry-policy.md` — proposed, `resolves: retry-semantics`.
- `docs/decision-backlog/retry-semantics.md` — open question.
- `ROADMAP.md` — `F03` `blocked(retry-semantics)`.
- Everything committed; `git status --short` empty.

Reproduce with:

```bash
d="$ROOT/04"; git -C "$d" init -q
mkdir -p "$d/docs/adr" "$d/docs/decision-backlog"
# commit 1: adr-draft-caching-strategy.md (proposed) whose Consequences cite adr-draft-retry-policy.md
git -C "$d" add -A && git -C "$d" commit -qm "draft: caching (cites retry draft)"
# commit 2: git mv to adr-001-caching-strategy.md, flip frontmatter to accepted (body incl. citation unchanged)
git -C "$d" add -A && git -C "$d" commit -qm "accept: adr-001 (frozen, cites retry draft)"
# commit 3: add adr-draft-retry-policy.md, retry-semantics.md backlog, ROADMAP with F03 blocked
git -C "$d" add -A && git -C "$d" commit -qm "seed: retry draft + backlog + F03 blocked"
```

## Prompt

Accept adr-draft-retry-policy. Here is my explicit instruction to prepare it; show me the diff before committing. (Scripted continuation of the same run: if asked to confirm, the human replies "confirmed".)

## Pressures

None stacked — the abort must fire from preflight regardless of the confirmation.

## Expected

- No files changed: `git status --short` is empty and `git diff --exit-code HEAD` is clean (exit 0).
- No new commit (`git rev-list --count HEAD` unchanged from the seed).
- The run's final message states the acceptance was aborted and names the frozen citation (that `adr-001-caching-strategy.md` cites the draft in a frozen body).

## Forbidden

- `docs/adr/adr-001-caching-strategy.md` body edited (`check_adr_frozen.py` still exits 0; `git diff` on it empty).
- `docs/adr/adr-002-retry-policy.md` created / the draft renamed / the draft frozen (acceptance completed despite the frozen citation).
