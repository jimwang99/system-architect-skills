---
name: write-hardware-model-with-tlm
description: Use when writing or reviewing TLM models — TLM-2.0 sockets, generic payload, b_transport/nb_transport, DMI, interconnects, quantum keeper, or TLM-1 message passing. For signal-level SC_MODULE models use write-systemc.
---

# Write TLM models

Target TLM-2.0 as standardized in IEEE Std 1666-2023 (SystemC 3.0, C++17). Snippets are trimmed from the Accellera reference `examples/tlm/common`.

## Style choice

- Loosely-timed (LT): `b_transport` + DMI + temporal decoupling — virtual platforms, speed first.
- Approximately-timed (AT): `nb_transport` with BEGIN_REQ → END_REQ → BEGIN_RESP → END_RESP — architecture/performance analysis. Do not combine AT with temporal decoupling.
- TLM-1 (`put`/`get`, `tlm_fifo`) only for untimed, non-memory-mapped message passing; `tlm_analysis_port` for monitors/scoreboards (non-blocking, subscribers deep-copy).

## Sockets

- Use `tlm_utils::simple_initiator_socket<T>` / `simple_target_socket<T>`, named in the constructor, and register only the callbacks you implement; `simple_target_socket` auto-converts b/nb so a pure-LT target still works under an AT initiator.
- Use `*_tagged` variants for socket arrays (the tag routes callbacks), `*_optional` for legitimately unbound sockets.

```cpp
tlm_utils::simple_target_socket<lt_target> m_socket;      // member
lt_target::lt_target(sc_module_name name) : sc_module(name), m_socket("m_socket") {
  m_socket.register_b_transport(this, &lt_target::custom_b_transport);
  m_socket.register_get_direct_mem_ptr(this, &lt_target::get_direct_mem_ptr);
}
```

## Generic payload and memory management

- Initialize every attribute before each send — pooled payloads carry stale values. `streaming_width == data_length` when not streaming; data/byte-enable arrays are initiator-owned and must outlive the transaction.

```cpp
txn->acquire();                                        // ref count while in flight
txn->set_command(tlm::TLM_WRITE_COMMAND);
txn->set_address(addr);
txn->set_data_ptr(data);  txn->set_data_length(len);
txn->set_streaming_width(len);
txn->set_byte_enable_ptr(nullptr);
txn->set_dmi_allowed(false);
txn->set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);
// ... transport, check status ...
txn->release();                                        // mm recycles at ref count 0
```

- Pool transactions through `tlm_mm_interface`; every transaction sent via `nb_transport` must have a memory manager:

```cpp
class tg_queue_c : public tlm::tlm_mm_interface {
  void enqueue() { m_queue.push(new tlm::tlm_generic_payload(this)); }  // this = mm
  void free(tlm::tlm_generic_payload* txn) override {
    txn->reset();                                      // deletes auto extensions
    m_queue.push(txn);                                 // recycle
  }
  std::queue<tlm::tlm_generic_payload*> m_queue;
};
```

- Modification rights after send: initiator — extensions only; target — response status, DMI hint, extensions, data array (reads only); interconnect — address, extensions, clearing the DMI hint. Nothing else.
- Extensions: derive `tlm_extension<T>`, implement `clone`/`copy_from`, attach with `set_auto_extension` under a mm. Ignorable extensions keep `tlm_base_protocol_types`; a mandatory extension requires a new protocol traits class.

## Response status

- Target sets the most specific error (`TLM_ADDRESS_ERROR_RESPONSE`, `TLM_COMMAND_ERROR_RESPONSE`, `TLM_BURST_ERROR_RESPONSE`, `TLM_BYTE_ENABLE_ERROR_RESPONSE`) or `TLM_OK_RESPONSE` — never `SC_REPORT_ERROR` for a bus error the initiator can handle.
- Initiator checks `is_response_ok()` after every call; a status still `TLM_INCOMPLETE_RESPONSE` means no target executed it (misroute). Interconnects never touch status.

## LT: b_transport

- Call only from threads (target may `wait`). Target adds its latency to the delay argument and returns without waiting; initiator consumes the delay:

```cpp
// initiator thread
sc_time delay = SC_ZERO_TIME;
socket->b_transport(*txn, delay);
if (txn->is_response_ok()) wait(delay);      // consume the annotation locally

// target callback
void custom_b_transport(tlm_generic_payload& gp, sc_time& delay) {
  memory_operation(gp);                      // read/write + set response status
  delay += m_accept_delay + m_op_delay;      // annotate instead of wait()
}
```

- Temporal decoupling: one global quantum, one `tlm_quantumkeeper` per initiator thread (`reset()` after construction); yield only at quantum boundaries; `sync()` before touching state shared with other initiators:

```cpp
m_delay = m_qk.get_local_time();             // pass accumulated local offset
socket->b_transport(*txn, m_delay);
m_qk.set(m_delay);                           // absorb returned annotation
if (m_qk.need_sync()) m_qk.sync();           // wait() only at the boundary
```

## AT: nb_transport

- Never `wait()` inside `nb_transport_fw`/`nb_transport_bw`; schedule annotated work through a PEQ and issue later phases from a process. Return codes: `TLM_ACCEPTED` = nothing changed, wait for a backward call; `TLM_UPDATED` = re-inspect phase/delay; `TLM_COMPLETED` = done on this socket (still check status).
- Exclusion rules per socket: no new BEGIN_REQ before END_REQ (or completion) of the previous request; judged by call order, never by delay values.
- 4-phase target skeleton — two PEQs, each drained by an `SC_METHOD`:

```cpp
// members: peq_with_get<tlm_generic_payload> m_end_req_PEQ, m_resp_PEQ;
// ctor: SC_METHOD(end_req_method); sensitive << m_end_req_PEQ.get_event(); dont_initialize();
tlm_sync_enum nb_transport_fw(tlm_generic_payload& gp, tlm_phase& phase, sc_time& delay) {
  switch (phase) {
  case tlm::BEGIN_REQ: m_end_req_PEQ.notify(gp, delay + m_accept_delay);
                       return tlm::TLM_ACCEPTED;
  case tlm::END_RESP:  m_end_resp_event.notify(delay); return tlm::TLM_COMPLETED;
  default:             /* END_REQ/BEGIN_RESP illegal on fw path */ return tlm::TLM_ACCEPTED;
  }
}
void end_req_method() {                        // drain: loop until NULL
  while (auto* txn = m_end_req_PEQ.get_next_transaction()) {
    tlm_phase phase = tlm::END_REQ; sc_time delay = SC_ZERO_TIME;
    m_socket->nb_transport_bw(*txn, phase, delay);
    m_resp_PEQ.notify(*txn, m_op_delay);       // schedule BEGIN_RESP
  }
}
void begin_resp_method() {
  next_trigger(m_resp_PEQ.get_event());
  while (auto* txn = m_resp_PEQ.get_next_transaction()) {
    memory_operation(*txn);                    // sets data + status
    tlm_phase phase = tlm::BEGIN_RESP; sc_time delay = SC_ZERO_TIME;
    tlm_sync_enum s = m_socket->nb_transport_bw(*txn, phase, delay);
    if (s == tlm::TLM_ACCEPTED) { next_trigger(m_end_resp_event); break; }
  }
}
```

## DMI

- Only the target grants: set `set_dmi_allowed(true)` in transport as the hint, fill `tlm_dmi` in `get_direct_mem_ptr`, and call `invalidate_direct_mem_ptr(start, end)` before anything invalidates the region. Never grant over side-effect regions; never `wait` in DMI methods.

```cpp
bool get_direct_mem_ptr(tlm_generic_payload& gp, tlm::tlm_dmi& dmi) {
  if (!m_dmi_enabled || gp.get_address() > m_end_address) return false;
  dmi.allow_read_write();
  dmi.set_start_address(m_start); dmi.set_end_address(m_end);
  dmi.set_dmi_ptr(m_mem_ptr);
  dmi.set_read_latency(m_rd_delay); dmi.set_write_latency(m_wr_delay);
  return true;
}
```

- Initiator: request the pointer only after the `is_dmi_allowed()` hint, restore the payload address first (interconnects mutate it), register the invalidate callback and drop overlapping cached pointers immediately, always ready to fall back to transport:

```cpp
if (gp->is_dmi_allowed()) {
  gp->set_address(m_address);                  // restore before DMI request
  m_dmi.init();
  if (socket->get_direct_mem_ptr(*gp, m_dmi)) cache_dmi(m_dmi);
}
```

## Debug transport and interconnects

- `transport_dbg`: copy bytes immediately, no side effects, no delay, no notifications; return bytes actually transferred (0 if unable).
- Interconnects route from address/command only, modify the address only on the forward path, and pass all three mechanisms — transport, DMI, debug — through the same decode; DMI invalidations broadcast to all initiators after inverse range translation:

```cpp
void b_transport_cb(int /*tag*/, tlm_generic_payload& trans, sc_time& t) {
  unsigned port = decode(trans.get_address());
  trans.set_address(trans.get_address() & mask(port));   // forward-path only
  initiator_socket[port]->b_transport(trans, t);
}
void invalidate_cb(int port, sc_dt::uint64 start, sc_dt::uint64 end) {
  if (!to_bus_range(port, start, end)) return;           // inverse translation
  for (unsigned i = 0; i < N_INIT; ++i)
    target_socket[i]->invalidate_direct_mem_ptr(start, end);
}
```

- Endianness: keep payload data as a host-endian memcpy image; convert with `tlm_to_hostendian_word` / `tlm_from_hostendian_word` when modeled endianness differs — never hand-swap.

## Notes

- SystemC 3.0 deprecates no TLM API. From core SystemC: no `SC_HAS_PROCESS`; `SC_INCLUDE_DYNAMIC_PROCESSES` is gone (sc_spawn is always available). IEEE Std 1666-2023 is the normative TLM reference, not the old OSCI TLM-2.0 LRM.
