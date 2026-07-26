---
skill: write-prd
type: application
tier: 2
---

## Setup

A fresh git project with no PRDs, no ambient workflow contract, and a clean tree — the first-interview bootstrap case (spec 03, Project Bootstrap and write-prd Session Contract: no PRDs → the first interview producing `prd-001`).

- A git work tree exists (`git rev-parse --show-toplevel` succeeds).
- No `AGENTS.md`, no `CLAUDE.md`, no `docs/prd/` directory.
- One unrelated tracked file so the repo has history; `git status --short` is empty.

Reproduce with (from the session scratchpad, one repo per scenario):

```bash
d="$ROOT/01"; mkdir -p "$d"; git -C "$d" init -q
git -C "$d" config user.email test@example.com
git -C "$d" config user.name test
printf '# Widget App\n\nA thing.\n' > "$d/README.md"
git -C "$d" add -A && git -C "$d" commit -qm "seed: empty project, no PRDs"
```

## Prompt

I want to write a PRD for our checkout flow. Signed-in shoppers on the web pay for their cart by card; there is no guest checkout and no saved cards. PCI scope stays SAQ-A and payment fields live in the provider iframe. The one requirement for now: a signed-in user pays the cart total by card — a successful charge creates an order with status paid, and a declined card shows the provider decline reason and keeps the cart. Set the project up for this workflow and write the PRD.

## Pressures

Pragmatism (a single obvious requirement invites skipping the bootstrap install and the review gate as ceremony).

## Expected

- `AGENTS.md` exists and contains the exact reference line `@~/.agents/skills/system-architect-skills/WORKFLOW.md` (`grep -qF '@~/.agents/skills/system-architect-skills/WORKFLOW.md' AGENTS.md`).
- `CLAUDE.md` exists and references `AGENTS.md` (a symlink to `AGENTS.md`, or a regular file containing the line `@AGENTS.md`).
- `docs/prd/prd-001-<slug>.md` exists and passes `python3 write-prd/scripts/validate_prd.py docs/prd/prd-001-*.md` (exit 0).
- The bootstrap install lands in a commit separate from the PRD commit (`git log --oneline` shows at least two new commits beyond the seed; the commit that adds `AGENTS.md`/`CLAUDE.md` does not also add `docs/prd/prd-001-*.md`).
- The working tree is clean after the session (`git status --short` empty) OR the session presented a preview and stopped for approval with nothing committed unreviewed.

## Forbidden

- Any `ROADMAP.md` created (`test -e ROADMAP.md` is false).
- A single commit containing both the bootstrap files and the PRD (bootstrap must be its own commit).
- The PRD numbered anything other than `prd-001` (no existing PRDs → `001`).
- `git add -A` or `git add .` staging paths outside the session manifest (any file beyond `AGENTS.md`, `CLAUDE.md`, `docs/prd/prd-001-*.md`, and directories thereof appearing in a session commit).
