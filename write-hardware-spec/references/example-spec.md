# Synchronous FIFO Specification

> **NON-NORMATIVE REFERENCE:** [`SKILL.md`](../SKILL.md) is the sole contract. This worked example illustrates one valid set of FIFO decisions; it does not make those decisions mandatory for other blocks.

Merged architecture and microarchitecture example for a single-clock, non-pipelined FIFO.

## Contents

- [Purpose](#purpose)
- [Parameters](#parameters)
- [Interfaces](#interfaces)
- [Functional Requirements](#functional-requirements)
- [Timing Requirements](#timing-requirements)
- [Reset-Visible Behavior](#reset-visible-behavior)
- [Non-Goals](#non-goals)
- [Block Diagram](#block-diagram)
- [Interface Timing](#interface-timing)
- [Implementation Detail](#implementation-detail)
- [Test Plan](#test-plan)

## Purpose

`sync_fifo` buffers an ordered stream between a producer and consumer in one clock domain. It absorbs producer bursts, applies backpressure at full occupancy, and prevents reads at empty occupancy. This example deliberately has no cut-through path and chooses conservative full-boundary behavior: a read may succeed while full, but a simultaneous write waits until the following cycle.

## Parameters

| Parameter | Type | Default | Legal Values / Constraints | Derived? | Description |
|-----------|------|---------|----------------------------|----------|-------------|
| DataWidth | int unsigned | 32 | >= 1 | No | Payload width in bits |
| Depth | int unsigned | 4 | Power of 2 and >= 2 | No | Number of stored entries |
| AddrWidth | int unsigned | $clog2(Depth) | Determined by Depth | Yes | Read/write pointer width |

Configurations with `DataWidth < 1`, `Depth < 2`, or non-power-of-two `Depth` are illegal and must fail elaboration. Pointer wrap uses binary truncation, so the power-of-two constraint is architectural for this implementation.

## Interfaces

### Clock and Reset

| Port | Direction | Width | Domain | Description |
|------|-----------|-------|--------|-------------|
| clk_i | input | 1 | — | Rising-edge clock |
| rst_ni | input | 1 | clk_i | Active-low asynchronous reset; deassertion is synchronous to `clk_i` |

### Write Channel

| Port | Direction | Width | Domain | Description |
|------|-----------|-------|--------|-------------|
| wr_valid_i | input | 1 | clk_i | Producer presents `wr_data_i` |
| wr_ready_o | output | 1 | clk_i | FIFO can accept one payload |
| wr_data_i | input | DataWidth | clk_i | Write payload |

**Protocol:** Valid/ready. The producer may assert `wr_valid_i` independently of `wr_ready_o`. A write transfer occurs when both are high at a rising edge while `rst_ni` is high. If valid is asserted without a transfer, the producer holds `wr_valid_i` and `wr_data_i` stable while stalled. After a transfer, the producer may present a new payload on the next cycle while keeping `wr_valid_i` high.

### Read Channel

| Port | Direction | Width | Domain | Description |
|------|-----------|-------|--------|-------------|
| rd_valid_o | output | 1 | clk_i | FIFO presents the oldest stored payload |
| rd_ready_i | input | 1 | clk_i | Consumer can accept the payload |
| rd_data_o | output | DataWidth | clk_i | Oldest payload; meaningful only when `rd_valid_o` is high |

**Protocol:** Valid/ready. A read transfer occurs when `rd_valid_o` and `rd_ready_i` are both high at a rising edge while `rst_ni` is high. While stalled (`rd_valid_o=1` and `rd_ready_i=0`), the FIFO holds `rd_valid_o` and `rd_data_o` stable. After a transfer, the FIFO may present the next payload on the following cycle while keeping `rd_valid_o` high.

### Status

| Port | Direction | Width | Domain | Description |
|------|-----------|-------|--------|-------------|
| full_o | output | 1 | clk_i | Occupancy equals `Depth` |
| empty_o | output | 1 | clk_i | Occupancy equals zero |
| count_o | output | AddrWidth+1 | clk_i | Current number of stored entries |

Status outputs are level signals with no handshake. `count_o` is meaningful during and after reset. Consumers qualify `rd_data_o` with `rd_valid_o`; `rd_data_o` may reflect uninitialized memory while invalid.

## Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-01 | A write transfer stores the sampled `wr_data_i` exactly once at the current write position. |
| FR-02 | A read transfer presents and removes the oldest stored payload exactly once. |
| FR-03 | At full occupancy, `full_o=1` and `wr_ready_o=0`; no write transfer occurs. |
| FR-04 | At empty occupancy, `empty_o=1` and `rd_valid_o=0`; no read transfer occurs. |
| FR-05 | If read and write are attempted while full, the read succeeds and the write stalls. The pending write may transfer in the following cycle. |
| FR-06 | If read and write are attempted while empty, the write succeeds and no read transfer occurs. The new payload is not cut through. |
| FR-07 | `count_o` equals the exact number of stored, unread entries after every accepted event, including simultaneous read/write away from boundaries. |
| FR-08 | Read transfers preserve strict first-in-first-out ordering across pointer wrap. |
| FR-09 | While reset is asserted, no transfer occurs; `wr_ready_o=0`, `rd_valid_o=0`, `full_o=0`, `empty_o=1`, and `count_o=0`. |
| FR-10 | Illegal parameter configurations fail elaboration; every legal configuration implements FR-01 through FR-09. |
| FR-11 | While a read payload is stalled, `rd_valid_o` remains high and `rd_data_o` remains stable until transfer or reset. |

## Timing Requirements

| ID | Requirement | Value / Constraint | Reference Points |
|----|-------------|--------------------|------------------|
| TR-01 | Write-to-read latency | 1 cycle | Write into an empty FIFO at edge N to `rd_valid_o=1` with that payload during cycle N+1 |
| TR-02 | Sustained throughput | 1 write and 1 read per cycle | Consecutive cycles when neither channel is blocked by its occupancy boundary |
| TR-03 | Write-data combinational path | Forbidden | No `wr_data_i` to `rd_data_o` path; data first enters `mem` at a write edge |
| TR-04 | Read-data combinational path | Allowed | `mem[rd_ptr_q]` to `rd_data_o` while non-empty |
| TR-05 | Handshake/status combinational paths | Forbidden except reset gating | No `wr_valid_i`, `wr_data_i`, or `rd_ready_i` path to `wr_ready_o`, `rd_valid_o`, `full_o`, `empty_o`, or `count_o`; `rst_ni` may gate handshake outputs |
| TR-06 | Reset recovery | 1 cycle | First transfer is permitted in the first complete cycle after synchronous reset deassertion |

## Reset-Visible Behavior

Reset asserts asynchronously when `rst_ni` goes low and initializes the registered pointers and occupancy immediately. Reset deassertion is externally synchronized to a rising edge of `clk_i`.

While `rst_ni=0`, handshake outputs are gated inactive, status reports empty occupancy, and no transfer is recognized. During the first complete cycle after deassertion, the FIFO is empty and may accept a write; this is the recovery interval in TR-06. Reset discards every previously stored entry. The memory array is not reset, but its contents remain architecturally invisible until overwritten and made valid by a later write.

## Non-Goals

- No asynchronous or cross-clock-domain operation
- No fall-through or cut-through read mode
- No simultaneous replacement write while full
- No ECC, parity, almost-full, or almost-empty status
- No non-power-of-two depth
- No registered read-data output

## Block Diagram

```text
              +------------------------------------------------+
 wr_valid_i ->|                                                |<- rd_ready_i
 wr_ready_o <-|  wr_ptr_q --> mem[Depth] <-- rd_ptr_q          |-> rd_valid_o
 wr_data_i -->|                    |                           |-> rd_data_o
              |                 count_q                         |-> full_o
 rst_ni ----->|  reset gate -----+-----------------------------|-> empty_o
              |                                                |-> count_o
              +------------------------------------------------+
                                sync_fifo
```

- `mem[Depth]` stores payloads at `wr_ptr_q` and supplies `mem[rd_ptr_q]` combinationally.
- `count_q` is the sole occupancy state and supplies full, empty, and count status.
- `rst_ni` resets pointers/count and gates the handshake outputs inactive during reset.

## Interface Timing

Each column shows stable signal and state values immediately before the labeled rising edge. Transfers occur at that edge; resulting state appears in the next column.

### Back-to-Back Write and Read

```text
cycle        :  0    1    2    3
wr_valid_i   :  1    1    0    0
wr_data_i    :  A    B    -    -
wr_ready_o   :  1    1    1    1
rd_ready_i   :  0    1    1    0
rd_valid_o   :  0    1    1    0
rd_data_o    :  -    A    B    -
count_q      :  0    1    1    0
```

- Edge 0 accepts A. A becomes readable during cycle 1, exactly 1 cycle later (TR-01).
- Edge 1 accepts B and reads A; occupancy remains one (FR-07).
- Edge 2 reads B; the FIFO becomes empty during cycle 3.

### Full-Boundary Read and Pending Write

`Depth=2`; the FIFO initially contains A then B, and the producer holds pending payload C while stalled.

```text
cycle        :  0    1    2
count_q      :  2    1    2
wr_valid_i   :  1    1    0
wr_data_i    :  C    C    -
wr_ready_o   :  0    1    0
rd_ready_i   :  1    0    0
rd_valid_o   :  1    1    1
rd_data_o    :  A    B    B
```

- Edge 0 reads A; C cannot transfer because current occupancy is full (FR-05).
- During cycle 1 the FIFO is no longer full, so the producer's stable C may transfer at edge 1.
- During cycle 2 the FIFO is full again, containing B then C.

## Implementation Detail

### Sub-Block Decomposition

| Sub-Block | Function | Inputs | Outputs | State / Storage |
|-----------|----------|--------|---------|-----------------|
| Write control | Accept writes and advance write position | rst_ni, wr_valid_i, full_o | wr_ready_o, wr_en, wr_ptr_d | wr_ptr_q |
| Read control | Present/remove oldest entry and advance read position | rst_ni, rd_ready_i, empty_o | rd_valid_o, rd_en, rd_ptr_d | rd_ptr_q |
| Occupancy control | Track accepted writes and reads | wr_en, rd_en | count_d, full_o, empty_o, count_o | count_q |
| Storage | Retain payloads in FIFO order | wr_en, wr_ptr_q, wr_data_i, rd_ptr_q | rd_data_o | mem |

### Internal Signals and Storage

| Signal | Width | Kind | Owner | Description |
|--------|-------|------|-------|-------------|
| mem | Depth x DataWidth | register array | Storage | Payload storage; not reset |
| wr_ptr_q / wr_ptr_d | AddrWidth | register / combinational | Write control | Current/next write position |
| rd_ptr_q / rd_ptr_d | AddrWidth | register / combinational | Read control | Current/next read position |
| count_q / count_d | AddrWidth+1 | register / combinational | Occupancy control | Current/next occupancy |
| wr_en | 1 | combinational | Write control | `rst_ni && wr_valid_i && wr_ready_o` |
| rd_en | 1 | combinational | Read control | `rst_ni && rd_valid_o && rd_ready_i` |

### Write Path

```text
wr_ready_o = rst_ni && !full_o
wr_en      = wr_valid_i && wr_ready_o

if wr_en at a rising edge:
    mem[wr_ptr_q] <= wr_data_i
    wr_ptr_q      <= ptr_inc(wr_ptr_q)
```

`ptr_inc` wraps by truncation because `Depth` is a legal power of two.

### Read Path

```text
rd_valid_o = rst_ni && !empty_o
rd_en      = rd_valid_o && rd_ready_i
rd_data_o  = mem[rd_ptr_q]

if rd_en at a rising edge:
    rd_ptr_q <= ptr_inc(rd_ptr_q)
```

While stalled, `rd_ptr_q` does not advance and no write can target the unread oldest slot, so the combinational `rd_data_o` remains stable (FR-11).

### Occupancy and Status

```text
case {wr_en, rd_en}:
    2'b10: count_d = count_q + 1
    2'b01: count_d = count_q - 1
    default: count_d = count_q

full_o  = (count_q == Depth)
empty_o = (count_q == 0)
count_o = count_q
```

Full and empty are combinational functions of current registered occupancy. No stale registered status is used. FR-05 follows because `wr_ready_o` remains low for the entire cycle whose current occupancy is full, even when a read transfers at its ending edge.

### Reset Behavior

| State / Storage | Reset Value | Reset Style | Rationale / No-Reset Justification |
|-----------------|-------------|-------------|------------------------------------|
| wr_ptr_q | '0 | Asynchronous assertion | First legal write position |
| rd_ptr_q | '0 | Asynchronous assertion | First legal read position |
| count_q | '0 | Asynchronous assertion | Establish empty occupancy |
| mem | Not reset | — | Invalid while count_q is zero; each visible entry is overwritten by an accepted write |

Handshake outputs are gated by `rst_ni`, so no transfer occurs while reset is asserted. Status derives from reset `count_q` and reports empty.

### Critical Timing Paths

| Path | From -> To | Concern | Mitigation / Constraint |
|------|------------|---------|-------------------------|
| Write ready | count_q -> full_o -> wr_ready_o | Occupancy comparator on producer backpressure | Keep combinational for this simple block; if registered later, compute the register D input from count_d and update TR-05 |
| Read valid | count_q -> empty_o -> rd_valid_o | Occupancy comparator on consumer valid | Keep combinational for this simple block; no input controls this path except reset gating |
| Read payload | mem[rd_ptr_q] -> rd_data_o | Depth-wide combinational read mux | Accepted by TR-04; adding an output register changes TR-01 and is a different architecture |

### Requirement Mapping

| Requirement | Implementing Mechanism |
|-------------|------------------------|
| FR-01, FR-03, FR-05 | wr_ready_o, wr_en, mem write, wr_ptr_q |
| FR-02, FR-04, FR-06, FR-11 | rd_valid_o, rd_en, combinational mem read, rd_ptr_q |
| FR-07 | count_q/count_d event table |
| FR-08 | Independent monotonic write/read pointers with power-of-two wrap |
| FR-09 | Asynchronous pointer/count reset and rst_ni handshake gates |
| FR-10 | Elaboration-time parameter assertions |
| TR-01, TR-03, TR-04 | Registered memory write plus combinational addressed read |
| TR-02 | Independent read/write enables and simultaneous count hold |
| TR-05 | Status depends only on count_q; reset is the documented gating exception |
| TR-06 | Reset state and synchronous deassertion assumption |

## Test Plan

### Functional and Timing Tests

| ID | Maps To | Description | Stimulus | Expected Observation |
|----|---------|-------------|----------|----------------------|
| T-01 | FR-01 | Single write | Present A while empty and not in reset | One write transfer; count becomes one; A stored once |
| T-02 | FR-02, FR-08 | Ordered reads | Write A, B, C, then enable reads | Read transfers return A, B, C exactly once in order |
| T-03 | FR-03 | Fill to full | Accept exactly Depth writes without reads | full_o=1, wr_ready_o=0, count_o=Depth |
| T-04 | FR-04 | Drain to empty | Read every stored entry | empty_o=1, rd_valid_o=0, count_o=0 |
| T-05 | FR-05 | Simultaneous attempt while full | At full, assert wr_valid_i and rd_ready_i | Read transfers; write stalls; pending write may transfer next cycle |
| T-06 | FR-06 | Simultaneous attempt while empty | At empty, assert wr_valid_i and rd_ready_i | Write transfers; no read transfer; payload appears next cycle |
| T-07 | FR-07 | Occupancy accounting | Random legal reads/writes including simultaneous transfers | count_o equals scoreboard occupancy after every edge |
| T-08 | FR-08 | Ordering across pointer wrap | Write/read more than 3*Depth tagged payloads | All read tags remain in accepted-write order |
| T-09 | FR-09 | Reset-visible outputs | Assert reset from non-empty state | Handshakes inactive; status empty; prior entries discarded |
| T-10 | FR-10 | Legal parameter sweep | Elaborate DataWidth={1,32}, Depth={2,4,16} | Every legal configuration passes mapped functional tests |
| T-11 | FR-11 | Read stall stability | Hold rd_ready_i low for several cycles while non-empty | rd_valid_o stays high and rd_data_o stays unchanged |
| T-20 | TR-01 | Measure empty write latency | Write A at edge N while empty | A is valid/readable during cycle N+1, not cycle N |
| T-21 | TR-02, FR-07 | Sustained simultaneous throughput | Keep both channels active away from boundaries | One write and one read transfer at every edge; count holds |
| T-22 | TR-03, TR-04 | Datapath structure check | Lint/netlist path inspection | No wr_data_i-to-rd_data_o path; documented mem-read path exists |
| T-23 | TR-05 | Handshake/status independence | Toggle wr_valid_i, wr_data_i, rd_ready_i within stable count state | Ready/valid/status do not change from those inputs |
| T-24 | TR-06, FR-09 | Reset recovery | Deassert reset synchronously and present a write | Write transfers in the first complete post-reset cycle |

### Corner and Parameter Tests

| ID | Maps To | Description | Stimulus | Expected Observation |
|----|---------|-------------|----------|----------------------|
| T-30 | FR-05, FR-07 | Repeated full-boundary turnover | Repeatedly read from full then complete the pending write | No overflow; count sequence is Depth, Depth-1, Depth |
| T-31 | FR-06, TR-01 | Empty-boundary write/read request | Repeated write/read attempts from empty | No cut-through; each payload becomes readable 1 cycle later |
| T-32 | FR-01, FR-02, FR-07, FR-08 | Minimum depth and wrap | Use Depth=2 for many fill/drain cycles | Correct count, no corruption, FIFO order preserved |
| T-33 | FR-09, TR-06 | Reset during read stall | Stall a valid payload, then assert/deassert reset | Valid drops during reset; old payload never transfers; clean recovery |
| T-34 | FR-10 | Illegal configurations | Elaborate DataWidth=0, Depth=1, and Depth=3 separately | Each configuration fails elaboration with a parameter error |

### Assertions

Apply `disable iff (!rst_ni)` to operational temporal properties.

- `ASSERT_COUNT_RANGE`: `count_q <= Depth`
- `ASSERT_COUNT_INC`: `wr_en && !rd_en |=> count_q == $past(count_q) + 1`
- `ASSERT_COUNT_DEC`: `!wr_en && rd_en |=> count_q == $past(count_q) - 1`
- `ASSERT_COUNT_HOLD`: `wr_en == rd_en |=> count_q == $past(count_q)`
- `ASSERT_WR_PTR_ADVANCE`: `wr_en |=> wr_ptr_q == ptr_inc($past(wr_ptr_q))`
- `ASSERT_WR_PTR_HOLD`: `!wr_en |=> $stable(wr_ptr_q)`
- `ASSERT_RD_PTR_ADVANCE`: `rd_en |=> rd_ptr_q == ptr_inc($past(rd_ptr_q))`
- `ASSERT_RD_PTR_HOLD`: `!rd_en |=> $stable(rd_ptr_q)`
- `ASSERT_READ_STALL_STABLE`: `rd_valid_o && !rd_ready_i |=> rd_valid_o && $stable(rd_data_o)`
- `ASSERT_WRITE_STALL_STABLE` (environment assumption): `wr_valid_i && !wr_ready_o |=> wr_valid_i && $stable(wr_data_i)`
- `ASSERT_RESET_STATE`: `!rst_ni |-> !wr_ready_o && !rd_valid_o && !full_o && empty_o && count_o == 0`

Ordering and exactly-once behavior use the testbench scoreboard rather than a vacuous restatement of pointer/data assignments.

### Coverage

- `CVR_FULL`: reach full occupancy
- `CVR_EMPTY_AFTER_DATA`: return to empty after at least one stored entry
- `CVR_SIMULTANEOUS_RW`: complete read and write at the same edge
- `CVR_READ_FROM_FULL`: complete a read while full and a write is pending
- `CVR_WRITE_FROM_EMPTY`: complete a write while the consumer is ready at empty
- `CVR_PTR_WRAP`: observe each pointer wrap
- `CVR_READ_STALL`: stall a valid read for at least two cycles, then transfer
- `CVR_RESET_DURING_STALL`: assert reset while a read payload is stalled
