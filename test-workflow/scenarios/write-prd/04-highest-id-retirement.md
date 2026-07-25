---
skill: write-prd
type: application
tier: 2
---

## Setup

A single-PRD project whose highest requirement ID is already tombstoned, exercising the allocation rule "New IDs are assigned as max(live ∪ retired) + 1 — retiring the highest ID therefore never frees it" (spec 03, PRD File Grammar).

- Bootstrapped `AGENTS.md`/`CLAUDE.md`.
- `docs/prd/prd-001-search.md`: live `R-02` and `R-04`; `- Retired: R-01, R-03`. So max(live ∪ retired) = 4. This is the `good/retired` validator fixture body; it passes `validate_prd.py`.
- Clean tree.

Reproduce with (from the session scratchpad, one repo per scenario):

```bash
d="$ROOT/04"; mkdir -p "$d/docs/prd"; git -C "$d" init -q
git -C "$d" config user.email test@example.com
git -C "$d" config user.name test

cat > "$d/AGENTS.md" <<'EOF'
## Doc-driven workflow

Before any workflow task, read and follow
@~/.agents/skills/system-architect-skills/WORKFLOW.md.
EOF
printf '@AGENTS.md\n' > "$d/CLAUDE.md"

cat > "$d/docs/prd/prd-001-search.md" <<'EOF'
# Search

## Purpose

Let users find products by keyword.

## Users

Signed-in shoppers on web.

## Non-goals

No faceted filtering. No full-text ranking.

## Constraints

Latency under 500 ms at p99 for the catalogue size.

## Success criteria

Search CTR is measurable per release.

## Requirements

- Retired: R-01, R-03

### R-02 — Keyword search

- Statement: A user can search products by keyword and see matching results.
- Acceptance:
  - A query returns products whose title or description contains the keyword.
  - An empty result set shows a zero-results message.

### R-04 — Search analytics

- Statement: Each search query is logged for analytics.
- Acceptance:
  - Every search query is written to the analytics event stream.
  - The event includes the keyword and result count.
EOF

git -C "$d" add -A && git -C "$d" commit -qm "seed: prd-001 search, R-01/R-03 tombstoned"
```

## Prompt

Add a requirement to prd-001-search: users can sort search results by price, ascending or descending. When sorting by price ascending the lowest-priced product appears first; toggling to descending reverses the order. Add it.

## Pressures

Pragmatism (the tombstone list looks like dead history; the obvious "next" number is R-04+1 or the freed-looking R-03).

## Expected

- The new requirement's heading is `### R-05 — <title>` — max(live {R-02, R-04} ∪ retired {R-01, R-03}) + 1 = R-05.
- `docs/prd/prd-001-search.md` passes `python3 test-workflow/validators/validate_prd.py docs/prd/prd-001-search.md` (exit 0), which confirms live IDs unique and ascending, retired list intact, live ∪ retired = R-01..R-05 contiguous and disjoint.
- The `- Retired: R-01, R-03` line is unchanged.

## Forbidden

- Any tombstoned ID (`R-01` or `R-03`) reappearing as a live requirement heading.
- The new requirement numbered `R-04` (collision with the existing live requirement) or any ID ≤ `R-04`.
- Removing or editing `R-02` or `R-04`, or altering the `Retired` line.
