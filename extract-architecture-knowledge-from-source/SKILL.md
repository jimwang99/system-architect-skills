---
name: extract-architecture-knowledge-from-source
description: Create standalone, implementation-ready architecture documentation from a reference codebase for readers who will not have the source. Use when reusable reimplementation documentation is requested; not for codebase tours, API docs, or direct implementation.
---

# Extract Architecture Knowledge from Source

## Outcome

Produce a self-contained specification from which a fresh engineer or agent can reimplement and verify the requested design without access to the reference repository. Explain the mechanism, contract, invariants, and trade-offs; source excerpts are evidence, not the deliverable.

The user's scope, format, target language, and output path take priority. Default to one Markdown document. Split the result only when distinct readers or implementation stages benefit from selective loading.

Keep the reference repository read-only. Put temporary analysis artifacts outside it and create additional models or code only when the user explicitly authorizes them.

## 1. Fix Scope and Source Identity

Record the repository identity, relevant configuration, requested subsystem, intended reader, and acceptance test. Use an exact commit or tag when available. For a dirty or unversioned tree, record the base revision when present, dirty-state summary, and a tree, content, or snapshot hash that identifies the inspected bytes.

Define in-scope behavior and explicit exclusions. Ask one concise question only when a missing target, boundary, or externally visible choice would materially change the extraction.

Classify mechanisms against the user's required behavior and constraints:

- **Essential:** removing it breaks a required function or constraint.
- **Replaceable:** another mechanism may satisfy the same contract, with a stated trade-off.
- **Incidental:** repository integration or optimization outside the requested scope.

Scope is complete when every requested behavior and constraint has a destination in the planned document or an explicit exclusion.

## 2. Build a Coverage Ledger

Map each in-scope item to the source evidence needed to explain it:

- Interfaces, data formats, parameters, configuration, and error behavior.
- State, storage, invariants, algorithms, ordering, concurrency, and lifecycle.
- Timing, capacity, throughput, resource, or complexity claims when material.
- Tests, comments, issue history, and defensive code that expose corner cases or hard-won lessons.

For every material claim, record:

- Claim and exact source location as `path:line` at the recorded source identity.
- Origin: source, test, benchmark, publication, derivation, measurement, or inference.
- Status: supported, derived with assumptions, conflicting, or unresolved.
- Validation performed and its result.

File and line citations are traceability, not a substitute for enough explanation to reimplement the behavior.

## 3. Extract the Design

Explain each mechanism before showing any source exhibit. Preserve exact widths, encodings, layouts, event ordering, and boundary behavior when they are contractual. Separate the reference's choices from requirements a new implementation must preserve.

Use Mermaid for a block diagram or flow chart only when it makes structure or sequence clearer, and follow it with plain-language explanations. Use tables for repeated fields, cycle behavior, state transitions, and like-for-like comparisons.

Include target-language examples only when requested or when they materially remove ambiguity. Label exact source contracts separately from proposed target adaptations, and follow the target project's coding guidance.

For a multi-file result, give each file a clear purpose and prerequisite, plus one index that says when to read it. Avoid a multi-file hierarchy when one document remains usable.

## 4. Verify Proportionally

Use the reference's existing tests, build, simulations, benchmarks, or golden models when they directly check a conclusion-driving claim. Run write-producing tools in a disposable copy or redirect their outputs outside the reference tree. If isolation is unavailable, keep the repository unchanged and record the verification gap.

Record commands, configurations, inputs, expected results, actual results, and limitations. A test pass supports only the behavior it observes. Label claims that could not be verified rather than filling gaps with a plausible design.

## 5. Completion Gate

Finish only when:

- Every coverage-ledger item is documented, excluded, conflicting, or explicitly unresolved.
- A reader can recover interfaces, behavior, timing, state, corner cases, and verification intent required by the acceptance test.
- Every material repository-derived claim cites the recorded source identity and location.
- Derived and inferred claims state their assumptions; measured claims state their method.
- Reference-specific choices are distinguishable from requirements the new implementation must preserve.
- Diagrams, tables, prose, and examples agree.
- The output contains no silent invention or dependency on unavailable source material.
