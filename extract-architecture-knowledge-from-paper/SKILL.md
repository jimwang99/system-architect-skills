---
name: extract-architecture-knowledge-from-paper
description: Use when asked to extract, distill, or mine design/architecture knowledge from an academic paper or publication (usually a PDF) into reusable documentation — "extract how X works from this paper", reproducing or implementing a published architecture, or when the primary reference for a design is a paper rather than a codebase.
---

# Extract Architecture Knowledge from Paper

## Overview

Same goal as `extract-architecture-knowledge-from-source`: produce a buildable spec from which a fresh session with no access to the reference can implement the design. But a paper is a *lossy* reference — ideas are abstract, engineering details are omitted as "obvious", and load-bearing information hides in figures. **Core principle: a paper is lossy compression of a design; extraction is decompression with provenance, never silent invention.**

**REQUIRED BACKGROUND:** `extract-architecture-knowledge-from-source`. Its Phase 1 spec (acceptance test, scope, baseline-vs-extensions, code tiers), Phase 2 ground rules, and Phase 3 doc verification apply unchanged. This skill adds what a paper reference demands on top.

## Phase 1 — Deep-read the paper, highest effort

- Read the PDF **page by page, every page** — never work from abstract + intro + conclusion. Figures, tables, captions, and footnotes are primary sources, not decoration.
- **Every architecture figure gets transcribed**: read it visually (the Read tool renders PDF pages for vision), enumerate blocks, arrows, labels, and bus widths, then redraw as ASCII art with an explanation list. Reconcile the figure against body text — a text/figure mismatch is a finding to record, not noise to skip.
- Tables and equations transcribe exactly; never paraphrase numbers from memory.
- Output of this phase is a **claims ledger**: one row per architectural or quantitative claim — claim, source (§ / Fig. / Table / Eq.), status ∈ {stated, derived, ambiguous, missing}. The ledger drives every later phase; a claim not in the ledger does not exist.

## Phase 2 — Close gaps; never assume

Work the ambiguous/missing rows through three channels, in order of authority:

1. **Artifact code.** Check for a linked repo (footnotes, artifact-evaluation badge, project page; search GitHub/Zenodo by paper title and author names). If found, download and analyze it — dispatch into `extract-architecture-knowledge-from-source` for that part. Code outranks prose for interfaces, widths, encodings, and corner cases.
2. **Cross-papers.** Fetch cited predecessors, follow-ups that cite this paper, and surveys covering the area. Cross-check mechanisms and numbers. A disagreement between papers is recorded with both citations, never silently resolved.
3. **Human.** Remaining ambiguous/missing rows go to the user as a decision table: claim, candidate interpretations, implication of each. Do not pick one yourself — ask, wait, record who decided.

Every claim in the final docs carries a provenance tag: `paper-stated` / `artifact-code` / `cross-paper` / `model-verified` / `human-decided`. A claim with no tag does not ship.

## Phase 3 — Verify by executable model

Quantitative and behavioral claims (throughput, latency, occupancy, hit rate, scheduling/arbitration behavior) must be checked by simulation before their doc counts as done:

- **Default: SimPy.** Processes + queues + resources cover throughput, contention, occupancy, and latency-distribution claims with minimal code.
- **Escalate to SystemC** only when the claim depends on cycle-level pipelining, bit-accurate datapaths, or interface handshakes that SimPy's abstraction cannot express.
- Run the model on the paper's own configuration and compare against the paper's reported numbers. Match → tag the claim `model-verified`. Mismatch → an unstated assumption exists; go back to Phase 2 to find it. Never tune the model until numbers agree without recording the assumption that made them agree.
- Keep the models in the doc set — they are part of the deliverable (golden reference for the eventual implementation).

## Phase 4 — Write the docs

All ground rules from the source-based skill apply (mechanism before artifact, ASCII block diagrams, quantitative behavior as tables, selective loading, essential-vs-incidental), with two substitutions:

- **Traceability targets:** paper claims cite § / Fig. / Table / Eq.; artifact claims cite `file:line`; verified numbers cite the model script + run.
- **Pitfalls section additionally covers omissions:** what the paper left unstated (reset, initialization, flow control, error paths, corner cases) and how each omission was resolved — with its provenance tag.

## Red flags — stop, go back a phase

| Thought | Reality |
|---------|---------|
| "The figure is just an illustration; the text covers it" | Figures carry dataflow and interfaces the text never states. Transcribe it. |
| "This detail is obvious; any reasonable choice works" | That is an *ambiguous* ledger row. Ask the human. |
| "The numbers are published; no need to model them" | Published ≠ reproducible from stated information. Modeling exposes unstated assumptions. |
| "The artifact code is messy/outdated; skip it" | Messy code still outranks clean prose for interfaces and corner cases. |
| "A follow-up paper describes it differently; the original wins" | Conflict is signal. Record both citations; resolve via model or human. |
| "SimPy is toy-like; start in SystemC" | Escalate only on the stated conditions. SimPy first buys iteration speed. |
