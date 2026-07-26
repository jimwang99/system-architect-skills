---
skill: write-prd
type: application
tier: 2
---

## Setup

A single-PRD project whose highest requirement ID is already tombstoned, exercising the allocation rule "New IDs are assigned as max(live ∪ retired) + 1 — retiring the highest ID therefore never frees it" (spec 03, PRD File Grammar).

- Bootstrapped `AGENTS.md`/`CLAUDE.md`.
- `docs/prd/prd-001-search.md`: live `REQ-002` and `REQ-004`; `- Retired: REQ-001, REQ-003`. So max(live ∪ retired) = 4. This is the `good/retired` validator fixture body; it passes `validate_prd.py`.
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

- Retired: REQ-001, REQ-003

### REQ-002 — Keyword search

- Statement: A user can search products by keyword and see matching results.
- Acceptance:
  - A query returns products whose title or description contains the keyword.
  - An empty result set shows a zero-results message.

### REQ-004 — Search analytics

- Statement: Each search query is logged for analytics.
- Acceptance:
  - Every search query is written to the analytics event stream.
  - The event includes the keyword and result count.
EOF

git -C "$d" add -A && git -C "$d" commit -qm "seed: prd-001 search, REQ-001/REQ-003 tombstoned"
```

## Prompt

Add a requirement to prd-001-search: users can sort search results by price, ascending or descending. When sorting by price ascending the lowest-priced product appears first; toggling to descending reverses the order. Add it.

## Pressures

Pragmatism (the tombstone list looks like dead history; the obvious "next" number is REQ-004+1 or the freed-looking REQ-003).

## Expected

- The new requirement's heading is `### REQ-005 — <title>` — max(live {REQ-002, REQ-004} ∪ retired {REQ-001, REQ-003}) + 1 = REQ-005.
- `docs/prd/prd-001-search.md` passes `python3 write-prd/scripts/validate_prd.py docs/prd/prd-001-search.md` (exit 0), which confirms live IDs unique and ascending, retired list intact, live ∪ retired = REQ-001..REQ-005 contiguous and disjoint.
- The `- Retired: REQ-001, REQ-003` line is unchanged.

## Forbidden

- Any tombstoned ID (`REQ-001` or `REQ-003`) reappearing as a live requirement heading.
- The new requirement numbered `REQ-004` (collision with the existing live requirement) or any ID ≤ `REQ-004`.
- Removing or editing `REQ-002` or `REQ-004`, or altering the `Retired` line.
