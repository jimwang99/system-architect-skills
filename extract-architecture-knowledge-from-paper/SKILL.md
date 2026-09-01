---
name: extract-architecture-knowledge-from-paper
description: Create a standalone, implementation-ready architecture specification when one academic paper is the primary design reference. Use for reimplementation documentation from a publication; not for paper summaries, literature surveys, or direct implementation.
---

# Extract Architecture Knowledge from Paper

## Outcome

Decompress a lossy publication into a self-contained design specification without silently inventing omitted engineering details. A fresh engineer or agent should be able to implement the in-scope design using the output while seeing which details are stated, derived, conflicting, or unknown. The deliverable is documentation, not implementation code.

The user's scope, format, and output path take priority. Keep downloaded papers, repositories, and temporary models outside the deliverable unless the user requests them.

## 1. Fix Scope and Source Identity

Record the exact paper title, authors, version or publication, retrieval date, and DOI or stable URL when available. For a supplied file without stable identity, record its filename and content hash. Define the requested subsystem, implementation target, acceptance test, and explicit exclusions.

Ask one concise question only when an unresolved boundary or user-owned design choice would materially change the extraction. Otherwise state the assumption and preserve uncertainty.

Scope is complete when every requested behavior and constraint has a destination in the document or an explicit exclusion.

## 2. Build the Claims Ledger

Inspect the complete supplied or accessible paper, including appendices and supplementary material. Record any inaccessible cited supplement. Deep-read every implementation-bearing section and every relevant figure, table, equation, caption, and footnote.

For each implementation-critical or quantitative claim, record:

- Claim and exact location: section, page, figure, table, equation, appendix, or `not stated`.
- Origin: paper, artifact, related publication, derivation, measurement, or user decision.
- Status: stated, derived with assumptions, conflicting, ambiguous, or missing.
- Validation method and result, kept separate from origin; use `not performed` when verification is outside scope or unavailable.

Transcribe exact numbers, units, widths, formulas, and configurations from the source. Reconcile figures with prose and equations. A mismatch is a ledger item, not a detail to smooth over.

## 3. Close Material Gaps

Use only the evidence channels needed by the requested scope:

1. **Linked artifact:** identify its exact revision and configuration. For a substantial code subtask, apply the source-extraction method when available. The artifact describes that revision; it does not silently override the paper.
2. **Related publications:** inspect cited predecessors, follow-ups, corrections, or evaluations when they can resolve a material mechanism or quantitative conflict.
3. **User decision:** ask when the remaining ambiguity changes correctness or requires a user-owned implementation choice. Record the decision as a decision, not as source provenance.

Keep unresolved alternatives visible when evidence cannot choose among them. State which omissions block implementation and which permit local design freedom.

At minimum, check for omitted interface semantics, widths and encodings, initialization and reset, flow control, arbitration, concurrency, error handling, corner cases, timing reference points, workload assumptions, and evaluation conditions when relevant.

## 4. Verify Proportionally

Match verification to the claim:

- Re-derive equations and unit conversions for analytical claims.
- Run existing artifact tests or reproduce published configurations when available and within scope.
- Build a focused executable model only when the user explicitly authorizes code or model creation, the claim is modelable from available information, and the model materially reduces implementation risk.

A model checks consistency under its recorded assumptions; it does not prove empirical performance or paper truth. Record inputs, configuration, randomness, expected result, actual result, and limitations. On mismatch, investigate artifact version, workload, model error, randomness, omitted assumptions, and source error without forcing agreement.

## 5. Write the Specification

Explain mechanisms before implementation artifacts. Preserve exact interfaces, dataflow, state, ordering, equations, timing, and corner behavior required by the acceptance test. Separate required behavior from one possible implementation.

Use Mermaid for block diagrams and flow charts that materially clarify structure or sequence, followed by plain-language explanations. Use tables for repeated fields, state transitions, timing, and comparable quantitative results.

Cite paper evidence by section, page, figure, table, or equation; artifact evidence by `path:line` at revision; verification evidence by model or test and recorded run. Put assumptions and unresolved omissions beside the affected mechanism.

## 6. Completion Gate

Finish only when:

- Every critical ledger row is supported, derived with explicit assumptions, conflicting, or explicitly unknown.
- Text, figures, equations, artifacts, and external evidence are reconciled or their disagreement is reported.
- A reader can recover the in-scope interfaces, behavior, timing, state, corner cases, and verification intent.
- Each material claim has separate origin, location, status, and validation.
- Generated models or adaptations are included only when they are part of the requested deliverable.
- The specification contains no silent invention or false claim of verification.
