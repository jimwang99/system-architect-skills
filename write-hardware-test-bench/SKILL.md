---
name: write-hardware-test-bench
description: Write or review SystemC testbenches for RTL compiled with Verilator `--sc`. Use for block-level stimulus, monitors, scoreboards, and regressions; not for pure C++ `--cc` harnesses or synthesizable RTL.
---

# Write a SystemC Testbench for Verilator

## Outcome and Scope

Produce the smallest testbench that proves the requested observable behavior and fails reliably on a mismatch, unexpected output, incomplete check, or timeout. A review request reports findings without editing.

Read the user request, available specification or test plan, DUT ports, existing testbench infrastructure, and project build commands. Use existing `T-xx` IDs when present. A formal hardware-spec skill is not a prerequisite for a focused regression, but expected behavior, timing, and completion must be explicit before code is written.

Use the repository's C++ standard, naming, build, logging, and artifact conventions. The supplied references assume SystemC 3.0.x, Verilator 5.x, and C++17; verify local versions before relying on a version-specific API.

## 1. Define the Test Contract

For each requested case, record:

- Requirement or behavior under test.
- Stimulus, protocol acceptance edge, and legal backpressure.
- Expected observations and exact timing.
- Completion condition and watchdog bound.
- Negative expectation window when the required result is no output.

Ask only when an unresolved behavior would change pass or fail. The test contract is complete when every expected result can be computed independently of the RTL implementation.

## 2. Choose Proportionate Structure

A small deterministic smoke test may use one top-level module and a few processes. Separate reset, driver, monitor, reference model, scoreboard, and completion components when concurrency, reuse, multiple channels, or protocol complexity makes ownership clearer.

Keep stimulus generation separate from checking. For multi-channel or out-of-order protocols, track accepted transactions by the protocol's correlation key and enforce only legal ordering. A FIFO queue is sufficient only for strict in-order responses.

Use `std::unique_ptr` for Verilated models and trace objects. Split headers from sources only for components reused across testbenches.

## 3. Drive and Observe at Contracted Events

Derive drive and sample points from the DUT protocol instead of applying one edge convention to every design. Establish synchronous inputs before the specified acceptance edge, then observe outputs after the DUT and SystemC delta cycles have settled. Avoid driver, DUT, and monitor races at the same edge.

A driven valid/payload is an attempt, not an accepted transaction. Add an expectation exactly once when the protocol transfer event occurs. Hold or retry stalled inputs as the protocol requires without duplicating expectations.

On an output transfer, require a matching expectation before consuming it. For a forbidden-output test, register a bounded observation window and fail on any matching event; do not represent absence with a dummy queue item.

The completion controller may stop only after stimulus is done and every required observation has completed. Fail on pending expectations, unexpected outputs, expected/check count mismatch, assertion failure, or watchdog timeout.

## 4. Make Failures Diagnosable

Use the project's logging layer. Otherwise wrap `SC_REPORT_INFO_VERB` so logs identify the hierarchical component.

At runtime-selectable verbosity, log:

- Test ID and phase boundaries.
- Accepted stimulus and correlation ID.
- Expected versus actual values for each check.
- Unexpected outputs, timeouts, and final counts.

Default logs should explain the first failure without dumping every cycle. Add signal-level or every-cycle logs only for focused debugging. Use `debug-hardware-with-logging` when a simulation failure needs iterative instrumentation.

## 5. Integrate with Verilator

In `--sc` flow, let the SystemC kernel evaluate the model through `sc_start()`; do not call `eval()` manually.

Tracing is conditional. When using `VerilatedFstSc`, enable tracing before model construction, complete zero-time elaboration before registering the trace in Verilator versions that require it, and close the trace after simulation.

Call the model's `final()` after simulation. When coverage is enabled, write coverage after `final()` to an explicit project output path and use the same path for annotation.

Use the repository's build first. When none exists, adapt [references/CMakeLists.txt](references/CMakeLists.txt); read [references/reference.md](references/reference.md) for `--sc` integration, tracing, coverage, and logging details. Use [references/example-testbench.cpp](references/example-testbench.cpp) as an example to adapt, not a mandatory architecture.

## 6. Verify

Build and run through the project's normal commands. Run each focused case, then the relevant regression. Exercise required functional cover targets when coverage is in scope; explain unreachable or intentionally waived targets rather than treating every raw coverage counter as a requirement.

Finish only when:

- Every requested behavior or `T-xx` case has stimulus, expected observations, timing, and a completion result.
- Expected values come from the specification or an independent reference model, not copied DUT logic.
- Acceptance and checking occur exactly once per contracted event.
- Negative expectations and global completion are bounded.
- The executable returns failure for every scoreboard, count, unexpected-output, assertion, or timeout error.
- Build and relevant tests pass, with artifacts written to known output paths.
