---
name: write-hardware-spec
description: Use when creating, updating, reviewing, or finalizing architecture or microarchitecture specifications for RTL blocks before RTL or testbench implementation; covers interfaces, protocols, timing, reset, FSM and pipeline behavior, traceable tests, and review gates.
---

# Write Hardware Spec

## Purpose

Create the single source of truth for what an RTL block does and how it is implemented. Freeze observable behavior, timing, state, reset, and verification intent before any RTL or testbench implementation begins.

Treat this file as the sole normative contract for the skill. References are non-normative aids; when a reference conflicts with this file, follow this file.

## Required Skills

- **REQUIRED BACKGROUND:** `superpowers:brainstorming`. Invoke it before drafting every new specification and before any update that changes externally visible behavior or a microarchitecture decision. If it is unavailable, stop and report the missing prerequisite.
- **CONDITIONAL HANDOFF DEPENDENCY:** `write-hardware-rtl`. Require it only when dispatching RTL implementation from an approved specification.
- **CONDITIONAL HANDOFF DEPENDENCY:** `write-hardware-test-bench`. Require it only when dispatching verification implementation from an approved specification.

Do not replace a missing required skill with an improvised workflow.

## Workflow

Follow every applicable gate in order:

```text
Load this contract and stage dependencies
                 |
                 v
Inspect requirements or the existing specification
                 |
                 v
Invoke superpowers:brainstorming
                 |
                 v
Choose merged or architecture + microarchitecture format
                 |
                 v
Draft the specification and test plan
                 |
                 v
Run definition-of-done and mechanical checks
                 |
                 v
Dispatch an independent review subagent
                 |
                 v
Resolve blocking decisions with the user
                 |
                 v
Obtain explicit user approval of the frozen specification
                 |
                 v
Dispatch parallel RTL and testbench handoffs
```

For an update, read the complete existing specification first. Preserve unrelated requirements, tests, IDs, and design decisions. Add new IDs rather than renumbering existing IDs unless the user explicitly requests a renumbering migration.

## Stop Conditions

Stop the affected workflow branch and ask the user when:

- an externally visible behavior, corner case, or timing choice is ambiguous;
- the existing specification required for an update is unavailable;
- a required dependency for the current stage is unavailable;
- parameter legality or an interface protocol cannot be determined;
- mechanical validation fails;
- requirement-to-test traceability is incomplete;
- an independent reviewer reports an unresolved blocking concern; or
- the final specification has not received explicit user approval.

Never invent externally visible behavior to complete a document. Record unresolved decisions as questions during brainstorming; do not leave placeholders in a draft presented as complete.

## Output Format Selection

Use exactly one of these layouts:

```text
spec/<block>_spec.md   # merged architecture + microarchitecture
spec/<block>_arch.md   # architecture for a complex block
spec/<block>_uarch.md  # microarchitecture + test plan for a complex block
```

- **REQUIRED — split format:** Use separate architecture and microarchitecture documents for a pipelined block, a design with multiple FSMs, multiple independently reviewable sub-blocks, or a design whose implementation detail would obscure the observable contract.
- **CONDITIONAL — merged format:** Use one merged document only for a single non-pipelined block with at most one control FSM and no independently reviewable sub-blocks.
- **REQUIRED — update format:** Preserve the existing valid split/merged layout unless the change makes it violate these criteria. If the format must change, explain the migration before editing.

In split format, define externally observable requirements only in the architecture document. Put the implementation refinement and shared test plan in the microarchitecture document; reference architecture IDs rather than redefining them.

## Normative Contract

Use explicit **REQUIRED**, **CONDITIONAL**, and **RECOMMENDED** language in the specification wherever compliance strength matters.

### Architecture Contract

An architecture document defines observable behavior, not implementation. It is **REQUIRED** to contain:

1. **Purpose** — scope, problem solved, and operating context.
2. **Parameters** — name, type, default, meaning, legal range, derived status, and illegal combinations.
3. **Interfaces** — every port, direction, width, clock/reset domain, grouping, and protocol role. Use lowRISC suffixes (`_i`, `_o`, `_io`, `_ni`, `_no`) unless the project already mandates another convention.
4. **Functional Requirements** — independently testable `FR-xx` definitions. Resolve simultaneous events, boundary behavior, ordering, cancellation, backpressure, and error behavior.
5. **Timing Requirements** — measurable `TR-xx` definitions with cycle/rate/path reference points.
6. **Reset-Visible Behavior** — interface behavior during reset and quantified recovery after reset.
7. **Non-Goals** — explicit exclusions that do not contradict requirements or parameters.
8. **Block Diagram** — a small ASCII diagram followed by explanatory bullets.

Do not prescribe internal register names, state encodings, pipeline registers, or private implementation structure in an architecture document.

### Microarchitecture Contract

A microarchitecture document or merged document defines implementation decisions. It is **REQUIRED** to contain:

1. **Block Diagram** — sub-blocks, storage, and real signal flow.
2. **Sub-Block Decomposition** — function, inputs, outputs, state, and behavior for each unit.
3. **Internal Signals and Storage** — names, widths, kind, ownership, and purpose.
4. **Critical Timing Paths** — source, destination, concern, and safe mitigation.
5. **Reset Behavior** — reset value or explicit no-reset justification for every register and storage array.
6. **Requirement Mapping** — show how each architecture `FR-xx` and `TR-xx` is implemented without redefining it.
7. **Test Plan** — the shared, two-way traceable plan described below.

In merged format, place these sections under a REQUIRED `Implementation Detail` heading.

Include these sections when applicable:

- **CONDITIONAL — Pipeline Stages:** For every stage, specify function, inputs, outputs, inter-stage registers, advance condition, stall behavior, bubble/replay behavior, and flush behavior. Include an ASCII pipeline diagram.
- **CONDITIONAL — FSM Definitions:** Define every state and encoding. Give every transition a stable `FSM-<NAME>-<NN>` ID, an unambiguous condition, priority when conditions overlap, and reset/flush behavior. Define recovery or assertion behavior for illegal state encodings. Treat the transition table as authoritative and add a small ASCII state sketch.
- **CONDITIONAL — Datapath Equations:** State arithmetic width, signedness, truncation, saturation, rounding, and overflow behavior.

### Protocol Semantics

For every interface channel, it is **REQUIRED** to state the protocol kind, producer, consumer, transfer event, ordering, backpressure, and stability rules.

For every valid/ready channel:

- The producer may assert valid independently of ready. Valid must not wait for ready.
- A transfer occurs only when valid and ready are both asserted at the specified sampling edge.
- After valid is asserted without a transfer, the producer holds valid and its payload stable while stalled.
- After a transfer, the producer may present a new payload on the next cycle even if valid remains asserted.
- The specification states whether ready may depend combinationally on valid and lists every permitted or forbidden cross-interface combinational path.
- Any exception that retracts valid or discards data, such as flush or cancellation, is an explicit functional requirement with priority and recovery behavior.

Do not write the ambiguous rule that payload remains stable for every cycle in which valid is high; it incorrectly forbids back-to-back transfers with different payloads.

For valid-only, ready-only, request/acknowledge, credit, interrupt, and memory-mapped interfaces, state equally precise event, persistence, and response rules.

### Timing and Reset

Every timing requirement is **REQUIRED** to use a unique `TR-xx` ID and define measurable reference points. State, as applicable:

- clock and sampling edge;
- latency start event, end event, and exact cycles;
- sustained throughput in transfers or items per cycle;
- behavior of latency under stalls, bubbles, replay, and flush;
- allowed and forbidden combinational paths;
- reset assertion style, reset deassertion assumptions, and recovery cycles; and
- any frequency, setup, or integration constraint owned by the block.

Use current registered state for combinational status outputs. When registering ready, valid, full, empty, or another state-derived status for the following cycle, derive its D input from the corresponding next-state value. Never register a one-cycle-stale current-state full indication if that permits an extra transfer with nowhere to store it.

Reset treatment is **REQUIRED** for every state element:

- Give each register an explicit reset value.
- For every array or memory not reset, justify why unread/uninitialized contents cannot become architecturally visible.
- Define output validity and handshake behavior during reset.
- Quantify the first cycle in which each interface may transfer after reset deassertion.

### Test Plan and Traceability

Use these stable ID grammars:

| Item | Definition ID | Definition Location |
|------|---------------|---------------------|
| Functional requirement | `FR-xx` | Functional Requirements |
| Timing requirement | `TR-xx` | Timing Requirements |
| FSM transition | `FSM-<NAME>-<NN>` | FSM Transitions |
| Test | `T-xx` | Test Plan |

IDs are **REQUIRED** to be unique definitions. References to an ID do not redefine it.

Two-way traceability is **REQUIRED**:

- Every `FR-xx`, `TR-xx`, and `FSM-<NAME>-<NN>` maps to at least one `T-xx`.
- Every `T-xx` maps on its definition row to at least one requirement or transition ID.
- Every ID cited by a test has exactly one definition in the selected specification set; an ID-shaped token alone is not a valid mapping.
- Every FSM transition has at least one mapped test.
- Every parameter boundary and illegal combination has a mapped test when the testbench can elaborate it.
- Corner tests cover reset during operation, back-to-back activity, boundary values, simultaneous events, stalls, and flushes when applicable.

Each test definition states stimulus, expected observations, timing, and completion criteria. A test name alone is not a plan.

Run the bundled mechanical validator before review:

```text
python3 scripts/validate_spec.py <spec-file-or-directory> [--format auto|merged|split]
```

Treat a clean result as structural evidence only. It does not establish semantic hardware correctness.

### Assertions and Coverage

Every listed assertion is **REQUIRED** to be temporal or independently falsifiable against the implementation. Prefer properties that check state transitions, stability under stall, legal ranges, ordering, conservation, and protocol obligations.

Reject:

- a direct restatement of the combinational assignment that constructs the checked signal;
- a condition made impossible by the same handshake or gating expression in the assertion;
- a property already implied entirely by another assertion; or
- a property whose antecedent cannot occur under legal assumptions.

State interface assumptions separately from DUT assertions. Explain any assumption that constrains the environment.

Coverage points are **REQUIRED** to target meaningful requirements, state/transition reachability, boundary states, concurrent events, stalls, and recovery sequences. Do not use coverage as a substitute for checking behavior.

### Diagrams

All diagrams are **REQUIRED** to use ASCII. Do not use Mermaid, Graphviz/dot, or image files.

- Use real interface and internal signal names.
- Keep each diagram small; split dense diagrams by abstraction or sub-block.
- Follow each diagram with bullets that explain elements and direction.
- Use cycle-by-cycle waveform tables for interface timing, with one sampled cycle per column.
- Treat tables, equations, and numbered requirements as authoritative; diagrams are explanatory.

## Definition of Done

Do not dispatch independent review until every applicable item passes:

- [ ] Purpose and scope are unambiguous.
- [ ] All parameters include legality, defaults, derived status, and illegal combinations.
- [ ] Every port and protocol role is defined.
- [ ] Every externally visible functional behavior has one `FR-xx` definition.
- [ ] Every timing behavior has one quantified `TR-xx` definition.
- [ ] Boundary and simultaneous-event behavior is resolved.
- [ ] Split/merged format satisfies the objective selection rules.
- [ ] Microarchitecture mechanisms cover every architecture requirement.
- [ ] Every pipeline stage and FSM transition has complete stall/flush/reset behavior when applicable.
- [ ] Every register and storage array has reset treatment.
- [ ] Two-way test traceability is complete.
- [ ] Assertions are temporal or independently falsifiable.
- [ ] Coverage targets meaningful behavior.
- [ ] ASCII diagrams agree with authoritative tables and equations.
- [ ] Every referenced local file exists.
- [ ] No unresolved decision markers or placeholders remain.
- [ ] `scripts/validate_spec.py` passes.

## Independent Review Gate

After the definition of done passes, dispatch a separate review subagent. Self-review cannot substitute for this gate.

Give the reviewer:

1. every spec file path;
2. the absolute path to `references/review-checklist.md` resolved from this skill directory;
3. instructions to read the complete spec and checklist; and
4. instructions to return ranked findings in the checklist format without editing the spec.

The reviewer challenges semantic correctness, implementability, protocol behavior, timing, reset, traceability, assertions, and diagram consistency. Mechanical failures are returned immediately rather than buried among design opinions.

For each blocking or important concern, present the issue, impact, and 2-3 alternatives with trade-offs to the user. The user decides externally visible behavior and architecture trade-offs. If a resolution changes architecture, rerun mechanical validation and independent review.

## User Approval Gate

After all blocking findings are resolved, present the final spec paths, the resolved decisions, remaining non-blocking suggestions, and validation result. Important findings are resolved or explicitly accepted by the user. Obtain explicit user approval before declaring the specification frozen.

Any architecture-affecting edit after approval invalidates the frozen state and requires validation, independent review, and user approval again.

## Implementation Handoff

Do not write RTL or a testbench in this skill.

After approval, require both sibling handoff skills and dispatch RTL and testbench work in parallel because both consume the frozen specification:

1. **RTL handoff:** Provide spec paths, target `rtl/<block>.sv`, and require `write-hardware-rtl` before code is written.
2. **Testbench handoff:** Provide spec paths, the complete test plan, target `tb/tb_<block>.cpp`, and require `write-hardware-test-bench` before code is written.

The testbench is written against the specification, not the RTL. Integration, lint, build, and simulation follow the handoff skills after both implementations complete.

If either handoff skill is unavailable, stop before implementation dispatch and identify the missing dependency.

## References

- [references/templates.md](references/templates.md) — **RECOMMENDED** before drafting; copyable, non-normative structures.
- [references/example-spec.md](references/example-spec.md) — **RECOMMENDED** when a complete merged-format example is useful.
- [references/review-checklist.md](references/review-checklist.md) — **REQUIRED** for the independent review subagent.

References illustrate this contract and must not introduce new requirements.
