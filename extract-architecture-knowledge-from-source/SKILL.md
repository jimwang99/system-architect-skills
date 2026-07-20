---
name: extract-architecture-knowledge-from-source
description: Use when asked to extract, distill, or mine design/architecture knowledge from a reference codebase into reusable documentation — "extract how X is implemented", or when porting an architecture to another language/stack and the source repo won't be available later.
---

# Extract Architecture Knowledge

## Overview

Turn a reference implementation into a prescriptive knowledge base: a doc set from which a fresh session (LLM or engineer) with no repo access can produce a working implementation. **Core principle: the output is a buildable spec, not a code tour.**

Not for contributor onboarding (write an architecture README) or library API reference (standard docs).

## Phase 1 — Write the extraction spec first

Before deep-reading code, write and (if interactive) get approval on a short spec fixing:

- **Acceptance test** — the definition of done, measurable: "a fresh session given only these docs produces a working, verified implementation of X in <target language>."
- **Scope** — explicit in/out lists. Core concept in; host/platform integration (buses, build system, framework glue) out or survey-only.
- **Baseline vs extensions** — a canonical, simplified baseline presented first-class; repo-specific optimizations become named extensions, each with problem / technique / cost. Sorting rule: removing it breaks correctness of the core function → baseline; costs only performance, area, or generality → extension.
- **Code depth tiers** — complete code sketches in the target language (not the repo's source language) for the small critical modules; annotated fragments for assembly/plumbing. Code illustrates the design and need not compile or run — but interfaces (ports, widths, field layouts, encodings) transcribe exactly from the repo source, never paraphrased from memory. Snippets-as-evidence alone fail the acceptance test.
- **Code style source** — the user skills/guidelines covering the target language (e.g. `write-hardware-rtl` for SystemVerilog); all embedded example code follows them.
- **Verification plan** — how quantitative claims (timing, capacity, complexity) get checked, against the repo's own tests/simulation or cited publications, before a doc counts as done.

## Phase 2 — Extract, under these ground rules

1. **Mechanism before artifact** — explain each idea in implementation-neutral terms (registers, queues, invariants); quote repo code afterward as a labeled exhibit.
2. **Block diagrams as ASCII art** — every major structure gets one, with descriptive labels and an accompanying list of explanations. Break a complicated diagram into several focused ones (one concern each) rather than forcing everything into a single diagram.
3. **Two-level traceability** — repo-derived claims cite `file:line`; performance/trade-off claims cite publications. A quantitative claim with no published source (e.g. a magic constant): cite the code and mark it "re-derive for your design".
4. **Quantitative behavior as tables** — never prose: cycle-accurate tables, state walkthroughs, complexity bounds. Where a number encodes the reference's own pipeline/implementation choices, present the derivation (a formula in the reader's parameters), not the reference's constant.
5. **Mine hard-won lessons** — code comments, TODOs, oddly-defensive code, and the repo's own tests feed mandatory Pitfalls sections and a verification doc (golden model, staged checks, corner cases from the repo's tests).
6. **Selective loading** — each doc opens with what-it-covers plus prerequisites. README carries: index with load-when guidance per file, glossary, recommended implementation order. A reader must not need all files at once.
7. **Essential vs incidental** — each doc ends with universal design rules vs repo-specific choices a reimplementer may change (with the trade-off stated).

## Phase 3 — Verify the docs themselves

- Check every quantitative claim (timing tables, capacities, constants) against the repo's own tests/simulation output or the cited publication.
- Final gate: re-read the doc set as the acceptance-test reader. Any "implement this" doc missing interfaces, timing, or corner cases fails.
