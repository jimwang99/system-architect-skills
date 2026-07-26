# Session Management

## Purpose

Provide durable authenticated sessions across API requests.

## Users

Signed-in users on web and mobile.

## Non-goals

No anonymous sessions. No federated SSO.

## Constraints

Tokens must not exceed 4 KB; sessions live in Redis only.

## Success criteria

Session renewal is measurable per release.

## Requirements

### REQ-001 — Issue session token

- Statement: The API issues a signed token on successful login.
- Rationale: keeps ops simple
- Acceptance:
  - A valid login returns a token with a configurable TTL.
  - The token is signed with the deployment key.

### REQ-002 — Refresh session token

- Statement: A valid token can be exchanged for a fresh token before expiry.
- Acceptance:
  - Exchanging a valid token returns a new token with a reset TTL.
  - Exchanging an expired token returns 401.

## Glossary

session: an authenticated context bound to a user identity.
