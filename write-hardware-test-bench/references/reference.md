# SystemC + Verilator Testbench Quick Reference

Versions assumed: SystemC 3.0.x (IEEE 1666-2023), Verilator 5.x, and CMake 3.19 or newer for the CMake flow.

## Section 1: SystemC Basics

### Headers & Namespaces

| Header | Effect |
|--------|--------|
| `<systemc>` | Modern. Everything stays in `sc_core` / `sc_dt` — add `using namespace sc_core;` in the .cpp (never in a header) |
| `<systemc.h>` | Legacy. Injects using-directives into the global namespace |

### Core Constructs

| Construct | Syntax | Notes |
|-----------|--------|-------|
| Module declaration | `SC_MODULE(MyTb) { ... };` | Expands to `struct MyTb : sc_module` |
| Simple constructor | `SC_CTOR(MyTb) { ... }` | Declares ctor taking `sc_module_name`. Supports `SC_THREAD`/`SC_METHOD` registration inside. |
| Custom constructor | plain C++ ctor taking `sc_module_name` + extra params | In SystemC 3.0 (IEEE 1666-2023) `SC_HAS_PROCESS` is deprecated and unnecessary — process macros work in any ctor. Only legacy SystemC 2.3 requires `SC_HAS_PROCESS(MyTb);` |
| Sequential thread | `SC_THREAD(run);` | Runs once, uses `wait()` to advance time, must call `sc_stop()` when done |
| Thread sensitivity | `sensitive << clk.pos();` | Place immediately after `SC_THREAD(run);`; event finders are safe before port binding |
| Combinational method | `SC_METHOD(check);` | Re-triggers on sensitivity list, **no** `wait()` allowed |
| Method sensitivity | `sensitive << sig_a << sig_b;` | Place immediately after `SC_METHOD(check);` |
| Clock | `sc_clock clk{"clk", 10, SC_NS};` | Name, period, unit. 50% duty cycle by default |
| Signal | `sc_signal<uint32_t> data{"data"};` | Named construction required for VCD/FST tracing |
| Start simulation | `sc_start();` | Runs until `sc_stop()` or starvation |
| Timed start | `sc_start(1000, SC_NS);` | Runs for specified duration |
| Stop simulation | `sc_stop();` | Call from `SC_THREAD` when tests complete |
| Current time | `sc_time_stamp()` | Returns `sc_time` object |
| Time literal | `sc_time(10, SC_NS)` | Used with `wait(sc_time(10, SC_NS))` |
| Skip initial trigger | `dont_initialize();` | Place after `SC_METHOD`; prevents call at time 0 |

### Data Types

| Type | Use When | Example |
|------|----------|---------|
| `uint8_t` / `uint16_t` / `uint32_t` / `uint64_t` | Bit width <= 64, no 4-state logic needed, best performance | `sc_signal<uint32_t> data{"data"};` |
| `sc_uint<N>` | Arbitrary bit width, bit selection needed, still 2-state | `sc_signal<sc_uint<12>> addr{"addr"};` |
| `sc_bv<N>` | Wide bit vectors, no arithmetic needed | `sc_bv<256> wide_bus;` |
| `sc_logic` / `sc_lv<N>` | 4-state logic (0, 1, X, Z) needed | `sc_signal<sc_lv<8>> tristate{"tristate"};` |

---

## Section 2: Verilator API

### Model Instantiation

```cpp
#include "Vtop.h"             // Generated header — name matches top-level module
#include "verilated.h"
#if VM_TRACE_FST
#include "verilated_fst_sc.h" // For FST tracing in SystemC
#endif

auto dut = std::make_unique<Vtop>("dut");
```

### Port Access (C++ flow only)

In pure C++ testbenches (`--cc`), ports map directly to public members:

```cpp
dut->clk = 0;
dut->rst_n = 1;
dut->data_in = 0xDEAD;
uint32_t result = dut->data_out;  // read output
```

In SystemC flow (`--sc`), ports connect via `sc_signal` bindings — see example-testbench.cpp.

### Evaluation

**SystemC flow (`--sc`):** The SystemC kernel manages evaluation automatically via `sc_start()`. Do **not** call `eval()` manually — the kernel handles it.

**C++ flow (`--cc`):**

```cpp
dut->a = 5;
dut->eval();  // Propagates inputs and internally settles generated regions
```

Call `eval()` once after changing inputs or advancing simulation time. Verilator's evaluation call performs its own settle iterations; an unconditional second call is not required. External interfaces such as VPI may request another evaluation after they modify model state, but that is a new state change rather than a “double-eval” rule.

### Finalization

```cpp
dut->final();  // MUST call before destruction — flushes coverage, releases resources
```

### Command-Line Plusargs

```cpp
int sc_main(int argc, char** argv) {
    Verilated::commandArgs(argc, argv);  // enables +verilator+... plusargs
    // ...
}
```

### FST Trace Setup (preferred over VCD)

When built with `--trace-fst`, use `VerilatedFstSc`, which auto-dumps during `sc_start()`:

```cpp
#if VM_TRACE_FST
Verilated::traceEverOn(true);  // MUST call before creating trace object

// ... instantiate DUT, bind ports ...

sc_start(SC_ZERO_TIME);       // Verilator 5.x: complete elaboration first,
                              // or trace() aborts at runtime

auto tfp = std::make_unique<VerilatedFstSc>();
dut->trace(tfp.get(), 99);    // 99 = trace depth
tfp->open("trace.fst");

// sc_start() auto-dumps — no manual dump() calls needed

// At end:
tfp->close();
#endif
```

For non-SystemC (pure C++) testbenches, use `VerilatedFstC` with manual `tfp->dump(sim_time)` calls.

### Coverage

```cpp
#if VM_COVERAGE
#include "verilated_cov.h"  // required — coveragep() returns incomplete type otherwise

// At end of simulation, AFTER dut->final() (final() flushes the counters).
// Use one explicit path in both the writer and annotation command:
dut->final();
Verilated::threadContextp()->coveragep()->write("build/coverage.dat");
#endif
```

Enable with `verilator --coverage` (or the `COVERAGE` option of CMake `verilate()`). View with `verilator_coverage --annotate <outdir> --annotate-min 1 build/coverage.dat` — default `--annotate-min` is 10, which marks points hit fewer than 10 times as uncovered (`%` prefix). Run annotation from the directory containing the RTL sources: source paths in coverage.dat resolve relative to cwd. The example CMake file defines `TB_OUTPUT_DIR` as its binary directory so the writer and command agree even when the executable is launched from the source directory.

### Building

**CMake (default)** — see CMakeLists.txt in this directory for the full working template:

```cmake
set(CMAKE_CXX_STANDARD 17)   # SystemC 3.x hard-requires C++17; builds fail without it
find_package(verilator REQUIRED HINTS $ENV{VERILATOR_ROOT})
add_executable(tb_<block> tb_<block>.cpp)
option(TB_ENABLE_TRACE_FST "Build FST tracing support" OFF)
option(TB_ENABLE_COVERAGE "Build coverage instrumentation" OFF)
set(TB_VERILATE_FEATURES SYSTEMC)
if(TB_ENABLE_TRACE_FST)
    list(APPEND TB_VERILATE_FEATURES TRACE_FST)
endif()
if(TB_ENABLE_COVERAGE)
    list(APPEND TB_VERILATE_FEATURES COVERAGE)
endif()
verilate(tb_<block> SOURCES <block>.sv TOP_MODULE <block>
         ${TB_VERILATE_FEATURES} VERILATOR_ARGS --assert -Wall)
verilator_link_systemc(tb_<block>)
```

- `SYSTEMC` selects `--sc` output mode — `--sc` and `--cc` are mutually exclusive
- `--assert` keeps RTL assertions enabled across the supported Verilator 5.x range
- Configure with `-DTB_ENABLE_TRACE_FST=ON` or `-DTB_ENABLE_COVERAGE=ON` only when those artifacts are needed
- `verilator_link_systemc()` finds SystemC via `SYSTEMC_INCLUDE`/`SYSTEMC_LIBDIR`/`SYSTEMC_ROOT` env vars, falling back to the default prefix (e.g. `/opt/homebrew`, `/usr/local`)

**Raw Verilator CLI fallback (no CMake):**

```bash
verilator --sc --exe --assert -Wall -CFLAGS "-std=c++17" \
    <block>.sv tb_<block>.cpp -o tb_<block>
make -C obj_dir -f V<block>.mk
```

- Add `--trace-fst` or `--coverage` only when the source guards and requested run need that artifact
- `-CFLAGS -I` paths are relative to `obj_dir/`, not the project root (e.g. `-CFLAGS "-I../verif/common"` for `verif/common/tb_log.h`)
- Export `SYSTEMC_INCLUDE`/`SYSTEMC_LIBDIR` if SystemC is not in the default prefix

### Gotchas

| Gotcha | Problem | Fix |
|--------|---------|-----|
| Calling `eval()` in SystemC flow | SystemC kernel handles evaluation | Only use `eval()` in pure C++ (`--cc`) testbenches; in SystemC (`--sc`), `sc_start()` manages evaluation |
| Calling `eval()` twice to “settle” C++ flow | A single `eval()` already performs internal settling | Call once after each input/time change; evaluate again only after another state change |
| `trace()` before elaboration | Verilator 5.x aborts: "trace() is called before sc_core::sc_start()" | Run `sc_start(SC_ZERO_TIME);` before `dut->trace()` |
| C++ standard below 17 | SystemC 3.x `#error`s at compile time | `set(CMAKE_CXX_STANDARD 17)` / `-std=c++17` |
| Missing `verilated_cov.h` | "member access into incomplete type 'VerilatedCovContext'" | Include it wherever `coveragep()` is called |
| Coverage written before `final()` | Counters not yet flushed — undercounts | Call `dut->final()` first, then `coveragep()->write()` |
| Missing `final()` | Resource leaks, incomplete coverage data | Call `dut->final()` before `dut` goes out of scope |
| Trace not enabled | `trace()` silently does nothing | Call `Verilated::traceEverOn(true)` **before** creating `VerilatedFstSc` |
| `contextp()->time()` vs `sc_time_stamp()` | Wrong time value in SystemC context | In SystemC testbenches, use `sc_time_stamp()` |

---

## Section 3: Logging Macro Reference

### Macro Definitions

```cpp
#define TB_LOG(verbosity, msg) \
    SC_REPORT_INFO_VERB(name(), msg, verbosity)

#define TB_LOG_LOW(msg)    TB_LOG(SC_LOW, msg)
#define TB_LOG_MEDIUM(msg) TB_LOG(SC_MEDIUM, msg)
#define TB_LOG_HIGH(msg)   TB_LOG(SC_HIGH, msg)
#define TB_LOG_DEBUG(msg)  TB_LOG(SC_DEBUG, msg)
```

### Message Formatting

`SC_REPORT_INFO_VERB` takes `const char*` for `msg`. Use string formatting, **not** iostream `<<`.

```cpp
// fmt::format (if fmt library available):
TB_LOG_MEDIUM(fmt::format("Driving a=0x{:x} b=0x{:x}", a_val, b_val).c_str());

// std::format (C++20):
TB_LOG_MEDIUM(std::format("Driving a=0x{:x} b=0x{:x}", a_val, b_val).c_str());

// std::ostringstream fallback:
std::ostringstream oss;
oss << "Driving a=0x" << std::hex << a_val << " b=0x" << b_val;
TB_LOG_MEDIUM(oss.str().c_str());
```

### Verbosity Levels

| Level | Value | Use For | Example |
|-------|-------|---------|---------|
| `SC_NONE` | 0 | Suppressed | — |
| `SC_LOW` | 100 | Test pass/fail, phase transitions | `"Reset complete"`, `"ALL TESTS PASSED"` |
| `SC_MEDIUM` | 200 | Stimulus/response, expected vs actual | `"Driving a=0x5 b=0xa"`, `"CHECK: expected=0xf actual=0xf PASS"` |
| `SC_HIGH` | 300 | Signal detail, FSM transitions | `"State: IDLE -> ACTIVE"`, `"handshake: valid=1 ready=0"` |
| `SC_FULL` | 400 | Detailed internal state | `"Scoreboard queue depth: 5"` |
| `SC_DEBUG` | 500 | Every cycle, raw values | `"cycle 42: clk=1 rst_n=1 a=0x5 b=0xa sum=0xf"` |

### Runtime Control

```cpp
// Set global verbosity threshold
sc_report_handler::set_verbosity_level(SC_HIGH);

// Silence a specific block. The string must exactly match the report type;
// TB_LOG uses name(), so use the module's full hierarchical name.
sc_report_handler::set_actions("tb.driver", SC_INFO, SC_DO_NOTHING);
```

`set_actions()` controls what happens after a report reaches the report
handler; it does not override verbosity. `SC_REPORT_INFO_VERB` drops messages
above the global threshold before consulting actions. To enable `SC_DEBUG` for
one module while keeping another at `SC_LOW`, add per-module thresholds to the
logging wrapper (or use separate logging objects) and keep the global threshold
at least as high as the highest message that any module may emit.

**Command-line verbosity:** SystemC has no built-in CLI parsing — no `--sc_verbosity` flag exists. Parse a `+verbosity=<LEVEL>` plusarg yourself in `sc_main` and feed the result to `set_verbosity_level()` (see `parse_verbosity()` in example-testbench.cpp).

---

## Section 4: Transaction and Scoreboard Rules

### Ready/Valid Acceptance

Treat driving `valid` and payload as a transaction attempt. Add an expected
result exactly once, when `valid && ready` is sampled on the protocol's
acceptance edge. If `ready` is low, hold or retry the request as required by
the protocol, but do not enqueue another expectation on each stalled cycle.

The output Monitor performs the inverse operation: when output
`valid && ready` is sampled, an expectation must exist. An output handshake
with an empty scoreboard is an unexpected-output failure.

### Multi-Channel and Out-of-Order Protocols

A FIFO queue is sufficient only for strictly in-order responses. For AXI-like
protocols, channel Drivers and Monitors remain separate, while a shared
transaction-level scoreboard:

- correlates independently accepted address and data channels;
- updates the reference model only after the required handshakes occur;
- tracks outstanding requests by transaction ID; and
- enforces ordering within each ID while permitting protocol-legal reordering
  between IDs.

### Negative Expectations

Tests such as “no response while disabled” should not push a dummy expected
value. Register a bounded observation window instead, and fail if the Monitor
sees a forbidden output handshake during that window.
