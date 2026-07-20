// =============================================================================
// example-testbench.cpp — SystemC testbench for a 4-bit adder (Vadder)
//
// This file is a fully annotated reference testbench demonstrating the
// canonical structure for Verilator + SystemC verification.  It tests a
// combinational 4-bit adder with ports: clk, rst_n, a[3:0], b[3:0], sum[4:0]
// (see adder.sv in this directory).
//
// Build & run (CMake — see CMakeLists.txt in this directory):
//   cmake -B build
//   cmake --build build
//   ./build/tb_adder                    # default verbosity (SC_MEDIUM)
//   ./build/tb_adder +verbosity=DEBUG   # every-cycle detail
// =============================================================================

// ---------------------------------------------------------------------------
// Includes — ordered per Google C++ Style adapted for Verilator:
//   1. Verilator model header (the DUT)
//   2. Verilator infrastructure
//   3. SystemC
//   4. C++ standard library
//
// <systemc> (no .h) keeps everything inside namespace sc_core.  A
// using-directive is acceptable in a .cpp file — never in a header.
// ---------------------------------------------------------------------------
#include "Vadder.h"

#include "verilated.h"
#include "verilated_cov.h"     // VerilatedCovContext — required for coverage write
#include "verilated_fst_sc.h"  // FST tracing in the SystemC flow

#include <systemc>

#include <cstdint>
#include <cstring>
#include <memory>
#include <queue>
#include <sstream>
#include <string>

using namespace sc_core;

// CMake defines this as its binary directory. The raw Verilator CLI fallback
// leaves it as the current working directory.
#ifndef TB_OUTPUT_DIR
#define TB_OUTPUT_DIR "."
#endif

static std::string output_path(const char* filename) {
    return std::string{TB_OUTPUT_DIR} + "/" + filename;
}

// ---------------------------------------------------------------------------
// Logging macros — thin wrappers around SC_REPORT_INFO_VERB.
// SC_REPORT takes a const char*, so callers build strings with ostringstream
// and pass .str().c_str().  The verbosity parameter lets us control noise:
//   SC_LOW    — always visible (summaries, final pass/fail)
//   SC_MEDIUM — per-transaction messages (default visibility)
//   SC_HIGH   — detailed internal state
//   SC_DEBUG  — extremely verbose (enable with +verbosity=DEBUG)
// ---------------------------------------------------------------------------
#define TB_LOG(verbosity, msg) SC_REPORT_INFO_VERB(name(), msg, verbosity)
#define TB_LOG_LOW(msg)    TB_LOG(SC_LOW, msg)
#define TB_LOG_MEDIUM(msg) TB_LOG(SC_MEDIUM, msg)
#define TB_LOG_HIGH(msg)   TB_LOG(SC_HIGH, msg)
#define TB_LOG_DEBUG(msg)  TB_LOG(SC_DEBUG, msg)

// ---------------------------------------------------------------------------
// Runtime verbosity control — SystemC has NO built-in command-line parsing.
// We parse a +verbosity=<LEVEL> plusarg ourselves in sc_main.
// ---------------------------------------------------------------------------
static sc_verbosity parse_verbosity(int argc, char* argv[]) {
    for (int i = 1; i < argc; ++i) {
        if (std::strncmp(argv[i], "+verbosity=", 11) != 0) continue;
        const std::string level{argv[i] + 11};
        if (level == "LOW")    return SC_LOW;
        if (level == "MEDIUM") return SC_MEDIUM;
        if (level == "HIGH")   return SC_HIGH;
        if (level == "FULL")   return SC_FULL;
        if (level == "DEBUG")  return SC_DEBUG;
        SC_REPORT_WARNING("tb", ("Unknown +verbosity= level: " + level).c_str());
    }
    return SC_MEDIUM;  // default: DRIVE/CHECK messages visible
}

// ---------------------------------------------------------------------------
// Scoreboard state shared by Driver, Monitor, and CompletionController.
// A passing run requires every queued expectation to be checked; zero
// mismatches alone is not sufficient.
// ---------------------------------------------------------------------------
struct Scoreboard {
    std::queue<uint32_t> expected;
    unsigned expected_count = 0;
    unsigned check_count = 0;
    unsigned pass_count = 0;
    unsigned fail_count = 0;
    unsigned unexpected_count = 0;
    bool stimulus_done = false;
    bool timed_out = false;

    bool passed() const {
        return stimulus_done && !timed_out && expected.empty()
               && check_count == expected_count && fail_count == 0
               && unexpected_count == 0;
    }
};

// ---------------------------------------------------------------------------
// ResetGen — dedicated reset thread.
//
// Keeping reset in its own SC_MODULE (rather than inlined in the Driver)
// makes the sequence reusable and extensible: multi-stage resets, mid-test
// reset injection, or per-domain resets all slot in here without touching
// stimulus code.
// ---------------------------------------------------------------------------
SC_MODULE(ResetGen) {
    sc_in<bool> clk;
    sc_out<bool> rst_n;

    SC_CTOR(ResetGen) {
        SC_THREAD(reset_thread);
        sensitive << clk.pos();
    }

    void reset_thread() {
        rst_n.write(false);
        TB_LOG_LOW("Reset asserted");
        wait();  // hold reset for two clock cycles
        wait();
        rst_n.write(true);
        TB_LOG_LOW("Reset released");
    }
};

// ---------------------------------------------------------------------------
// Driver — generates stimulus and feeds expected results to the scoreboard.
//
// The driver owns an SC_THREAD that waits for reset release, then calls one
// helper per T-xx test-plan item. Each helper logs its test ID and uses the
// common drive-and-expect primitive.
// ---------------------------------------------------------------------------
SC_MODULE(Driver) {
    sc_in<bool> clk;
    sc_in<bool> rst_n;
    sc_out<uint32_t> a;
    sc_out<uint32_t> b;

    // Non-owning pointer. The scoreboard is owned by the top-level testbench.
    Scoreboard* scoreboard;

    SC_CTOR(Driver) : scoreboard(nullptr) {
        SC_THREAD(drive_thread);
        sensitive << clk.pos();
    }

    void drive_and_expect(uint32_t a_value, uint32_t b_value) {
        a.write(a_value);
        b.write(b_value);

        // This combinational DUT has no ready/valid handshake, so the input
        // is accepted when driven. Handshaked protocols enqueue only when
        // valid && ready is sampled on the acceptance edge.
        const uint32_t expected = a_value + b_value;
        scoreboard->expected.push(expected);
        ++scoreboard->expected_count;

        std::ostringstream oss;
        oss << "DRIVE: a=0x" << std::hex << a_value
            << " b=0x" << b_value
            << " expected_sum=0x" << expected;
        TB_LOG_MEDIUM(oss.str().c_str());

        wait();
    }

    void test_zero_inputs() {  // T-01
        TB_LOG_MEDIUM("=== T-01: Zero inputs ===");
        drive_and_expect(0x0, 0x0);
    }

    void test_without_carry() {  // T-02
        TB_LOG_MEDIUM("=== T-02: Addition without carry-out ===");
        drive_and_expect(0x1, 0x1);
        drive_and_expect(0x7, 0x1);
    }

    void test_with_carry() {  // T-03
        TB_LOG_MEDIUM("=== T-03: Addition with carry-out ===");
        drive_and_expect(0x8, 0x8);
    }

    void test_max_inputs() {  // T-04
        TB_LOG_MEDIUM("=== T-04: Maximum inputs ===");
        drive_and_expect(0xF, 0xF);
    }

    void drive_thread() {
        // Wait for the dedicated reset generator to release rst_n.
        while (!rst_n.read()) {
            wait();
        }
        wait();  // one cycle of margin after reset release

        test_zero_inputs();
        test_without_carry();
        test_with_carry();
        test_max_inputs();

        scoreboard->stimulus_done = true;
        TB_LOG_LOW("Stimulus complete; waiting for scoreboard drain");
    }
};

// ---------------------------------------------------------------------------
// Monitor — samples DUT outputs and compares against the scoreboard.
//
// Samples on the negative edge of clk so that combinational outputs have
// settled after the positive-edge stimulus.  This half-cycle offset is a
// common verification pattern to avoid races.
// ---------------------------------------------------------------------------
SC_MODULE(Monitor) {
    sc_in<bool> clk;
    sc_in<bool> rst_n;
    sc_in<uint32_t> sum;

    Scoreboard* scoreboard;

    SC_CTOR(Monitor) : scoreboard(nullptr) {
        SC_THREAD(monitor_thread);
        sensitive << clk.neg();  // sample on negedge — outputs are stable
    }

    void monitor_thread() {
        // Wait until reset is released before checking anything.
        while (!rst_n.read()) {
            wait();
        }
        // One extra cycle so the first driven data has propagated.
        wait();

        while (true) {
            if (scoreboard->expected.empty()) {
                wait();
                continue;
            }

            const uint32_t expected = scoreboard->expected.front();
            scoreboard->expected.pop();
            const uint32_t actual = sum.read();
            ++scoreboard->check_count;

            const bool ok = (expected == actual);
            if (ok) {
                ++scoreboard->pass_count;
            } else {
                ++scoreboard->fail_count;
            }

            std::ostringstream oss;
            oss << "CHECK: expected=0x" << std::hex << expected
                << " actual=0x" << actual
                << (ok ? " PASS" : " **FAIL**");
            TB_LOG_MEDIUM(oss.str().c_str());

            wait();
        }
    }

};

// ---------------------------------------------------------------------------
// CompletionController — stops only after stimulus completes and all expected
// responses have been checked. Both phases are bounded so a stuck testbench
// fails instead of hanging forever.
// ---------------------------------------------------------------------------
SC_MODULE(CompletionController) {
    sc_in<bool> clk;
    Scoreboard* scoreboard;

    static constexpr unsigned kStimulusTimeoutCycles = 100;
    static constexpr unsigned kDrainTimeoutCycles = 20;

    SC_CTOR(CompletionController) : scoreboard(nullptr) {
        SC_THREAD(control_thread);
        sensitive << clk.neg();
    }

    void control_thread() {
        unsigned cycles = 0;
        while (!scoreboard->stimulus_done
               && cycles < kStimulusTimeoutCycles) {
            wait();
            ++cycles;
        }

        if (!scoreboard->stimulus_done) {
            scoreboard->timed_out = true;
            TB_LOG_LOW("TIMEOUT: stimulus did not complete");
            sc_stop();
            return;
        }

        cycles = 0;
        while (!scoreboard->expected.empty()
               && cycles < kDrainTimeoutCycles) {
            wait();
            ++cycles;
        }

        if (!scoreboard->expected.empty()) {
            scoreboard->timed_out = true;
            std::ostringstream oss;
            oss << "TIMEOUT: " << scoreboard->expected.size()
                << " expected response(s) remain";
            TB_LOG_LOW(oss.str().c_str());
        }
        sc_stop();
    }
};

// ---------------------------------------------------------------------------
// Testbench — owns and connects the DUT, clock, signals, verification agents,
// and shared scoreboard. sc_main is limited to runtime and artifact setup.
// ---------------------------------------------------------------------------
SC_MODULE(Testbench) {
    sc_clock clk;
    sc_signal<bool> rst_n;
    sc_signal<uint32_t> a;
    sc_signal<uint32_t> b;
    sc_signal<uint32_t> sum;

    std::unique_ptr<Vadder> dut;
    Scoreboard scoreboard;
    ResetGen reset_gen;
    Driver driver;
    Monitor monitor;
    CompletionController completion;

    SC_CTOR(Testbench)
        : clk{"clk", 10, SC_NS},
          rst_n{"rst_n"},
          a{"a"},
          b{"b"},
          sum{"sum"},
          dut{std::make_unique<Vadder>("dut")},
          reset_gen{"reset_gen"},
          driver{"driver"},
          monitor{"monitor"},
          completion{"completion"} {
        dut->clk(clk);
        dut->rst_n(rst_n);
        dut->a(a);
        dut->b(b);
        dut->sum(sum);

        reset_gen.clk(clk);
        reset_gen.rst_n(rst_n);

        driver.clk(clk);
        driver.rst_n(rst_n);
        driver.a(a);
        driver.b(b);
        driver.scoreboard = &scoreboard;

        monitor.clk(clk);
        monitor.rst_n(rst_n);
        monitor.sum(sum);
        monitor.scoreboard = &scoreboard;

        completion.clk(clk);
        completion.scoreboard = &scoreboard;
    }

    bool report() const {
        std::ostringstream summary;
        summary << "SUMMARY: " << scoreboard.pass_count << " passed, "
                << scoreboard.fail_count << " failed, "
                << scoreboard.check_count << "/"
                << scoreboard.expected_count << " checked, "
                << scoreboard.expected.size() << " pending, "
                << scoreboard.unexpected_count << " unexpected, timeout="
                << (scoreboard.timed_out ? "yes" : "no");
        TB_LOG_LOW(summary.str().c_str());
        return scoreboard.passed();
    }
};

// ---------------------------------------------------------------------------
// sc_main — runtime entry point.
//
// Responsibilities:
//   1. Initialize Verilator and SystemC runtime
//   2. Instantiate the top-level Testbench
//   3. Elaborate, then set up FST waveform tracing
//   4. Run simulation
//   5. Report results and clean up
// ---------------------------------------------------------------------------
int sc_main(int argc, char* argv[]) {
    // Let Verilator parse its own plusargs (e.g. +verilator+rand+reset+2).
    Verilated::commandArgs(argc, argv);

    // Enable tracing infrastructure before any model is constructed.
    Verilated::traceEverOn(true);

    // Default SC_MEDIUM shows DRIVE/CHECK; override with +verbosity=<LEVEL>.
    sc_report_handler::set_verbosity_level(parse_verbosity(argc, argv));

    Testbench tb{"tb"};

    // --- Complete elaboration BEFORE trace setup ---
    // Verilator 5.x registers the model's SystemC processes during
    // elaboration; calling trace() earlier aborts with
    // "trace() is called before sc_core::sc_start()".
    sc_start(SC_ZERO_TIME);

    // --- FST tracing setup (VerilatedFstSc auto-dumps in SystemC flow) ---
    auto tfp = std::make_unique<VerilatedFstSc>();
    tb.dut->trace(tfp.get(), 99);        // 99 levels of hierarchy
    const std::string trace_path = output_path("tb_adder.fst");
    tfp->open(trace_path.c_str());

    // --- Run until the completion controller calls sc_stop() ---
    sc_start();

    // --- Post-simulation cleanup ---
    tb.dut->final();    // Runs RTL final blocks and flushes coverage counters
    tfp->close();       // Flush and close the waveform file

    // Write coverage data — AFTER final(), which flushes the counters.
    const std::string coverage_path = output_path("coverage.dat");
    Verilated::threadContextp()->coveragep()->write(coverage_path);

    // Print a completion-aware summary and derive the exit code.
    return tb.report() ? 0 : 1;
}
