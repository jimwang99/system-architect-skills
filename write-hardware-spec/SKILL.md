---
name: write-hardware-spec
description: Create, update, review, or freeze architecture and microarchitecture specifications for RTL blocks. Use before RTL or testbench implementation when interfaces, protocols, timing, reset, state, or verification intent need an explicit contract; not for writing implementation code.
---

# Write Hardware Specification

## Outcome and Modes

Create a single source of truth for observable behavior and agreed implementation decisions before RTL and verification diverge.

Route by the user's request:

- **Create or update:** edit the specification, preserve unrelated decisions and stable IDs, then validate it.
- **Review:** inspect and report findings without editing unless the user separately asks for changes.
- **Finalize or freeze:** validate, run independent semantic review, resolve material findings, and obtain explicit user approval.
- **Handoff:** prepare RTL or testbench context only when the user explicitly requests implementation.

For an update, read the complete existing specification first. Preserve its valid layout, requirements, tests, IDs, and unrelated design decisions. Add IDs rather than renumbering them unless the user requests a migration.

Externally visible behavior and architecture trade-offs belong to the user. Resolve discoverable facts from available evidence, state safe assumptions, and ask one focused question when an unresolved choice changes the contract. Never invent behavior to complete a document.

## 1. Choose the Document Boundary

The user's path and repository convention take priority. For a new block with no convention, use:

```text
spec/<block>_spec.md   # merged architecture and microarchitecture
spec/<block>_arch.md   # observable architecture
spec/<block>_uarch.md  # implementation decisions and test plan
```

Use a merged document when the observable contract and implementation remain easy to review together. Split architecture from microarchitecture when pipeline, state, sub-block, or interface detail would obscure the external contract or the documents have different readers. Preserve an existing valid layout; propose a migration before changing file boundaries.

In split format, define externally observable requirements only in the architecture document. The microarchitecture references architecture IDs and must not redefine them. In merged format, place these sections under a REQUIRED `Implementation Detail` heading.

## 2. Architecture Contract

The architecture defines what the block does. Include:

1. **Purpose and scope:** operating context, ownership boundary, and non-goals.
2. **Parameters:** type, default, meaning, legal range, derived status, dependent constraints, and illegal combinations.
3. **Interfaces:** every port's direction, width, clock/reset domain, grouping, protocol role, and meaningful-valid condition.
4. **Functional requirements:** independently testable `FR-xx` definitions for externally visible behavior, including ordering, conservation, boundary conditions, simultaneous events, backpressure, cancellation, errors, and recovery.
5. **Timing requirements:** measurable `TR-xx` definitions for latency, throughput, path constraints, stalls, replay, flush, and reset recovery.
6. **Reset-visible behavior:** interface values, transfer rules during reset, deassertion assumptions, discarded state, and first permitted post-reset transfer.
7. **Block diagram:** a small Mermaid diagram followed by plain-language explanations.

Keep internal registers, state encodings, pipeline registers, and private implementation structure out of the architecture document.

## 3. Microarchitecture Contract

The microarchitecture or merged implementation detail defines how the contract is met. Include:

1. **Block diagram and sub-blocks:** real signal flow, each unit's function, inputs, outputs, state, and ownership.
2. **Internal signals and storage:** names, widths, kinds, owners, and purpose where needed for implementation.
3. **Requirement mapping:** mechanism for every architecture `FR-xx` and `TR-xx`, without redefining them.
4. **Timing risks:** expected critical combinational paths, constraints, and safe mitigation; label estimates that require synthesis confirmation.
5. **Reset treatment:** reset value or an architectural-invisibility proof for every register, memory, and storage array.
6. **Verification plan:** the traceable tests, assertions, and coverage described below.

When applicable:

- **Pipeline:** define each stage, inter-stage state, advance condition, stalls, bubbles, replay, flush, and backpressure propagation.
- **FSM:** define states, transition conditions and priority, reset/flush behavior, outputs, and illegal-state handling. Give transitions stable `FSM-<NAME>-<NN>` IDs when they are part of the verification contract. Fix an encoding only when externally visible, safety-relevant, or intentionally constrained. Define recovery or assertion behavior for illegal state encodings.
- **Datapath:** define operand widths and signedness, equations, intermediate widths, truncation, rounding, saturation, and overflow.

## 4. Protocol, Timing, and Reset Semantics

For every channel, state the producer, consumer, sampling edge, transfer event, persistence, ordering, backpressure, and permitted combinational dependencies.

For valid/ready:

- The producer may assert valid independently of ready.
- Transfer occurs only when valid and ready are sampled high at the specified edge.
- After valid is asserted without transfer, the producer holds valid and payload stable while stalled.
- After transfer, the producer may present a new payload on the next cycle while valid remains high.
- The specification lists permitted and forbidden combinational paths and prevents interface loops.
- Flush, cancellation, reset, or retraction is an explicit requirement with priority and recovery behavior.

Define equally precise semantics for valid-only, request/acknowledge, credit, interrupt, memory-mapped, and other protocols. Avoid language that holds payload stable for every valid cycle because it forbids legal back-to-back transfers.

Every timing requirement must give measurable reference points: clock edge, start event, end event, exact cycles or rate, behavior under stalls and recovery, and owned path or frequency constraints.

For each state element, specify a reset value or prove that uninitialized contents cannot become architecturally visible before a valid overwrite. Define output validity during reset and the exact post-deassertion recovery interval.

Specify capacity and status invariants at every boundary. The implementation may use current state, next state, look-ahead, or registered status only if the chosen method cannot accept beyond capacity, lose an event, or violate the timing contract.

## 5. Test Plan and Traceability

Use stable IDs:

| Item | ID |
|------|----|
| Functional requirement | `FR-xx` |
| Timing requirement | `TR-xx` |
| Contracted FSM transition | `FSM-<NAME>-<NN>` |
| Test | `T-xx` |

Each ID has exactly one definition. References to an ID do not redefine it.

Require two-way traceability:

- Every `FR-xx` and `TR-xx` maps to at least one `T-xx`.
- Every `T-xx` maps on its definition row to one or more requirements.
- Each contracted FSM transition maps to a test, independently falsifiable assertion, or coverage target.
- Parameter boundaries and illegal combinations have a verification method when the tools can elaborate them.

Each test states mapped IDs, stimulus, expected observations, timing, and completion criteria. Cover reset during operation, back-to-back activity, boundary values, simultaneous events, stalls, flushes, and error recovery when applicable.

Assertions must be temporal or independently falsifiable. Reject an assertion that merely restates the assignment that constructs the checked signal, has an impossible antecedent, duplicates another property, or constrains legal behavior. State environment assumptions separately from DUT guarantees.

Coverage targets requirements, state and transition reachability, boundaries, concurrency, stalls, and recovery. Coverage is evidence of stimulus, not a substitute for checking behavior.

## 6. Diagrams and Authority

Use Mermaid for block diagrams and flow charts, followed by bullets that explain elements and direction. Keep each diagram focused and use real interface or internal names.

Use cycle-by-cycle tables for waveform timing, with one sampled cycle per column. Numbered requirements, tables, equations, and transition definitions are authoritative; diagrams explain them and must agree.

Every referenced local file exists.

## 7. Validate and Review

Run the bundled validator, resolving the script path from this skill directory:

```bash
uv run <skill-directory>/scripts/validate_spec.py <spec-file-or-spec-set> --format auto
```

A clean result is structural evidence only; it does not establish semantic hardware correctness.

Before freezing a new or substantively changed specification, dispatch an independent reviewer with every spec path and the absolute path to [references/review-checklist.md](references/review-checklist.md). The reviewer reads both completely and returns ranked findings without editing.

Resolve blocking findings. Important findings are resolved or explicitly accepted by the user. When a finding has one clear correction, recommend it with the trade-off; present alternatives only for a genuine user-owned decision. Rerun validation and semantic review after a substantive architecture, microarchitecture, or verification-contract change.

After review and revalidation, present the exact final spec paths and revision or content hashes, validation result, resolved decisions, and accepted findings. Then ask the user to approve that reviewed revision. An initial request to create or freeze a specification expresses intent, not approval of content that did not yet exist.

Set the specification to frozen only after that post-review approval. Any later substantive contract change invalidates the approval.

## 8. Conditional Handoff

Handoff occurs only when the user requests implementation from a frozen specification:

- Give RTL work the spec paths and target RTL path; require `write-hardware-rtl` when available.
- Give testbench work the same spec, complete test plan, and target testbench path; require `write-hardware-test-bench` when available.
- Keep the testbench derived from the specification rather than from RTL implementation choices.

RTL and testbench work may run in parallel because both consume the same frozen contract. Missing handoff capability blocks that implementation branch, not specification delivery.

## Completion Gate

For create or update, finish when the applicable architecture, microarchitecture, protocol, timing, reset, traceability, assertion, coverage, and Mermaid requirements are complete; every referenced file exists; no unresolved placeholder is presented as decided; and the validator passes.

For review, finish with ranked, evidence-backed findings and no unrequested edits. For finalize or freeze, also require independent semantic review, resolved or accepted material findings, and explicit user approval.

## References

- [references/templates.md](references/templates.md) — read when a copyable merged or split structure is useful.
- [references/example-spec.md](references/example-spec.md) — read when a complete merged example is useful.
- [references/review-checklist.md](references/review-checklist.md) — required for independent semantic review.
