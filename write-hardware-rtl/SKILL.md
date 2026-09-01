---
name: write-hardware-rtl
description: Implement or review synthesizable SystemVerilog RTL intended for Verilator. Use for new modules, RTL changes, and RTL correctness or style review; not for testbench code or unresolved architecture decisions.
---

# Write Hardware RTL

## Outcome and Scope

Implement the agreed hardware contract with the smallest readable RTL change, or review existing RTL without editing when the user asks only for review.

Read the specification, existing module, callers, tests, and project build configuration before editing. Preserve ports, parameters, reset behavior, latency, throughput, ordering, and repository conventions unless the user explicitly requests a contract change. When externally visible behavior is missing or ambiguous, stop implementation at that decision and update or obtain the specification first.

Project style and tool configuration take priority. For a new standalone module with no repository convention, use the [lowRISC Verilog Coding Style Guide](https://github.com/lowRISC/style-guides/blob/master/VerilogCodingStyle.md) as the default. Check version-sensitive flags and language support against the repository-pinned Verilator or the [official Verilator guide](https://verilator.org/guide/latest/).

## 1. Map the Contract

Before writing logic, map each applicable functional requirement, timing requirement, protocol rule, reset rule, and state transition to:

- The RTL mechanism that implements it.
- A test, assertion, or coverage target that can falsify it.
- Any unresolved decision or repository constraint.

For a narrow fix, map only the affected contract and regression surface. This step is complete when no externally visible choice is being invented in RTL.

## 2. Implement Synthesizable Logic

Follow these invariants unless the existing project intentionally uses another convention:

- Use SystemVerilog with explicit declarations, typed parameters, explicit widths and signedness, and elaboration checks for illegal parameter combinations.
- Use ANSI ports and named parameter and port connections. Connect every port intentionally; avoid positional connections and `.*`.
- Use `logic` for synthesizable signals; use a net type when net semantics are actually required.
- Use `always_comb` with complete assignments and blocking `=`; use `always_ff` with non-blocking `<=`.
- Keep sequential blocks limited to reset and state updates. Compute next state and outputs in combinational logic when that structure fits the design.
- Give every `case` a safe default. Use explicit comparisons for control decisions; avoid `casex`, inferred latches, delays, hierarchical references, and `X` assignments in synthesizable RTL.
- State arithmetic width, signedness, extension, truncation, rounding, saturation, and overflow behavior directly in code.
- Name signals and state after their domain meaning. Write comments only for intent, constraints, units, or non-obvious tool behavior.

Reset control and validity state to the specified safe values. A datapath register or memory may omit reset only when reset control makes its contents architecturally invisible until overwritten; keep that reason beside the declaration or reset logic and check the gating behavior.

For an FSM, define the state type, reset state, transition priority, outputs, and illegal-state recovery required by the specification. Constrain the encoding only when the contract, safety goal, or implementation decision requires it.

## 3. Preserve Protocol Semantics

For valid/ready channels:

- The producer may assert valid without waiting for ready.
- Transfer occurs only when valid and ready are sampled high at the specified edge.
- While valid is stalled, hold valid and payload stable.
- After a transfer, a different payload may appear on the next cycle while valid stays high.
- Apply flush, cancellation, and reset priority exactly as specified.
- Avoid combinational paths or loops forbidden by the timing contract.

Derive acceptance, occupancy, and status from one consistent event model. Prove boundary cases such as simultaneous enqueue/dequeue, full, empty, back-to-back traffic, and reset recovery; do not copy a generic FIFO formula into a different contract.

## 4. Add Useful Observability

Assertions must check the specification across time or an independently falsifiable invariant. Separate environment assumptions from DUT guarantees. Gate operational properties through reset and ensure `$past` is not sampled before valid history exists.

Use assertion constructs supported by the project's Verilator version and compile them explicitly in verification builds, for example with `--assert`. Compile and run every new property; Verilator supports only part of SystemVerilog assertions.

Assert data is known only when the interface contract says it is meaningful. Prioritize protocol stability, legal ranges, conservation, ordering, capacity, state transitions, and reset recovery over assignments restated as assertions.

Add requirement-linked cover properties for important boundaries, concurrency, recovery, and state transitions. Automatic coverage and FSM detection are version- and pattern-dependent, so they do not replace explicit contract coverage.

For sequential or protocol-heavy modules, provide runtime-selectable event logging through the project's existing logging layer. If none exists, use a per-module `+LOG_<MODULE>=<level>` convention. Log accepted transfers, state changes, stalls, errors, and recovery with `$time` and `%m`; avoid combinational or every-cycle noise by default.

Wrap simulation-only assertions, logs, and cover properties with the repository's established synthesis guard.

## 5. Verify

Use the repository's lint, build, and simulation commands so includes, defines, source lists, top selection, and parameterizations match the real design. A standalone fallback lint command is:

```bash
verilator --lint-only --assert -Wall <project-options-and-sources>
```

Treat warnings as defects unless a narrow waiver documents why the construct is safe. Avoid global warning suppression for source-owned RTL.

Run:

1. Lint on the real source set and relevant parameter configurations.
2. Focused tests for the changed requirements and boundary cases.
3. The relevant regression.
4. Coverage review for requirement-linked targets, with unreachable or waived targets explained.

Finish only when the requested RTL or review is complete, no observable behavior was invented, lint and relevant tests pass, assertions compile and run, and logs or temporary probes do not hide a regression.
