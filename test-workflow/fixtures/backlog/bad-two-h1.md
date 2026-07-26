# Should sessions survive server restart?

- Type: product
- Origin: F04 session-tokens, 2026-07-25

# Another question

## Context

Users lose carts on deploy; PRD prd-001 is silent on session durability, and F04 cannot pick a store without this answer.

## Options

- Sticky in-memory sessions.
- Redis-backed sessions.
