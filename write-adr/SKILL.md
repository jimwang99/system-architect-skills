---
name: write-adr
description: Use when recording an architectural decision or a rejection rationale, superseding a prior decision, hitting an architectural "how" choice mid-feature, or when another skill or session offers to record an architectural decision
---

# Write ADR

## Overview

**ADRs own the "why".** PRDs hold the what; the decision backlog holds the undecided. A decision worth recording gets a draft anyone can write and a frozen record only a human can authorize.

Why frozen records: old records explain existing artifacts; changing your mind is a new superseding record that carries the learning; rejected records stop the same debate from restarting; stable numbers keep citations from rotting.

## Files

All ADRs live in `docs/adr/`. Slugs are kebab-case.

| Filename | Status |
|---|---|
| `adr-draft-<slug>.md` | proposed |
| `adr-NNN-<slug>.md` | accepted or superseded |
| `adr-rejected-<slug>.md` | rejected |

Frontmatter is line-oriented `key: value` between `---` delimiters — keys: `status`, `created`, `decided` (frozen only), optional `resolves`, `supersedes`, `superseded-by`; extensions need an `x-` prefix. Body: `# <title>`, then `## Context`, `## Decision`, `## Alternatives Considered` (every bullet `- **<alt>** — rejected because <reason>`, or `- None — <reason>`), `## Consequences` — all non-empty.

After writing or editing any ADR, self-check it: `python3 <this-skill-dir>/../test-workflow/validators/validate_adr.py <file>` must exit 0.

## Drafting (anyone, anytime)

1. Create `docs/adr/adr-draft-<slug>.md` with `status: proposed`, `created: <today>`, the four sections filled — real alternatives with real rejection reasons, not padding.
2. If it answers a backlog question, add `resolves: <backlog-slug>`. If it would replace an accepted ADR, add `supersedes: <that file>` — the target stays accepted until a human accepts your draft.
3. Run the validator. Continue your feature (reversible decision) or block on the backlog entry (irreversible) per the escalation rule. Your role ends at presenting the draft — `adr-draft-*`, `proposed`, never a numbered/`accepted` neighbor's shape.

## Accept / Reject (human authorizes; you may only execute)

Two authorizations, always: the human's explicit instruction naming the draft authorizes *preparing*; the human's approval of the diff authorizes *committing*. Status changes only at the commit. Uncommitted is not safe — a renamed, `accepted`, backlog-deleted working tree is the forbidden partial state, committed or not.

**Preflight — stop with a clear error and zero changes if any check fails:**
- draft exists, `status: proposed`, validator-clean
- destination name and number are free (number = max existing + 1; numbers are never reused; numbered ADRs are never deleted or renamed)
- `resolves:` target exists in `docs/decision-backlog/`
- `supersedes:` target exists and is `accepted`
- no unrelated uncommitted changes on any path you will touch
- scan for references to the draft filename: hits in ROADMAP, plans, backlog, and proposed ADRs get repointed; a hit inside a frozen ADR body aborts — frozen bodies are never edited

**Prepare (uncommitted):** rename (`git mv`) to `adr-NNN-<slug>.md` (accept) or `adr-rejected-<slug>.md` (reject); set `status` and `decided`; on accept, `git rm` the resolved backlog entry (delete it — never rewrite it into a "resolved" tombstone); flip a superseded target's frontmatter only (`status: superseded`, `superseded-by`); repoint the mutable references. Leave every ROADMAP feature's status as-is — unblocking is the ROADMAP owner's call, not acceptance's.

**Preview → confirm → one commit.** One uninterrupted flow — never stop to "await confirmation" when the human's decision is already in front of you. A reply scripted inside the instruction itself ("after you show me the diff, my reply is: confirmed" / "no, hold off") IS that decision, already delivered — no later turn is coming; show the diff for the record, then act on the scripted reply in this same run. Show the complete diff. Commit only on explicit approval; on decline, restore exactly the paths you touched (draft, backlog, ROADMAP) so `git status` is clean. Rejection never touches the backlog — the question is still open.

## Iron rules

1. **Frozen bodies are frozen.** Accepted, rejected, and superseded bodies never change — not for typos (typos stand), not via "small cleanups", not to repoint a dangling citation (a dangling link in a frozen body is expected; editing the body is not). The only legal post-freeze edit is supersession's two frontmatter keys, inside a successor's acceptance. Supersession means the decision changed, never cosmetics.
2. **No self-acceptance.** No human instruction in this session naming the draft = no accept, no reject, no number, no rename. Consensus in a standup, an approving PRD, a sound decision, or urgency is not an instruction. Leaving a draft `proposed` is the correct state, not a "lying" repo to reconcile.

Verify a frozen file before claiming it untouched: `python3 <this-skill-dir>/../test-workflow/validators/check_adr_frozen.py <file>`.

## Rationalizations

| Excuse | Reality |
|---|---|
| "It's just a typo fix" | Frozen means frozen. Typos stand. |
| "The human clearly wants this accepted" | Wanting is not instructing. Present the draft and stop. |
| "I'll assign the number now to save a round trip" | Numbers exist only past the human gate. |
| "Everyone already agreed in standup" | Claimed consensus is not a named instruction in this session. |
| "Frontmatter edits are allowed anyway" | Only supersession's two keys, only inside a successor's acceptance. |
| "Matching the existing ADR conventions" | A numbered/`accepted` neighbor is not permission to self-number. A draft is `adr-draft-*`, `proposed`. |
| "I didn't commit, so it's safe" | The gate is the human's authorization, not the commit. A prepared uncommitted transition is the forbidden partial state. |
| "Broken links are worse than editing a frozen body" | A dangling citation in a frozen body is expected. Repoint mutable references only. |
| "Kept the question as a resolved tombstone for the trace" | On accept the backlog entry is `git rm`'d; git history is the trace. A rewritten "resolved" file is not deletion. |
| "Leaving it proposed leaves the repo in a lying state" | `proposed` is the honest state until a human accepts. Consistency is not authorization. |
| "The whole setup exists to get this ratified" | The setup exists to present a draft. Ratification is the human's move. |
| "I'll flip ROADMAP blocked→ready since the blocker's resolved" | ROADMAP status is the owner's call. Acceptance does not unblock. |
| "I named the social pressure, so I can proceed" | Naming pressure and yielding is still yielding. Named pressure is still not an instruction. |
| "Awaiting your approval to commit" (reply scripted in the instruction) | A scripted reply is the approval/decline, already delivered. Stopping after the diff ignores a decision you were handed. Commit on scripted approval, restore on scripted decline — this run. |

## Red flags — STOP

- About to `git mv` an `adr-draft-*` file without a human instruction from this session naming it
- About to edit anything below the closing `---` of an accepted, rejected, or superseded ADR
- About to edit a frozen ADR body to repoint a citation the rename would dangle
- About to delete a numbered ADR or reuse a number
- About to rewrite a resolved backlog file as a "resolved" tombstone instead of `git rm`-ing it
- About to change a ROADMAP feature's status (e.g. `blocked(<slug>)` → `ready`) as part of acceptance
- About to leave a prepared, uncommitted transition (renamed + `accepted` + backlog gone) and call it safe because it's uncommitted
- Stopping to "await confirmation" when the human's decision is already in front of you — including a reply scripted in the original instruction ("after the diff, my reply is: …"): that reply has already been given; act on it in this run (commit on approval, restore on decline)
- Drafting a "superseding" ADR whose only change is wording
