---
name: act-learn-improve
description: Use when a significant work phase has finished and reality meaningfully diverged from the plan — especially when tests pass but specifications, assumptions, skills, or guidelines proved wrong or incomplete
---

# Act-Learn-Improve

## Overview

**Fixing the artifact is not learning.** Updating a wrong spec is a fix. Understanding *why* the spec was wrong and *what class of error* it represents is learning. This skill enforces the discipline of structured reflection before moving on.

The cycle is: **Act** (do the work) -> **Learn** (document what reality taught you) -> **Improve** (identify every affected target and assign each proposed change a P0, P1, or P2 priority for human approval). Applying those changes is a separate work phase.

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
[Create learning document]
          |
          v
[Present to human partner] <------------------------------+
          |                                               |
          v                                               |
<Learning document approved?> -- no --> [Revise document]-+
          |
         yes
          |
          v
        [Done]
```

**Triggers (meaningful divergences only):**
- Implementation revealed wrong assumptions in the design
- Debugging uncovered root causes not anticipated by the spec
- Tests found gaps not in the original test plan
- A skill or guideline was incomplete or misleading
- Workarounds were needed that diverge from the documented approach
- You discovered something that "the next person would have to rediscover"

**Do NOT use when:**
- Implementation went exactly as planned (no divergence)
- The only learnings are trivial typos or formatting

## Core Discipline: Separate Fix from Learn

**This is the #1 failure mode.** Agents naturally jump to "fix the spec, update the code, move on." That's necessary but not sufficient.

| Fix (necessary) | Learn (the actual goal) |
|-----------------|------------------------|
| Change config to use correct auth endpoint | "We assumed the auth URL from the old API docs. Lesson: external endpoint URLs must be verified against the live environment before design finalization." |
| Add retry logic for timeout errors | "The design assumed reliable network. Lesson: any external service call is an unreliable dependency — design must specify failure modes and retry policy." |
| Add missing test for concurrent access | "Race condition wasn't in test plan. Lesson: any shared-state operation needs test cases for concurrent and overlapping access patterns." |

The fix addresses THIS instance. The learning prevents THE CLASS of error.

## The Learning Document

After each significant work phase with a meaningful divergence, create a learning document (or append to an existing one in the working directory). Present it to your human partner for review.

**The structured format below is not optional.** Writing a summary or action list instead of the full format is the #2 failure mode (after conflating fix with learn). The structure forces depth — without it, you'll produce shallow bullet points that miss the root cause and class of error.

### Format

```markdown
# Learnings: [work phase description]
Date: [date]
Phase: [design | implementation | debugging | testing]

## What Happened
[1-3 sentences: what work was done, what was the plan vs reality]

## Learnings

### L1: [short title]
- **What we assumed:** [the original assumption]
- **What is actually true:** [what reality showed]
- **Evidence:** [one or more traceable references: specific test name and relevant output, command result, log identifier/span, file:line, specification section, published source, or URL; if none exists, write `Evidence unavailable`, name the gap, and state the needed verification]
- **Why the assumption was wrong:** [root cause — missing info, wrong source, untested claim, etc.]
- **Class of error:** [category — e.g., "unverified external dependency", "single-case generalization", "missing interaction test"]
- **Improvement items:** [evaluate every target class below; include every affected target and omit unaffected targets]
  - **[P0 | P1 | P2] — [target class]:** `[specific artifact or path]` — [proposed change]

### L2: [short title]
...
```

Evidence must be traceable. Cite at least one specific test and relevant output, command result, log identifier or span, `file:line`, specification section, published source, or URL. If none is available, write the literal status **Evidence unavailable**, state what is missing, and name the verification needed before document approval. Never invent a test, output, log, location, section, source, or URL.

Every improvement item must begin with exactly one priority and one target class: `**[P0 | P1 | P2] — [target class]:**`. Name the concrete artifact or path when known and state the proposed change. Split changes that affect multiple targets into separate items so each target can be prioritized independently. An unlabeled or multiply labeled item is structurally incomplete.

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

Before finalizing each learning entry, evaluate every target class below. Include every affected target and omit unaffected targets; do not add `N/A` placeholders. If one proposed change spans multiple targets, split it into separate improvement items.

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

In this cycle, **Improve** means identifying and prioritizing candidate artifact or process changes for human approval. This skill produces the learning document; it does **not** apply those changes. Applying them is a separate, human-approved work phase. Learning-document approval approves the document only; it does not authorize applying candidate changes.

A P0 label records highest importance; it is not authorization to apply the change.

The document should be concrete enough that someone can act on it later without needing additional context — but the agent's job here is to write, not to fix.

## Red Flags — You're Skipping the Learning

- "Tests pass, let's move on" — passing tests don't mean you learned nothing
- "I already fixed the spec" — fixing is not learning (see table above)
- "The change was small, so the divergence was trivial" — size is not impact; document it only when the underlying assumption or error class is meaningful
- "We don't have time" — skipping documentation makes the same class of error easier to repeat and rediscover
- "I'll remember for next time" — you won't. The next agent definitely won't
- Listing action items without explaining WHY each matters

## Common Mistakes

**Shallow learnings** — "The spec was wrong" is not a learning. "The spec was wrong because we copied the endpoint from outdated docs without verifying against the live system" is a learning.

**Missing the class** — Every specific error belongs to a class. If you can't name the class, you haven't reflected enough. "Wrong auth URL" is an instance; "unverified external dependency" is the class.

**Skipping skill/guideline improvement** — The easiest artifacts to overlook. If a skill led you astray or failed to warn you, that's a high-priority improvement.

**Over-scoping improvements** — The learning document identifies what to improve, not a full redesign. Keep improvements proportional to the learning.

**Incomplete target sweep** — Evaluate every target class before finalizing the document. List all affected targets, not only the artifact that exposed the divergence; omit unaffected targets instead of adding `N/A`.

**Detached or missing priority** — Put exactly one P0, P1, or P2 label on each improvement item. A separate summary cannot substitute for per-item priority, and P0 does not authorize implementation.

## Quick Reference

1. Work phase done, reality meaningfully diverged from plan
2. STOP — don't just fix and move on
3. Create learning document with structured entries
4. For each divergence: assumption -> reality -> traceable evidence (or `Evidence unavailable` + gap + needed verification) -> why wrong -> class of error
5. Evaluate every target class; list every affected target and omit unaffected targets
6. Assign each improvement item exactly one priority: P0 must-have / P1 should-have / P2 nice-to-have
7. Present to the human partner; if rejected, revise the learning document and present it again
8. Learning-document approval and P0 priority do not authorize applying candidate changes
