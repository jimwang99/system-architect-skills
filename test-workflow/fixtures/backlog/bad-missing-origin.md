# Should sessions survive server restart?

- Type: product

## Context

Users lose carts on deploy; PRD-001 is silent on session durability, and FEAT-004 cannot pick a store without this answer.

## Options

- Sticky in-memory sessions.
- Redis-backed sessions.
