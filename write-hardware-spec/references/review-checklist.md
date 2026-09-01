# Hardware Specification Independent Review Checklist

> **NON-NORMATIVE REFERENCE:** [`SKILL.md`](../SKILL.md) is the sole contract. This checklist challenges compliance and semantic correctness; it introduces no requirements of its own.

Read every specification file completely before reporting findings. Challenge the design rather than reconstructing or editing it. The user owns externally visible behavior and architecture decisions.

## Mechanical Preconditions

Confirm these before semantic review:

- The bundled `scripts/validate_spec.py` command completed successfully for the selected format.
- Every applicable required section exists.
- `FR-xx`, `TR-xx`, `FSM-<NAME>-<NN>`, and `T-xx` definitions are unique.
- Mechanical two-way traceability is complete.
- No unresolved decision marker or placeholder remains.
- Every block diagram and flow chart uses Mermaid with explanatory text, and every referenced file exists.

If a precondition fails, return a **blocking** mechanical finding with the command output and affected file/line. Continue semantic review when the defect does not prevent reliable interpretation; otherwise state exactly what could not be reviewed.

## Architecture Review

### Purpose and Scope

- Could two engineers read the purpose and build different blocks?
- Are operating context, ownership boundaries, clock/reset domains, and scope explicit?
- Do non-goals exclude plausible adjacent features without contradicting a requirement?

### Parameters

- Does every parameter have a type, default, legal range, and meaning?
- Are derived parameters marked as derived?
- Are illegal combinations excluded explicitly?
- Do minimum, maximum, non-power-of-two, and dependent-parameter cases have defined behavior where applicable?

### Interfaces

- Is every port present with direction, width, domain, and protocol role?
- Are reset, flush, cancellation, error, and status signals present when the requirements need them?
- Could a simpler interface satisfy the same externally visible requirements?
- Does the architecture avoid leaking internal register names, encodings, or structure?

### Functional Requirements

- Is every `FR-xx` independently testable from observable behavior?
- Do any two requirements contradict each other or a non-goal?
- Does each boundary choose one behavior for simultaneous events?
- Are ordering, conservation, backpressure, cancellation, error, and recovery behaviors complete?
- Does an update preserve unrelated existing requirements and IDs?

## Microarchitecture Review

### Requirement Implementation

- Does every architecture `FR-xx` and `TR-xx` map to a mechanism without being redefined?
- Can the described sub-blocks implement every observable requirement?
- Is any internal mechanism unnecessary or more complex than the requirement demands?
- Are widths, signedness, arithmetic overflow, truncation, rounding, and saturation complete where applicable?

### Pipelines

- Does every stage have named inter-stage registers and an exact advance condition?
- Is stall behavior hold/bubble/replay behavior unambiguous for every stage?
- Is flush priority and in-flight operation disposal explicit?
- Can backpressure lose, duplicate, reorder, or overwrite an operation?
- Does the stage diagram agree with the stage table?

### FSMs

- Does every transition have a stable `FSM-<NAME>-<NN>` ID?
- Are transition conditions exhaustive and mutually prioritized where they overlap?
- Are any states or transitions unreachable?
- Is behavior defined for illegal encodings, reset, stall, and flush?
- Do the state sketch, encoding table, transition table, and output behavior agree?

### State and Storage

- Does every register have a reset value?
- Does every unreset array or memory have a valid architectural-invisibility justification?
- Can uninitialized storage become visible through a pointer, valid bit, or speculative read?
- Are next-state equations complete for simultaneous events and boundaries?

## Protocol Review

For every channel:

- Are producer, consumer, sampling edge, and transfer event explicit?
- Can valid assert independently of ready, as required for valid/ready channels?
- Are valid and payload held only while stalled, allowing a new payload after a completed transfer?
- Are persistence rules equally precise for valid-only, ready-only, request/acknowledge, credit, interrupt, or memory-mapped protocols?
- Are backpressure and all permitted/forbidden combinational dependencies explicit?
- Could connected interfaces form a combinational loop?
- Are flush, cancellation, or retraction exceptions explicit `FR-xx` requirements with priority and recovery behavior?
- Does any output depend on an input in a way that contradicts the timing table?

## Timing and Reset Review

- Does every `TR-xx` quantify latency, throughput, path, or recovery behavior with clear start/end reference points?
- Are cycle columns and edge semantics consistent across prose and waveform tables?
- Are claimed registered outputs driven by dedicated registers rather than muxes of registered storage?
- Are allowed and forbidden combinational paths consistent with the microarchitecture?
- If ready, valid, full, empty, or another status is registered, is its D input derived from the correct next-state value rather than stale current state?
- Could a registered full/ready decision accept one transfer beyond capacity?
- Are reset assertion style, deassertion assumptions, interface behavior during reset, and recovery cycles mutually consistent?

## Traceability, Assertions, and Coverage Review

### Tests and two-way traceability

- Does every `FR-xx` and `TR-xx` have at least one meaningful `T-xx`?
- Does every contracted `FSM-<NAME>-<NN>` have a meaningful test, independently falsifiable assertion, or coverage target?
- Does every `T-xx` map back to a requirement or transition on its definition row?
- Does each test specify stimulus, observations, timing, and completion criteria?
- Do tests cover reset during operation, back-to-back activity, legal parameter boundaries, illegal combinations, simultaneous events, stalls, and flushes when applicable?
- Could all mapped tests pass while the requirement is still violated?

### Assertions

- Is each assertion temporal or independently falsifiable?
- Does any assertion merely restate the assignment that constructs its checked signal?
- Is any antecedent impossible under legal assumptions or the same gating expression?
- Is any assertion already implied entirely by another assertion?
- Are environment assumptions separated from DUT assertions and justified?

### Coverage

- Does coverage target meaningful requirements, states, transitions, boundaries, concurrency, stalls, and recovery?
- Are coverage points reachable under legal assumptions?
- Is coverage being mistaken for a behavioral check?

## Diagram Review

- Do all block diagrams and flow charts use Mermaid and remain readable at their chosen abstraction level?
- Do arrow directions match real signal flow?
- Do names match the interface, stage, FSM, storage, and equation tables?
- Do waveform columns represent values sampled at the stated edge?
- When a diagram disagrees with a table, is the table treated as authoritative and the diagram reported for correction?

## Finding Format

Report each concern separately:

```text
Rank: blocking | important | suggestion
Issue: <specific defect or ambiguity>
Why it matters: <observable failure, implementation risk, or verification gap>
Evidence: <file:line and affected FR/TR/FSM/T IDs>
Alternatives:
1. <option when the user owns a genuine trade-off> — Pros: <...>; Cons: <...>
2. <second materially distinct option when needed> — Pros: <...>; Cons: <...>
User decision required: yes | no
```

Give one recommendation and its trade-off for each finding. Add alternatives only when the user owns a genuine decision with materially different valid outcomes. End with open questions and any assumptions the reviewer could not validate.

## Review Exit Criteria

The independent review is complete when the reviewer has reported mechanical status, every semantic area that could be evaluated, ranked findings with evidence and recommendations, open questions, and unvalidated assumptions. Resolution, revalidation, and approval belong to the main workflow.

The reviewer never edits the specification or approves it on the user's behalf.
