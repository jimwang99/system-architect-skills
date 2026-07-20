---
name: write-hardware-test-bench
description: Use when writing SystemC testbench code for Verilator-simulated RTL, when generating C++ test harnesses for hardware modules, or when the user asks to create a testbench, test, or stimulus for a Verilog/SystemVerilog design.
---

# SystemC Testbench Style Guide (Verilator)

A style-focused reference for writing readable, debuggable SystemC testbenches that drive Verilator-compiled RTL models. See `references/reference.md` for API details and `references/example-testbench.cpp` for the working template (with `references/adder.sv` DUT and `references/CMakeLists.txt` build script — verified to build and run green).

**Related skills:**
- **REQUIRED BACKGROUND:** `write-hardware-spec` — produces the T-xx test plan this skill implements
- `write-hardware-rtl` — RTL-side conventions (logging plusargs, assertions, cover properties)
- `debug-hardware-with-logging` — use when simulation fails or scoreboard mismatches appear

## Coding Style

- **Base**: Google C++ Style Guide
- **Language**: C++17; selective C++20 (e.g., `std::format` where available)
- **Naming**: hardware abbreviations are fine: `clk`, `rst_n`, `addr`, `wdata`, `rdata`, `en`, `vld`, `rdy`
- **Ownership**: `std::unique_ptr` for all Verilator models and trace objects -- never raw `new`/`delete`

## File Organization

| Item | Convention |
|------|-----------|
| Filename | `tb_<module>.cpp` |
| Include order | 1. `V<Module>.h` (Verilator model) 2. `verilated.h`, `verilated_cov.h`, `verilated_fst_sc.h` 3. `<systemc>` 4. C++ stdlib 5. Project headers |
| Namespace | `<systemc>` (no `.h`) keeps everything in `sc_core` — add `using namespace sc_core;` in the .cpp (never in a header) |
| Header/source split | Only when reusing driver/monitor modules across testbenches |

## Testbench Structure

- **Separate SC_MODULEs** for ResetGen, Driver, Monitor, and top-level Testbench -- never monolithic
- **Clock**: `sc_clock clk{"clk", period, SC_NS}` in the top module
- **Reset**: dedicated `SC_THREAD` in its own ResetGen module — asserts reset, waits N cycles, deasserts. Keeps multi-stage resets, mid-test reset injection, and per-domain resets out of stimulus code
- **Driving**: change signals on posedge
- **Sampling**: read signals on negedge (SystemC kernel handles evaluation automatically)
- **Scoreboard**: `std::queue<expected_t>` for in-order responses; create an expectation when the DUT accepts a transaction, and pop it when the corresponding output handshake occurs
- **Ready/valid protocols**: a drive is only an attempt — enqueue exactly once when `valid && ready` is sampled on the protocol edge, never once per stalled cycle
- **Multi-channel protocols** (e.g., AXI4): one Driver and one Monitor per channel, plus a transaction-level scoreboard that correlates independently accepted channels and tracks response IDs/order
- **Completion**: stop only after stimulus is complete and every expected response has been checked; fail on pending expectations, unexpected outputs, count mismatches, or watchdog timeout

## Logging & Tracing (CRITICAL)

The agent cannot use a waveform viewer. Logging is the primary debug tool.

**TB_LOG macro** — wrap SC_REPORT_INFO_VERB with automatic module name:
```cpp
#define TB_LOG(verbosity, msg) SC_REPORT_INFO_VERB(name(), msg, verbosity)
```
Note: `SC_REPORT_INFO_VERB` takes `const char*`. Format with `std::ostringstream` or `std::format`, then pass `.c_str()`.

**Verbosity levels** (full 6-level table with examples: `references/reference.md`):

| Level | Use for |
|-------|---------|
| `SC_LOW` | Test phase boundaries, pass/fail, end-of-test summary |
| `SC_MEDIUM` | Stimulus driven, expected-vs-actual checks |
| `SC_HIGH` | Signal-level detail, FSM transitions |
| `SC_DEBUG` | Every-cycle dumps, raw values |

**Per-block runtime control**: `set_actions(<exact-report-type>, SC_INFO, SC_DO_NOTHING)` can silence a module; with the `TB_LOG` macro, the exact report type is the module's hierarchical `name()` (for example, `tb.driver`). It cannot enable messages above the global verbosity threshold because `SC_REPORT_INFO_VERB` applies that threshold first. Implement a per-module threshold in the logging wrapper if selective verbosity is required.

**Runtime verbosity**: SystemC has **no built-in command-line parsing** — parse a `+verbosity=<LEVEL>` plusarg yourself in `sc_main` and call `sc_report_handler::set_verbosity_level()` (see `parse_verbosity()` in the example).

**Mandatory logging rules**:
- EVERY output check: log expected vs actual at `SC_MEDIUM`
- EVERY stimulus drive: log driven values at `SC_MEDIUM`
- End-of-test summary (total checks, passes, failures) at `SC_LOW`

## Verilator Integration

| Action | Rule |
|--------|------|
| Evaluation | SystemC kernel handles it via `sc_start()` — never call `model->eval()` in `--sc` flow (manual `eval()` is `--cc`-only) |
| Tracing | `Verilated::traceEverOn(true)` before model construction; `sc_start(SC_ZERO_TIME)` (elaboration) before `model->trace()`; `VerilatedFstSc` auto-dumps during `sc_start()` |
| Cleanup | `model->final()` after `sc_start()` returns — runs RTL final blocks, flushes coverage counters |
| Coverage dump | **After** `final()`: write to an explicit build/output path, e.g. `Verilated::threadContextp()->coveragep()->write("build/coverage.dat")`; requires `verilated_cov.h` |

> **Warning**: `VerilatedFstSc` privately inherits from `sc_trace_file`, so `sc_trace()` cannot trace custom SystemC signals into FST. Track testbench-only signals (like test phase) via console logging.

## Building & Running

**CMake is the default build tool** — Verilator ships `find_package(verilator)` with a `verilate()` function that handles include paths, C++ standard, and SystemC linkage. Working template: `references/CMakeLists.txt`. CMake elements, SystemC discovery, and the raw Verilator CLI fallback: `references/reference.md`.

The template defines `TB_OUTPUT_DIR` from `CMAKE_CURRENT_BINARY_DIR`, so FST and coverage artifacts are placed in `build/` regardless of the runtime working directory. Keep the filename passed to `coveragep()->write()` and the `verilator_coverage` command identical.

```bash
cmake -B build && cmake --build build
./build/tb_<block>                    # default verbosity (SC_MEDIUM)
./build/tb_<block> +verbosity=HIGH    # custom plusarg — see Logging

# From the RTL source dir (annotation resolves paths relative to cwd):
verilator_coverage --annotate coverage_annotated --annotate-min 1 build/coverage.dat
```

Check every RTL cover point was hit — misses mean the stimulus is not exercising the spec's functional requirements.

## Mapping Spec Test Plan to Code

The spec (from `write-hardware-spec`) produces a test plan with T-xx IDs. **Structure:** one `SC_THREAD` runs all tests sequentially, and each T-xx test is a helper function called in order. After stimulus completes, a bounded completion controller drains the scoreboard before calling `sc_stop()`.

**Rules:**
- **Every T-xx test must log its ID** at `SC_MEDIUM` when it starts — this makes it trivial to find failures in the log
- **Every T-xx test declares its expected behavior** — enqueue accepted transactions for normal outputs; for “no output” cases, register a bounded observation window that the Monitor checks independently
- **Order tests from simple to complex** — basic operations first, corner cases last
- **Corner-case tests (T-2x, T-3x)** may need custom Monitor logic (e.g., checking reset behavior) — add a flag or separate queue
- **Never infer pass from `fail_count == 0` alone** — require stimulus completion, zero pending expectations, expected/check-count equality, zero unexpected outputs, and no timeout

## Common Mistakes

| Symptom | Fix |
|---------|-----|
| `no template named 'sc_out'; did you mean 'sc_core::sc_out'?` | `<systemc>` keeps names in `sc_core` — `using namespace sc_core;` in the .cpp |
| `SystemC requires a C++ standard version of at least C++17` | `set(CMAKE_CXX_STANDARD 17)` (CMake) or `-CFLAGS "-std=c++17"` (raw CLI) |
| Runtime abort: `trace() is called before sc_core::sc_start()` | `sc_start(SC_ZERO_TIME);` before `model->trace()` |
| `member access into incomplete type 'VerilatedCovContext'` | `#include "verilated_cov.h"` |
| Coverage counts zero or undercounted | Write coverage **after** `model->final()`; annotate with `--annotate-min 1` (default 10 marks <10-hit points uncovered) |
| `--sc_verbosity` flag has no effect | No such flag — SystemC parses no CLI args; implement a `+verbosity=` plusarg (see example) |
