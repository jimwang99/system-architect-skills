# Hardware-diagram abstraction

A diagram is an argument, not an inventory. Its value comes from removing details that do not help the named reader answer the named question.

## Frame the argument

Answer these before drawing:

- **Reader:** architect, RTL engineer, verification engineer, firmware engineer, or mixed review group.
- **Question:** one sentence that the figure must answer.
- **Subject:** one block or path that may carry more detail and the accent color.
- **Frame:** a structure the reader already understands, such as pipeline stages, package boundaries, or a left-to-right request path.
- **Omissions:** clock/reset, DFT, debug, internal queues, bypass paths, or other details excluded on purpose.

If removing a block does not change the answer, remove it.

## Choose one level

| Level | Keep | Remove by default |
|---|---|---|
| System | Packages, external links, major data movement | RTL units and signal names |
| SoC | Major IP, fabrics, memory controllers, boundary interfaces | Internal muxes and pipelines |
| Microarchitecture | Stages, major structures, queues, subject data/control paths | Unrelated bypasses and per-bit signals |
| Datapath | Registers, muxes, operators needed to explain one algorithm | Whole-chip context |

Do not place a gate-level detail beside a chip-level block in the same figure.

## Collapse repetition

| Situation | Representation |
|---|---|
| Identical instances | One block with `.stack(count)` and a count label |
| Related signal bundle | One bus with a verified width |
| Valid/ready or credits | One handshake bus or dashed control edge only when flow control is the subject |
| Clock, reset, power, or DFT | Omit, or show a domain boundary when the boundary is the subject |
| Off-chip component | An `io` block at the edge |

Use names from the supplied design sources. Put at most one organization fact such as size, depth, or port count in a block subtitle. Put assumptions and omissions in the caption.

## Primary visual references

- [lowRISC Ibex block diagram SVG](https://github.com/lowRISC/ibex/blob/master/doc/03_reference/images/blockdiagram.svg) is a maintained hardware block-diagram example with stage grouping and explicit data/control paths.
- [OpenHW CVA6 design introduction](https://docs.openhwgroup.org/projects/cva6-user-manual/03_cva6_design/intro.html) pairs a processor overview figure with architecture text; use the text to verify meaning rather than copying geometry.
