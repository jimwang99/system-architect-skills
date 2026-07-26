---
name: act-learn-improve
description: Use when a significant work phase has finished and reality meaningfully diverged from the plan — especially when tests pass but specifications, assumptions, skills, or guidelines proved wrong or incomplete
---

# Act-Learn-Improve

## Overview

**Fixing the artifact is not learning.** Updating a wrong spec is a fix. Understanding *why* the spec was wrong and *what class of error* it represents is learning. This skill forces structured reflection before moving on.

The cycle: **Act** (do the work) -> **Learn** (write what reality taught you) -> **Improve** (list every affected target, each with a P0, P1, or P2 priority, for human approval). Applying the changes is a separate work phase.

**Each learning entry is one numbered file in `docs/learnings/` at the repository root: `ALI-001.md`, `ALI-002.md`, ...** Never write learnings anywhere else. Update every iteration: each work phase with a divergence adds the next-numbered file; each revision during review edits that same file.

## When to Use

```text
[Work phase completed]
          |
          v
<Meaningful divergence from plan?> -- no --> [Move on]
          |
         yes
          |
          v
[Create docs/learnings/ALI-NNN.md (next number)]
          |
          v
[Present to human partner] <----------------------------+
          |                                             |
          v                                             |
<Entry approved?> -- no --> [Revise the same ALI-NNN.md]+
          |
         yes
          |
          v
        [Done]
```

**Triggers (meaningful divergences only):**
- Implementation revealed wrong assumptions in the design
- Debugging uncovered root causes the spec did not anticipate
- Tests found gaps not in the original test plan
- A skill or guideline was incomplete or misleading
- Workarounds were needed that diverge from the documented approach
- You discovered something the next person would otherwise have to rediscover

**Do NOT use when:**
- The work went exactly as planned (no divergence)
- The only learnings are trivial typos or formatting

In doc-driven-workflow projects this fires at feature end (drafts travel with the feature's metadata commit) and drafts are approved at milestone review.

## Core Discipline: Separate Fix from Learn

**This is the #1 failure mode.** Agents naturally jump to "fix the spec, update the code, move on." That is necessary but not sufficient.

| Fix (necessary) | Learn (the actual goal) |
|-----------------|------------------------|
| Change config to use correct auth endpoint | "We assumed the auth URL from the old API docs. Lesson: external endpoint URLs must be verified against the live environment before design finalization." |
| Add retry logic for timeout errors | "The design assumed reliable network. Lesson: any external service call is an unreliable dependency — design must specify failure modes and retry policy." |
| Add missing test for concurrent access | "Race condition wasn't in test plan. Lesson: any shared-state operation needs test cases for concurrent and overlapping access patterns." |

The fix addresses THIS instance. The learning prevents THE CLASS of error.

## Writing the Learning File

After each work phase with a meaningful divergence:

1. List `docs/learnings/` at the repository root (create the directory if it does not exist). Find the highest existing `ALI-NNN.md` number; your file is the next one. The first file is `ALI-001.md`. Numbers are zero-padded to three digits. Never overwrite or reuse an existing number.
2. Write the file using the format below. One work phase = one file. Include `Status: draft`.
3. Present the file to your human partner. If they ask for changes, revise the same `ALI-NNN.md` in place — never a new file or a side document. Run the validator before presenting.

**The format below is not optional.** Writing a summary or an action list instead of the full format is the #2 failure mode (after conflating fix with learn). The structure forces depth; without it you get shallow bullets that miss the root cause and the class of error.

### File Format

```markdown
# ALI-NNN: [work phase description]
Date: [date]
Phase: [design | implementation | debugging | testing]
Status: draft | approved

**What happened:** [1-3 sentences: what was planned, what actually happened]

## L1: [short title]
- **What we assumed:** [the original assumption]
- **What is actually true:** [what reality showed]
- **Evidence:** [traceable reference — see below]
- **Why the assumption was wrong:** [root cause — missing info, wrong source, untested claim, ...]
- **Class of error:** [category — e.g. "unverified external dependency", "single-case generalization", "missing interaction test"]
- **Improvement items:** [check every target class; list every affected target, omit the rest]
  - **[P0 | P1 | P2] — [target class]:** `[artifact or path]` — [proposed change]

## L2: [short title]
...
```

**Evidence must be traceable:** a specific test name with its output, a command result, a log identifier, a `file:line`, a specification section, a published source, or a URL. If none exists, write the literal status **Evidence unavailable**, name what is missing, and state the verification needed before approval. Never invent a test, output, log, location, section, source, or URL.

**Status is a lifecycle field with an authority boundary.** You write `Status: draft` — always. Only a human-authorized review session (in doc-driven-workflow projects, `review-milestone`) changes it to `approved`. Conversational approval of the document does not authorize you to flip it, and neither does a P0 label. Before presenting the file, it must pass `python3 <this-skill-dir>/scripts/validate_learning.py <file>` (exit 0).

**Every improvement item starts with exactly one priority and one target class:** `**[P0 | P1 | P2] — [target class]:**`. Name the concrete artifact or path when known and state the proposed change. If one change touches several targets, split it into one item per target so each can be prioritized on its own.

### What Makes a Good Learning Entry

**Good:** Identifies the class of error and traces why the assumption existed
```
**Evidence:** Test `auth_endpoint_live_integration` output: `expected HTTP 200, got HTTP 404 for /v1/token` (CI run `1842`, log lines `310-318`).
**Class of error:** Unverified external dependency
**Why wrong:** Auth endpoint URL was copied from outdated API docs.
Never verified against the live environment before writing the integration.

**Improvement items:**
- **P0 — Source code:** `src/auth/client.ts` — read the endpoint from verified deployment configuration.
- **P1 — Project specification:** `docs/specs/authentication.md` — replace the obsolete endpoint and cite the live configuration source.
- **P2 — AI agent skill:** `skills/api-integration/SKILL.md` — refine the example to require endpoint verification.
```

**Bad:** Just describes what happened
```
The auth URL was wrong. Fixed it.
```

## Improvement Targets and Priorities

Before finalizing an entry, check every target class below. List every affected target; leave unaffected targets out — no `N/A` placeholders. If one proposed change spans several targets, split it into separate items.

| Priority | Meaning |
|----------|---------|
| **P0** | Highest-priority, must-have fix |
| **P1** | Should-have fix or improvement |
| **P2** | Nice-to-have improvement |

| Target class | Includes |
|--------------|----------|
| **Source code and delivery** | Source code, configuration, build, deployment, and infrastructure artifacts |
| **Design documents** | Architecture and design documents, diagrams, interfaces, constraints, and decisions |
| **Project and product documents** | Requirements, specifications, features, milestones, roadmaps, and plans |
| **Verification** | Tests, test plans, verification artifacts, models, fixtures, and verification infrastructure |
| **AI agent assets** | Skills, prompts, instructions, agents, tools, and agent configuration |
| **Engineering and operations** | Guidelines, processes, checklists, runbooks, monitoring, and operational documentation |
| **Other affected targets** | Any other artifact or workflow affected by the learning |

## Scope: Document Only

**Improve** means identifying and prioritizing changes for human approval. This skill writes the `ALI-NNN.md` file; it does not apply the changes. Applying them is a separate, human-approved work phase. Approval of the file approves the document only — it does not authorize the changes, and neither does a P0 label.

Each file should be concrete enough that someone can act on it later without extra context — but your job here is to write, not to fix.

## Red Flags — You're Skipping the Learning

- "Tests pass, let's move on" — passing tests do not mean you learned nothing
- "I already fixed the spec" — fixing is not learning (see table above)
- "I'll jot this down in a notes file for now" — learnings go in `docs/learnings/ALI-NNN.md`, nowhere else
- "The change was small, so the divergence was trivial" — size is not impact; what matters is whether the assumption or error class is meaningful
- "We don't have time" — skipping the write-up makes the same class of error easy to repeat and rediscover
- "I'll remember for next time" — you won't. The next agent definitely won't
- Listing action items without explaining why each matters
- "The human said it's approved, so I'll update Status" — approval is recorded by the review session, not by you

## Common Mistakes

**Shallow learnings** — "The spec was wrong" is not a learning. "The spec was wrong because we copied the endpoint from outdated docs without verifying against the live system" is a learning.

**Missing the class** — Every specific error belongs to a class. If you can't name the class, you haven't reflected enough. "Wrong auth URL" is an instance; "unverified external dependency" is the class.

**Scattered learnings** — Writing learnings into per-directory notes, commit messages, or ad-hoc files. There is exactly one place: the next `ALI-NNN.md` in `docs/learnings/`, updated every iteration.

**Wrong file number** — Overwriting an existing `ALI-NNN.md` or skipping numbers. New work phase = highest existing number + 1; revisions edit the file that already exists.

**Skipping skill/guideline improvement** — The easiest targets to overlook. If a skill led you astray or failed to warn you, that is a high-priority improvement.

**Over-scoping improvements** — The file identifies what to improve, not a full redesign. Keep improvements proportional to the learning.

**Incomplete target sweep** — Check every target class before finalizing. List all affected targets, not only the artifact that exposed the divergence.

**Detached or missing priority** — Give each improvement item exactly one P0, P1, or P2 label. A summary section cannot substitute for per-item priorities.

## Quick Reference

1. Work phase done; reality meaningfully diverged from the plan
2. STOP — do not just fix and move on
3. Create `docs/learnings/ALI-NNN.md` at the repo root, where NNN = highest existing number + 1 (first file: `ALI-001.md`)
4. For each divergence: assumption -> reality -> traceable evidence (or `Evidence unavailable` + gap + needed verification) -> why wrong -> class of error; Status: draft
5. Check every target class; list only the affected ones
6. Give each improvement item exactly one priority: P0 must-have / P1 should-have / P2 nice-to-have
7. Present to your human partner; revise the same `ALI-NNN.md` until approved
8. Neither file approval nor a P0 label authorizes applying the changes
9. Only a human-authorized review session flips Status to approved — never you.
