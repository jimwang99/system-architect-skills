---
name: write-adr
description: Use when recording an architectural decision or a rejection rationale, superseding a prior decision, hitting an architectural "how" choice mid-feature, or when another skill or session offers to record an architectural decision
---

# Write ADR

## Overview

**ADRs own the "why".** PRDs hold the what; the backlog holds the undecided. Anyone can write a draft; only a human can freeze one.

Why frozen: old records explain existing artifacts; a changed mind becomes a new superseding record; rejections stop the same debate restarting; stable numbers keep citations from rotting.

## Files

All ADRs live in `docs/adr/`. Slugs are kebab-case.

| Filename | Status |
|---|---|
| `adr-draft-<slug>.md` | proposed |
| `adr-NNN-<slug>.md` | accepted or superseded |
| `adr-rejected-<slug>.md` | rejected |

Frontmatter is line-oriented `key: value` between `---` delimiters — keys: `status`, `created`, `decided` (frozen only), optional `resolves`, `supersedes`, `superseded-by`; extensions need an `x-` prefix. Body: `# <title>`, then `## Context`, `## Decision`, `## Alternatives Considered` (every bullet `- **<alt>** — rejected because <reason>`, or `- None — <reason>`), `## Consequences` — all non-empty.

After writing or editing any ADR: `python3 <this-skill-dir>/../test-workflow/validators/validate_adr.py <file>` must exit 0. Before claiming a frozen file untouched: `python3 <this-skill-dir>/../test-workflow/validators/check_adr_frozen.py <file>`.

## Drafting (anyone, anytime)

1. Create `docs/adr/adr-draft-<slug>.md` with `status: proposed`, `created: <today>`, the four sections filled — real alternatives with real rejection reasons, not padding.
2. If it answers a backlog question, add `resolves: <backlog-slug>`. If it would replace an accepted ADR, add `supersedes: <that file>` — the target stays accepted until a human accepts your draft.
3. Run the validator. Continue your feature (reversible) or block on the backlog entry (irreversible) per the escalation rule. Your role ends at presenting the draft — `adr-draft-*`, `proposed`, never a numbered/`accepted` neighbor's shape.

## Accept / Reject (human authorizes; you may only execute)

Two authorizations, always: the human's explicit instruction naming the draft authorizes *preparing*; the human's approval of the diff authorizes *committing*. Status changes only at the commit — a renamed, `accepted`, backlog-deleted working tree is the forbidden partial state whether or not committed.

**Preflight — stop with a clear error and zero changes if any check fails:**
- draft exists, `status: proposed`, validator-clean
- destination name and number are free (number = max existing + 1; numbers are never reused; numbered ADRs are never deleted or renamed)
- `resolves:` target exists in `docs/decision-backlog/`
- `supersedes:` target exists and is `accepted`
- no unrelated uncommitted changes on paths you touch
- reference scan on the draft filename: hits in mutable artifacts (ROADMAP, plans, backlog, proposed ADR bodies) get repointed; a hit inside a frozen ADR body aborts the WHOLE acceptance — zero changes, report which frozen file cites the draft, stop. The rename manufactures a dangling link inside that frozen body; living with it is the human's call.

**Prepare (uncommitted):** `git mv` to `adr-NNN-<slug>.md` (accept) or `adr-rejected-<slug>.md` (reject); set `status` and `decided`; on accept, `git rm` the resolved backlog entry — never rewrite it into a "resolved" tombstone; flip a superseded target's frontmatter only (`status: superseded`, `superseded-by`); repoint the mutable references. ROADMAP stays byte-identical — unblocking is the owner's call; the preview and report name each feature still `blocked(<slug>)` on the resolved slug.

**Preview → confirm → one commit.** Show the complete diff. When the reply is already scripted in the instruction, the SAME message that shows the diff also executes it: quote the scripted reply, then commit (scripted approval) or restore (scripted decline) before the message ends — ending a message with the transition staged and "awaiting confirmation" is itself the violation. Otherwise commit only on explicit approval; on decline restore exactly the paths you touched so `git status` is clean. Rejection never touches the backlog — the question is still open.

## Iron rules

1. **Frozen bodies are frozen.** Accepted, rejected, and superseded bodies never change — not for typos (typos stand), not via "small cleanups", not to repoint a dangling citation (dangling links in frozen bodies are expected). The only legal post-freeze edit is supersession's two frontmatter keys, inside a successor's acceptance. Supersession means the decision changed, never cosmetics.
2. **No self-acceptance.** No human instruction in this session naming the draft = no accept, no reject, no number, no rename. Leaving a draft `proposed` is the correct state, not a "lying" repo to reconcile.

## Rationalizations

| Excuse | Reality |
|---|---|
| "It's just a typo fix" | Frozen means frozen. Typos stand. |
| "The human clearly wants this accepted" / "the whole setup exists to get this ratified" | Wanting is not instructing. Present the draft and stop. |
| "I'll assign the number now to save a round trip" / "matching the existing ADR conventions" | Numbers exist only past the human gate; a numbered neighbor is not permission. |
| "Everyone already agreed in standup" / "I named the social pressure, so I can proceed" | Claimed consensus — named or not — is not an instruction in this session. |
| "Frontmatter edits are allowed anyway" | Only supersession's two keys, only inside a successor's acceptance. |
| "I didn't commit, so it's safe" | The gate is the human's authorization, not the commit. A prepared uncommitted transition is the forbidden partial state. |
| "Broken links are worse than editing a frozen body" / "I'll accept anyway and just not touch the frozen body" | The frozen-citation hit aborts the whole acceptance, not merely the repoint. Zero changes; name the frozen citer; stop. |
| "Kept the question as a resolved tombstone for the trace" | On accept the backlog entry is `git rm`'d; git history is the trace. |
| "Leaving it proposed leaves the repo in a lying state" | `proposed` is the honest state until a human accepts. Consistency is not authorization. |
| "I'll flip ROADMAP blocked→ready since the blocker's resolved" | ROADMAP status is the owner's call. Name the still-blocked feature in your report instead. |
| "Awaiting your approval to commit" (reply scripted in the instruction) | The scripted reply is the decision, already delivered — act on it this run. |

## Red flags — STOP

- About to `git mv` an `adr-draft-*` file without a human instruction from this session naming it
- About to edit anything below the closing `---` of an accepted, rejected, or superseded ADR — including to repoint a citation
- About to proceed with any part of an acceptance after the reference scan hit a frozen ADR body
- About to delete a numbered ADR, reuse a number, or rewrite a resolved backlog entry instead of `git rm`-ing it
- About to change any ROADMAP feature's status as part of a transition
- About to leave a prepared, uncommitted transition and call it safe because it's uncommitted
- About to end a message with a staged transition and no commit while the instruction already scripted the reply
