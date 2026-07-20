---
name: debug-hardware-with-logging
description: Use when debugging RTL simulation failures, assertion violations, scoreboard mismatches, or unexpected hardware behavior in Verilator + SystemC testbenches and no waveform viewer is available — before reading code or proposing fixes
---

# Debug Hardware with Logging

## Overview

Systematic workflow for debugging RTL simulated with Verilator + SystemC testbenches. No waveform viewer is available — **structured text logging is the primary debug tool.**

**Core principle:** the simulator already computed the answer. Never hand-trace RTL logic or propose a fix from code reading — add logging at the signals you care about, rerun, and read the output. The simulator shows what *actually* happens, not what you *think* happens.

## Workflow (follow in order)

### 1. Reproduce with logging enabled

```bash
verilator --sc --exe --trace-fst --coverage -Wall design.sv tb.cpp -o Vdesign
make -C obj_dir -f Vdesign.mk
./obj_dir/Vdesign +LOG_MODULE=4 +verbosity=DEBUG 2>&1 | tee sim.log
```

RTL logging uses `+LOG_<MODULE>=<level>` plusargs, levels 0–4 — conventions in the write-hardware-rtl skill. SystemC verbosity uses the testbench's `+verbosity=<LEVEL>` plusarg (`LOW`/`MEDIUM`/`HIGH`/`FULL`/`DEBUG`, max is `DEBUG`) — see the write-hardware-test-bench skill; there is no built-in `--sc_verbosity` flag. **Start at maximum verbosity**; filter with grep later.

Can't reproduce? Simplify the stimulus until you can, then continue.

### 2. Check assertions first

```bash
grep -E '%Error|%Fatal|ASSERT|MISMATCH' sim.log
```

Verilator prints `%Error:`/`%Fatal:` at runtime; literal `$error`/`$fatal` source syntax does not appear in the simulation log. Assertions sit at module boundaries and FSM transitions and report `$time` + module — they often pinpoint the exact cycle and signal. No assertion fired but the scoreboard mismatches? The bug is likely in the data path between assertion points.

### 3. Narrow the time window, add targeted logging

```bash
grep -n 'MISMATCH' sim.log | head -1     # first failure
grep -E '^\[14[0-9]{4}' sim.log          # adapt to your failure time (here: 140000–149999)
```

If existing logging is insufficient, add temporary statements at the exact signals you need and rerun — do not hand-trace:

```systemverilog
// Temporary debug — remove after fix
`ifndef SYNTHESIS
if (log_level >= 4)
  $display("[%0t] %m: DEBUG a=%0d b=%0d state=%s", $time, a, b, state_q.name());
`endif
```

```cpp
// Temporary debug in a TB block — remove after fix
TB_LOG_MEDIUM(fmt::format("{} sum_o={:#x}", sc_time_stamp().to_string(), sum_o.read()).c_str());
```

Root cause still unclear? Add more logging and rerun. Loop here — never fall back to mental tracing.

### 4. Fix and verify

1. Fix the RTL or testbench
2. Lint: `verilator --lint-only -Wall <file.sv>`
3. Rerun the failing test with logging to confirm
4. Run full regression; check coverage unchanged or improved
5. Remove temporary debug statements

## Still stuck

- **Coverage:** `verilator_coverage --annotate coverage_annotated --annotate-min 1 coverage.dat`, then `grep -rn '^%' coverage_annotated/` — with a minimum of 1, uncovered lines are prefixed with `%`. An uncovered path that should execute in the failing test means the stimulus never reaches that state — suspect the testbench driver, not the RTL.
- **FST trace (last resort):** the trace exists only if the testbench enabled it (`Verilated::traceEverOn` + `model->trace()` — see the write-hardware-test-bench skill). Convert with `fst2vcd dump.fst > dump.vcd` (GTKWave package) and inspect the VCD text, or ask the user to open the `.fst` in a waveform viewer.

## Common Bug Patterns

| Symptom | Likely Cause | What to Check |
|---------|-------------|---------------|
| Scoreboard mismatch on specific bits | Shift register or mux logic error | Log shift register contents each cycle |
| Works for some data values only | Data-dependent path (e.g. zero-fill) | Test with 0x00, 0xFF, 0xAA, 0x55 |
| Output delayed by N cycles | Pipeline depth mismatch vs scoreboard | Log timestamps in driver and monitor |
| Assertion fires after reset deasserts | Reset sequencing issue | Reset timing in testbench vs RTL |
| Intermittent failures | Sampling edge mismatch / race | Clock edge consistency (posedge everywhere) |
| Signal stuck at 0 or 1 | Undriven signal or wrong port binding | `--lint-only` warnings, SC port binding |

## Red Flags — STOP

Catch yourself doing any of these? Stop, return to Step 1:

- Building a truth table or trace table by hand from RTL code
- "I can already see the bug from the code" — before running the simulation
- Skipping assertion checks because "I know what the bug is"
- Proposing a fix without running the simulator
- Reading RTL before reproducing the failure with logging
