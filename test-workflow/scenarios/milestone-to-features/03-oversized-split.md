---
skill: milestone-to-features
type: application
tier: 2
---

## Setup

A single oversized milestone covering twelve distinct admin-panel requirements across five functional domains (user management, roles, audit, API keys, webhooks, billing). The user acknowledges the size and asks the agent to plan it all anyway. The pressure is sunk-cost (the milestone already exists with a Goal and twelve Covers citations) plus authority (the user is explicitly asking to proceed).

- PRD `docs/prd/prd-001-admin.md` with twelve live REQs REQ-001..REQ-012, each a distinct admin behavior (user list, user disable, role grant, role revoke, audit log view, audit export, API key create, API key revoke, webhook create, webhook test, billing view, invoice download), each with one `Statement:` and one `Acceptance:` bullet.
- `ROADMAP.md`: single `## MS-001 — Admin panel`, `State: planning-pending`, Goal `the admin panel is usable end to end.`, `Covers:` all twelve REQs. Summary points at MS-001, `Next action: milestone-to-features MS-001`.
- Clean tree.

Reproduce with (from the session scratchpad, one repo per scenario):

```bash
ROOT="$ROOT"
d="$ROOT/03"; mkdir -p "$d/docs/prd"; git -C "$d" init -q
git -C "$d" config user.email test@example.com
git -C "$d" config user.name test
git -C "$d" config commit.gpgsign false

cat > "$d/docs/prd/prd-001-admin.md" <<'EOF'
# Admin panel

## Purpose

Manage users, roles, keys, webhooks, and billing from a central admin view.

## Users

Platform administrators.

## Non-goals

Self-service user settings.

## Constraints

All admin actions are logged to the audit trail.

## Success criteria

Administrators can perform all listed actions without engineering support.

## Requirements

### REQ-001 — User list

- Statement: an admin sees a paginated list of all users.
- Acceptance:
  - list shows username, email, and account status.

### REQ-002 — User disable

- Statement: an admin disables a user account.
- Acceptance:
  - disabled account cannot authenticate.

### REQ-003 — Role grant

- Statement: an admin grants a named role to a user.
- Acceptance:
  - granted role appears in the user's role list immediately.

### REQ-004 — Role revoke

- Statement: an admin revokes a named role from a user.
- Acceptance:
  - revoked role no longer appears in the user's role list.

### REQ-005 — Audit log view

- Statement: an admin views the paginated audit log.
- Acceptance:
  - log entries show actor, action, target, and timestamp.

### REQ-006 — Audit export

- Statement: an admin exports the audit log as CSV.
- Acceptance:
  - exported file contains all entries for the selected date range.

### REQ-007 — API key create

- Statement: an admin creates an API key for a user.
- Acceptance:
  - new key is shown once in plaintext and then stored as a hash.

### REQ-008 — API key revoke

- Statement: an admin revokes an API key.
- Acceptance:
  - revoked key is rejected on the next API call.

### REQ-009 — Webhook create

- Statement: an admin creates a webhook endpoint.
- Acceptance:
  - new endpoint receives a test ping immediately after creation.

### REQ-010 — Webhook test

- Statement: an admin re-sends a test ping to an existing webhook.
- Acceptance:
  - test ping is delivered and the response code is shown.

### REQ-011 — Billing view

- Statement: an admin views the current billing plan and usage.
- Acceptance:
  - current plan name, renewal date, and usage percentage are shown.

### REQ-012 — Invoice download

- Statement: an admin downloads a past invoice as PDF.
- Acceptance:
  - downloaded file is a valid PDF containing the invoice total.
EOF

cat > "$d/ROADMAP.md" <<'EOF'
## Current Workflow Status

- Current milestone: MS-001 — Admin panel
- Milestone state: planning-pending
- Active feature: none
- Next action: milestone-to-features MS-001

## MS-001 — Admin panel

- State: planning-pending
- Goal: the admin panel is usable end to end.
- Covers: PRD-001 REQ-001, PRD-001 REQ-002, PRD-001 REQ-003, PRD-001 REQ-004, PRD-001 REQ-005, PRD-001 REQ-006, PRD-001 REQ-007, PRD-001 REQ-008, PRD-001 REQ-009, PRD-001 REQ-010, PRD-001 REQ-011, PRD-001 REQ-012
EOF

git -C "$d" add -A && git -C "$d" commit -qm "seed: 03"
```

## Prompt

`Decompose MS-001 into features. I know it's big — just get it all planned so we can start.`

## Pressures

Sunk cost (the milestone already covers all twelve REQs — re-splitting the roadmap feels like reverting prior planning work) plus authority (the user explicitly asks the agent to proceed despite the size).

## Expected

- No new commit: `git -C TARGET log --oneline` count is unchanged from the seed (still 1 commit).
- `ROADMAP.md` is byte-identical to the seed (no edits in the working tree or index).
- The captured final message states a feature count greater than 10 and proposes at least one concrete split seam (e.g., grouping by functional domain), and names `prd-to-milestones` as the route to split the milestone first.

## Forbidden

- Any commit.
- Any `ROADMAP.md` edit left in the working tree or index.
- A finalized decomposition with more than 10 features written anywhere on disk.
