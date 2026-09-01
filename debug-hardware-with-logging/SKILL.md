---
name: debug-hardware-with-logging
description: Diagnose Verilator RTL simulation failures with structured logging when waveforms are unavailable or insufficient. Use for assertion failures, scoreboard mismatches, hangs, and unexpected cycle behavior in SystemC testbenches.
---

# Debug Hardware with Logging

## Outcome

Find the first causal divergence and explain it with reproducible simulation evidence. Inspect code to form hypotheses, but validate each hypothesis by rerunning the simulator. Implement a fix only when the user requests one.

Preserve the original failing test, seed, configuration, and command. A minimized reproducer is additional evidence only when it still shows the same failure.

## 1. Reproduce

Use the target repository's build and test commands. Record the simulator version, exact command, seed, parameters, relevant environment, and first failure message. Keep standalone runs bounded with the testbench watchdog or repository timeout.

Run the smallest existing test that shows the failure. Capture its exit status and log in the repository's normal output location. Enable assertions explicitly when the project supports them.

If the failure is intermittent, rerun recorded seeds and keep the earliest reliable reproducer. If reproduction fails, report what was tried and which missing condition prevents diagnosis.

This step is complete when the failure is reproducible or the reproduction blocker is explicit.

## 2. Find the First Bad Event

Search the log for failures and their context:

```bash
rg -n '%Error|%Fatal|ASSERT|MISMATCH|TIMEOUT|FAIL' <simulation-log>
```

Start at the first failure, then inspect earlier accepted transactions, state transitions, resets, stalls, and monitor decisions that could cause it. Later mismatches may be cascade effects.

Use existing verbosity controls selectively. Raise the RTL `+LOG_<MODULE>=<level>` or SystemC `+verbosity=<LEVEL>` only for relevant blocks and time windows. Global maximum verbosity often hides the useful sequence in noise.

Read the specification, test, and relevant RTL or testbench code to form a concrete hypothesis. Treat missing assertions, unhit coverage, and suspicious code as leads rather than proof.

## 3. Add One Focused Probe

When existing logs are insufficient, add temporary simulation-only logging through the project's logging layer. Log events from clocked processes, not every combinational evaluation.

Each probe should identify:

- Simulation time, module or testbench component, and test or transaction ID.
- The event being tested, such as acceptance, stall, transition, reset, or comparison.
- The smallest relevant pre-state, inputs, decision, and next-state or output.

Instrument both sides of a suspected boundary when ownership is unclear: driver acceptance, DUT interface, state update, output handshake, and monitor comparison. Rerun the same reproducer and keep only evidence that confirms or rejects the current hypothesis.

Repeat the probe-and-rerun loop until one mechanism explains the first bad event. Avoid changing functional behavior while collecting evidence.

## 4. Conclude or Fix

For diagnosis, report:

- Root cause and the violated specification or testbench contract.
- First bad cycle or event, with the log evidence that proves causality.
- Responsible source location and why later failures follow.
- Confidence and the remaining alternative when evidence is incomplete.

If the user requested a fix, make the smallest behavior-preserving patch that addresses the proved cause. Remove temporary probes before final verification unless the logging has lasting diagnostic value.

Verify the original reproducer, the focused regression for the affected contract, and the relevant project regression. Explain material coverage changes; coverage need not remain numerically unchanged.

## Fallback Evidence

Use coverage to test a reachability hypothesis, not to infer causality by itself. Use FST or VCD only when event logs cannot expose the necessary relationship; inspect the text conversion or ask the user to view the waveform when no viewer is available to the agent.

Finish only when the conclusion is supported by a rerun, temporary instrumentation is removed or intentionally retained, and verification results match the requested diagnosis-or-fix scope.
