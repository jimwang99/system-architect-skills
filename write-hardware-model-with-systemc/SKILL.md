---
name: write-hardware-model-with-systemc
description: Use when writing or reviewing SystemC models — SC_MODULE, signals/channels, SC_METHOD/SC_THREAD/SC_CTHREAD processes, custom channels, sc_main setup. For TLM socket/generic-payload models use write-tlm; for SystemC testbenches driving Verilator RTL use write-hardware-test-bench.
---

# Write SystemC models

Target IEEE Std 1666-2023 (SystemC 3.0), C++17, `#include <systemc.h>`. Snippets are trimmed from the Accellera reference `examples/sysc`.

## Modules

- Constructor takes `sc_module_name` by value; forward it to `sc_module`. Register processes directly in the constructor (`SC_HAS_PROCESS` is deprecated).
- Name every module, signal, and clock after its C++ variable: `SC_NAMED(x)` or `x{"x"}`. Use `sc_vector`, never C arrays of ports/signals.
- `sensitive << ...` and `dont_initialize()` apply to the most recently registered process — keep them right under the registration.

```cpp
SC_MODULE(adder) {
  sc_out<int>           SC_NAMED(res);
  sc_vector<sc_in<int>> SC_NAMED(din, N_INPUTS);
  SC_CTOR(adder) {
    SC_METHOD(add_method);
    for (auto& d : din) sensitive << d;
    dont_initialize();                 // skip the time-zero evaluation
  }
  void add_method() { int s = 0; for (auto& d : din) s += d.read(); res.write(s); }
};
```

```cpp
// Extra constructor parameters: take sc_module_name first, no macro needed.
master(sc_module_name name_, unsigned priority, bool lock)
  : sc_module(name_), m_priority(priority), m_lock(lock) {
  SC_THREAD(main_action);
  sensitive << clock.pos();
}
```

## Processes

- `SC_METHOD`: runs to completion in zero time. `wait()` — including blocking `sc_fifo` `read()`/`write()` — is a fatal error inside it; re-arm with `next_trigger(...)`.
- `SC_THREAD`: infinite loop plus `wait()`; use for stimulus and anything keeping local state. Bare `wait()` waits on static sensitivity; `wait(10, SC_NS)` for time.
- `SC_CTHREAD(entry, clk.pos())`: clocked, synthesis-oriented; only `wait()`/`wait(n)` inside.
- Clocked threads get `reset_signal_is(reset, true)` (or `async_reset_signal_is`); body = reset outputs, one `wait()`, then the loop. Reset restarts the body from the top.

```cpp
SC_CTOR(fir) { SC_CTHREAD(entry, CLK.pos()); reset_signal_is(reset, true); }
void fir::entry() {
  result.write(0); output_data_ready.write(false);   // reset section
  wait();
  while (1) {
    do { wait(); } while (!input_valid.read());      // handshake wait
    // ... compute acc from sample.read() ...
    result.write(acc); output_data_ready.write(true); wait();
  }
}
```

## Signals and determinism

- Pass data between processes only through channels (`sc_signal`, `sc_fifo`, interface-method calls); plain members only for state one process owns. Channels defer updates, so results stay independent of process order.
- One writer process per `sc_signal` (two writers in one delta = error E115). Access with explicit `.read()`/`.write()`.
- A write becomes visible in the next delta cycle:

```cpp
count.write(count.read() + 1);
int now = count.read();      // still the OLD value
wait(SC_ZERO_TIME);          // thread: one delta (method: next_trigger(SC_ZERO_TIME))
int now2 = count.read();     // updated value
```

- Custom channel: interfaces derive `virtual public sc_interface`; channel derives `sc_channel` + interfaces; block callers with `sc_event`:

```cpp
class write_if : virtual public sc_interface { public: virtual void write(char) = 0; };
class fifo : public sc_channel, public write_if, public read_if {
  void write(char c) override {
    if (num_elements == max) wait(read_event);   // block until space
    data[(first + num_elements) % max] = c;
    ++num_elements; write_event.notify();
  }
  // read(): wait(write_event) when empty, then read_event.notify()
  sc_event write_event, read_event;              // members = channel-private state
};
```

- A struct carried by `sc_signal` needs `operator==`, `operator<<`, and an `sc_trace` overload:

```cpp
struct pkt { sc_int<8> data; bool dest0;
  bool operator==(const pkt& r) const { return r.data == data && r.dest0 == dest0; } };
inline std::ostream& operator<<(std::ostream& os, const pkt&) { return os << "pkt"; }
inline void sc_trace(sc_trace_file* tf, const pkt& p, const std::string& n) {
  sc_trace(tf, p.data, n + ".data"); sc_trace(tf, p.dest0, n + ".dest0");
}
```

## Ports, exports, binding

- Bind every port before `sc_start()` (unbound = error E109). Bind by name: `inst.port(sig)`.
- `sc_port<if_type, 0>` = multiport for variable fan-out; bind once per channel, iterate `size()`/`operator[]`:

```cpp
sc_port<slave_if, 0> slave_port;              // bus side, any number of slaves
slave_if* get_slave(unsigned addr) {
  for (int i = 0; i < slave_port.size(); ++i)
    if (slave_port[i]->start_address() <= addr && addr <= slave_port[i]->end_address())
      return slave_port[i];
  return nullptr;
}
```

- `sc_export<if_type>` publishes an internal channel at the module boundary:

```cpp
SC_MODULE(D) {
  sc_export<C_if> IFP;
  SC_CTOR(D) : IFP("IFP"), m_C("C") { IFP(m_C); }  // export → internal channel
  C m_C;
};  // parent: IFP2(m_D.IFP);  outer port: x.P2(e.IFP2);
```

## Events, time, types

- Signal between processes with `event.notify(SC_ZERO_TIME)`; immediate `notify()` is lost if the receiver is not already waiting. An `sc_event` keeps only one pending notification — use `sc_event_queue` when every one must arrive.
- Spawn runtime processes with `sc_spawn` (+ `sc_spawn_options::spawn_method()` for methods).
- All durations are `sc_time(value, SC_NS)`-style; current time is `sc_time_stamp()`; set `sc_set_time_resolution()` at most once, before any non-zero `sc_time` exists.
- Types: native C++ by default; `sc_int/sc_uint<N>` for exact widths ≤ 64; `sc_bigint` only above 64 bits; `sc_logic`/`sc_lv` only where X/Z matters; `#define SC_INCLUDE_FX` before the include for fixed point.

## Reporting, tracing, sc_main

- Report via `SC_REPORT_INFO/WARNING/ERROR/FATAL("msg_type", "...")`, never `cout`/`exit()`; `sc_assert` for testbench checks.
- Register all `sc_trace(tf, obj, "name")` calls before simulation starts (late adds = error E720); close the file after `sc_start()` returns.

```cpp
int sc_main(int, char*[]) {
  sc_clock clock("clock", 10, SC_NS);
  sc_signal<bool> SC_NAMED(reset);  sc_signal<int> SC_NAMED(result);
  fir fir1("fir1");
  fir1.CLK(clock); fir1.reset(reset); fir1.result(result);  // bind by name
  sc_trace_file* tf = sc_create_vcd_trace_file("waves");
  sc_trace(tf, result, "result");
  sc_start(1, SC_MS);                 // bounded run, or let a process call sc_stop()
  sc_close_vcd_trace_file(tf);
  return 0;
}
```

- Nothing structural (modules, binding) after `sc_start()`; repeated `sc_start(t)` calls continue, never restart.

## Never use (deprecated in 1666-2023 / SystemC 3.0)

`SC_HAS_PROCESS` · `sensitive_pos`/`sensitive_neg`/`sensitive(sig)` (use `sensitive << port.pos()`) · positional binding with `<<` · `sc_initialize()`/`sc_cycle()`/`sc_simulation_time()` (use `sc_start`, `sc_time_stamp`) · `notify_delayed()` and free `notify(e)` (use `e.notify(SC_ZERO_TIME)`) · `sc_bit` (use `bool`) · `timed_out()` · `sc_simcontext` member calls (use free `sc_delta_count()`, `sc_find_object()`, `sc_get_current_process_handle()`) · all-double `sc_clock` constructor · integer report ids.
