---
name: write-hardware-rtl
description: Use when writing, reviewing, or modifying synthesizable SystemVerilog RTL for Verilator simulation
---

# Write Hardware RTL

## Overview

Synthesizable SystemVerilog, lowRISC style. Primary simulator: Verilator (two-state). Every module gets runtime-configurable logging, assertions, and coverage points — AI agents debug with text, not waveforms.

**Style reference:** [lowRISC Verilog Coding Style Guide](https://github.com/lowRISC/style-guides/blob/master/VerilogCodingStyle.md)

## Module Structure

Layout order:

1. Module declaration (ANSI ports, `clk_i`/`rst_ni` first)
2. Parameters & localparams
3. Logging setup (plusargs-based verbosity)
4. Signal declarations
5. Input assertions (cross-module contracts)
6. Core logic (combinational, sequential, FSMs)
7. Logging, output assertions (`ASSERT_KNOWN` + functional), coverage
8. Submodule instantiations (named ports, all ports connected)

**Skeleton:**

```systemverilog
module example #(
  parameter int unsigned Width = 8
) (
  input  logic             clk_i,
  input  logic             rst_ni,
  input  logic [Width-1:0] data_i,
  input  logic             valid_i,
  output logic             ready_o,
  output logic [Width-1:0] data_o
);

  // -- Logging --
  `ifndef SYNTHESIS
  int unsigned log_level;
  initial begin
    if (!$value$plusargs("LOG_EXAMPLE=%d", log_level))
      log_level = 1;
  end
  `endif

  // -- Signals --
  logic [Width-1:0] data_q, data_d;
  logic             valid_q, valid_d;

  // -- Input assertions --
  `ifndef SYNTHESIS
  always_ff @(posedge clk_i) begin
    if (rst_ni) begin
      ASSERT_VALID_KNOWN: assert (!$isunknown(valid_i))
        else $error("[%0t] example: valid_i is unknown", $time);
    end
  end
  `endif

  // -- Core logic --
  always_comb begin
    data_d  = data_i;
    valid_d = valid_i;
  end

  always_ff @(posedge clk_i or negedge rst_ni) begin
    if (!rst_ni) begin
      valid_q <= 1'b0;
      // data_q has no reset — gated by valid_q
    end else begin
      valid_q <= valid_d;
      data_q  <= data_d;
    end
  end

  assign ready_o = ~valid_q;
  assign data_o  = data_q;

  // -- Logging, output assertions, coverage --
  `ifndef SYNTHESIS
  always_ff @(posedge clk_i) begin
    if (rst_ni && log_level >= 3 && valid_i && ready_o)
      $display("[%0t] [INFO] %m: accepted data 0x%0h", $time, data_i);
  end

  always_ff @(posedge clk_i) begin
    if (rst_ni) begin
      ASSERT_READY_KNOWN: assert (!$isunknown(ready_o))
        else $error("[%0t] example: ready_o is unknown", $time);
      ASSERT_DATA_KNOWN:  assert (!valid_q || !$isunknown(data_o))
        else $error("[%0t] example: data_o unknown while valid", $time);
    end
  end

  CVR_VALID_ACCEPTED: cover property (@(posedge clk_i)
    valid_i && ready_o);
  `endif

endmodule
```

## Logging & Tracing

Agents cannot use waveform viewers — runtime text logging is the debug interface.

**Verbosity levels:**

| Level | Name | Use for |
|-------|------|---------|
| 0 | Silent | No output |
| 1 | Error | Protocol violations, illegal states (use `$error`) |
| 2 | Warn | Recoverable issues, edge cases hit |
| 3 | Info | State transitions, key events |
| 4 | Debug | Detailed internal signal values |

**Rules:**
- Each module reads its own verbosity via plusargs at time 0: `+LOG_<MODULE_NAME>=<level>` (uppercase module name). Default 1.
- Plusarg is per module type, not per instance — all instances share one level; `%m` in messages tells instances apart
- All messages include `$time`, `%m`, and level label
- Level 1 messages use `$error` to fail simulation on protocol violations
- Log from `always_ff` at clock edge only — `always_comb` re-evaluates every delta cycle and spams
- Wrap in `` `ifndef SYNTHESIS `` / `` `endif ``

**Runtime usage (no recompile):**
```bash
./Vtb +LOG_UART_TX=3 +LOG_FIFO=4
```

**Pattern:**
```systemverilog
`ifndef SYNTHESIS
int unsigned log_level;
initial begin
  if (!$value$plusargs("LOG_MY_MODULE=%d", log_level))
    log_level = 1;
end

always_ff @(posedge clk_i) begin
  if (log_level >= 3 && state_q != state_d)
    $display("[%0t] [INFO] %m: state %s -> %s", $time, state_q.name(), state_d.name());
end
`endif
```

## Assertions

Free after synthesis, immediate text feedback. When in doubt, add one.

**Priority order:**
1. **ASSERT_KNOWN** — all module outputs. Uses `$isunknown`. Won't fire in Verilator (two-state) but essential for VCS/Xcelium portability.
2. **Protocol** — handshake rules (valid/ready), FIFO overflow/underflow, bus compliance
3. **Range** — counters in bounds, enums valid, bit-widths match
4. **FSM** — no illegal state, dead state detection
5. **Cross-module contracts** — assert input assumptions at module boundary

**Rules:**
- Immediate assertions (`assert` in `always_ff`) and one-cycle concurrent (`assert property (@(posedge clk_i) <boolean>)`) only. `$past(expr)` OK for previous-cycle checks.
- **No** implication (`|->`, `|=>`), sequences (`##N`), or SERE. Verilator ≥5.x compiles some of these, but one-cycle booleans stay portable across versions and have no subtle sequence semantics — keep to them.
- **No** `inside` operator — explicit comparisons (`state_q == StIdle || state_q == StSend`)
- Every assertion: descriptive label + `$error` message with `$time`
- Gate with reset: immediate via `if (rst_ni)`, concurrent via `!rst_ni ||` term — otherwise fires on X during reset in 4-state simulators
- Wrap in `` `ifndef SYNTHESIS `` / `` `endif ``

**Examples:**
```systemverilog
`ifndef SYNTHESIS
// Concurrent — one-cycle boolean, reset-gated
ASSERT_TX_KNOWN: assert property (@(posedge clk_i) !rst_ni || !$isunknown(tx_o))
  else $error("[%0t] uart_tx: tx_o is unknown", $time);

// Immediate — in always_ff, explicit comparisons (no `inside`)
always_ff @(posedge clk_i) begin
  if (rst_ni) begin
    ASSERT_STATE_VALID: assert (
      state_q == StIdle || state_q == StSend || state_q == StStop
    ) else $error("[%0t] uart_tx: illegal state %0d", $time, state_q);
  end
end
`endif
```

## Linting

Every module must pass Verilator lint with zero warnings before done.

**Command:**
```bash
verilator --lint-only -Wall \
  -Wno-SYNCASYNCNET \
  -Werror-WIDTH -Werror-WIDTHTRUNC -Werror-WIDTHEXPAND \
  -Werror-BLKSEQ -Werror-BLKANDNBLK \
  -Werror-IMPLICIT -Werror-LATCH \
  -Werror-CASEINCOMPLETE -Werror-PINMISSING \
  -Werror-UNDRIVEN -Werror-MULTIDRIVEN \
  design.sv
```

`-Wno-SYNCASYNCNET`: sim-only assertion/logging blocks sample `rst_ni` synchronously (`if (rst_ni)`) while core logic uses it async — inherent to this style, fires on every module. Same waiver OpenTitan applies globally.

**Key warnings — never suppress:**

| Warning | Catches |
|---------|---------|
| `WIDTH` / `WIDTHTRUNC` / `WIDTHEXPAND` | Silent truncation or zero-extension |
| `BLKSEQ` / `BLKANDNBLK` | Blocking in sequential, mixed assignment styles |
| `IMPLICIT` | Undeclared wires (typo risk) |
| `LATCH` | Unintended latch inference |
| `CASEINCOMPLETE` | Missing case branches |
| `UNDRIVEN` / `MULTIDRIVEN` | Floating or conflicting drivers |
| `PINMISSING` | Unconnected ports in instantiation |

**Verilator `-G` and enum parameters:** `-G` override of an enum-typed parameter injects a 32-bit literal, triggering `WIDTHTRUNC`. Suppress with `-Wno-WIDTHTRUNC` in build flags only — keep `-Werror-WIDTHTRUNC` in lint flags.

**Inline suppression** (only with justification):
```systemverilog
// verilator lint_off WIDTH
// Intentional truncation: extracting lower byte from wider bus
assign byte_val = wide_bus;
// verilator lint_on WIDTH
```

## Coverage

Compile with `--coverage` during development to find untested paths.

**Commands:**
```bash
# Build with SystemC testbench + coverage
verilator --sc --exe --trace-fst --coverage -Wall \
    design.sv tb.cpp -o Vtb
make -C obj_dir -f Vdesign.mk

# Run
./obj_dir/Vtb

# View
verilator_coverage --annotate coverage_annotated coverage.dat
```

**Coverage types:**

| Type | Flag | Tracks |
|------|------|--------|
| Line | `--coverage-line` | Code flow/branch execution |
| Toggle | `--coverage-toggle` | Signal bit transitions |
| Functional | `--coverage-user` | User-defined `cover property` points |
| Expression | `--coverage-expr` | Boolean expression truth tables |
| All | `--coverage` | All of the above |

**Cover points for interesting scenarios** (same one-cycle + `$past` subset as assertions):
```systemverilog
`ifndef SYNTHESIS
CVR_FIFO_FULL:    cover property (@(posedge clk_i) fifo_full);
CVR_BACK_TO_BACK: cover property (@(posedge clk_i)
  valid_i && ready_o && $past(valid_i && ready_o));
`endif
```

**Exclude debug/logging code:**
```systemverilog
/*verilator coverage_off*/
// Debug-only logging block
/*verilator coverage_on*/
```

**Note:** No native FSM coverage in Verilator. Use manual `cover property` per state transition.

## Style Quick Reference

| Topic | Rule |
|-------|------|
| **Types** | `logic` only. No `reg`, `wire` (except `assign` shorthand), `bit` |
| **Signals** | `lower_snake_case`. Ports: `_i`, `_o`, `_io`. Active-low: `_n` before direction (`_ni`, `_no`) |
| **Clk/Rst** | `clk_i` (primary), `clk_<domain>_i`. Reset: `rst_ni` (active-low, async) |
| **Parameters** | `UpperCamelCase`, explicit types, reasonable defaults. Derived: `localparam` |
| **Sequential** | `always_ff @(posedge clk_i or negedge rst_ni)`, non-blocking (`<=`) only |
| **Combinational** | `always_comb`, blocking (`=`) only. Prefer `assign` where practical |
| **Case** | `unique case` with `default`. Use `casez` for don't-care bits |
| **Literals** | Explicit widths: `8'd2` not `2`. Auto-sized `'0`, `'1` OK |
| **FSMs** | Three-part: enum decl (`typedef enum logic`), combo decode (defaults first), sequential register |
| **Generate** | Always named blocks (`begin : gen_name`). No `generate`/`endgenerate` keywords |
| **Instantiation** | Named ports only. No positional, no `.*`. All ports must appear |
| **Formatting** | 2-space indent, 100 char line limit, no tabs |
| **Prohibited** | `case inside`, `inside` operator, `casex`, `defparam`, `#delay`, `X` assignments, latches, tasks, hierarchical refs, `reg`, bare `always` |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `reg`/`wire` instead of `logic` | `logic` for all signals |
| Mixing blocking/non-blocking in one block | `=` in `always_comb`, `<=` in `always_ff`, never mix |
| Resetting all flops including data paths | Control-path flops must reset. Data-path flops may omit reset **only** when gated by a reset valid signal. Add assertion + comment when omitting. |
| Unsized literals (`0`, `1`, `42`) | Explicit widths: `1'b0`, `8'd42`. Exception: `'0`, `'1` |
| No assertions on outputs | Every output gets `ASSERT_KNOWN` minimum |
| No logging infrastructure | Every module gets plusargs-based log level |
| Positional port connections | Named only: `.port_i(signal)` |
| Missing `default` in `case` | Every `unique case` needs `default` |
| Multi-bit signal in boolean context | Explicit compare: `if (data != '0)` not `if (data)` |
| Latch inference | Assign all signals in all `always_comb` branches, or defaults at top |
| FSM logic in sequential block | Three-part FSM: enum, combo decode, sequential register only |
| `case inside` / `inside` operator | `casez` for wildcards, explicit `==` for assertions |
| `|->`, `##N`, sequences in assertions | One-cycle booleans + `$past` only |
| Logging from `always_comb` | Delta-cycle spam. Log from `always_ff` only |
| Both `synthesis translate_off` and `` `ifndef SYNTHESIS `` | Use `` `ifndef SYNTHESIS `` — more portable |
| No lint check before done | Run the lint command above, fix all warnings |
| No coverage points | `cover property` for FSM transitions and interesting scenarios |
