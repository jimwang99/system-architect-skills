# Diagram style contract

The Python helper keeps drawing primitives private. Extend the semantic builder only when the requested figure cannot be expressed with the existing block and edge types.

## Symbols

| Builder | Meaning |
|---|---|
| `stage.unit()` | Functional logic or a combined unit |
| `stage.mem()` | Cache, SRAM, register file, ROM, or TCM |
| `stage.fifo()` | Queue, buffer, ROB, or MSHR |
| `stage.mux()` | A selection point relevant to the question |
| `stage.control()` | Controller, hazard logic, or policy block |
| `stage.io()` | Package, PHY, memory, host, or other boundary entity |
| `.accent()` | The one subject of the figure |
| `.stack(count)` | Repeated equivalent instances |

Keep blocks with the same role visually consistent. Prefer a short design name and one short subtitle over prose inside a block.

## Edges

| Builder | Rendering | Use |
|---|---|---|
| `figure.wire()` | Thin solid arrow | Scalar or abstract data dependency |
| `figure.bus()` | Thick solid arrow with width | Multi-bit or protocol data path |
| `figure.ctrl()` | Thin dashed arrow | Control, stall, flush, redirect, or interrupt |

Keep the main path left to right. Mark feedback with `back=True`; the layout routes it below the main frame. Use named ports to show where a relationship enters or leaves a block.

## Manual overrides

`block.at(column, row)` and `edge.via((column, row), ...)` use a 20 px grid with positive Y downward. They are escape hatches, not the main interface. Each override appears in lint output and should survive a resize or label change before it is accepted.

## Output

SVG is the source rendering. PNG is an optional review copy created through CairoSVG. The helper uses drawsvg's supported drawing and `save_svg()` interfaces; see the [drawsvg API reference](https://cduck.github.io/drawsvg/) and [CairoSVG documentation](https://cairosvg.org/documentation/).
