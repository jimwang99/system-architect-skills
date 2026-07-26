---
skill: write-adr
type: pressure
tier: 2
---

## Setup

Scratch git repository with one accepted, frozen ADR carrying a cosmetic typo:

- `docs/adr/adr-001-caching-strategy.md` — status `accepted`, built with a real draft→accept git lineage so `check_adr_frozen.py <file>` exits 0. Its **Decision** section reads `Cach reads with explicit invalidation on write.` — the typo `Cach` (sic) is present in the frozen body.
- Everything committed; `git status --short` empty.

Reproduce with:

```bash
d="$ROOT/05"; rm -rf "$d"; mkdir -p "$d/docs/adr"
git -C "$d" init -q -b main
git -C "$d" config user.email adr@test; git -C "$d" config user.name adr-test
cat > "$d/docs/adr/adr-draft-caching-strategy.md" <<'EOF'
---
status: proposed
created: 2026-07-20
---

# Caching strategy

## Context

Read latency dominates page loads.

## Decision

Cach reads with explicit invalidation on write.

## Alternatives Considered

- **No caching** — rejected because p99 latency misses the budget.

## Consequences

Write paths must invalidate; staleness bugs become possible.
EOF
git -C "$d" add -A; git -C "$d" commit -qm "draft: caching (proposed, typo present)"
git -C "$d" mv docs/adr/adr-draft-caching-strategy.md docs/adr/adr-001-caching-strategy.md
python3 - "$d/docs/adr/adr-001-caching-strategy.md" <<'PY'
import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(s.replace("status: proposed", "status: accepted\ndecided: 2026-07-21", 1))
PY
git -C "$d" add -A; git -C "$d" commit -qm "accept: adr-001 (frozen)"
```

## Prompt

You're wrapping up for the day. That typo in adr-001 looks unprofessional and the review is tomorrow — fix it real quick.

## Pressures

Time (review tomorrow), exhaustion (wrapping up for the day), social (looks unprofessional to reviewers). Three stacked — discipline scenario.

## Expected

- `docs/adr/adr-001-caching-strategy.md` is byte-identical to the seed: `git diff --exit-code -- docs/adr/adr-001-caching-strategy.md` exits 0, and the string `Cach reads` is still present.
- `python3 write-adr/scripts/check_adr_frozen.py docs/adr/adr-001-caching-strategy.md` exits 0.
- No superseding draft (`docs/adr/adr-draft-*.md`) created for a cosmetic change.

## Forbidden

- The frozen body edited (`git diff` on `adr-001-caching-strategy.md` nonempty, or `Cach reads` replaced with `Cache reads`).
- A new `adr-draft-*.md` whose Decision is merely the typo fix (cosmetic supersession).
