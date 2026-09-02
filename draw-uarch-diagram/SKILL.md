---
name: draw-uarch-diagram
description: Create architecture and microarchitecture block diagrams as Python-authored SVG, especially pipelines, staged datapaths, control feedback, and left-to-right system flows. Use when a user asks for a hardware block diagram, pipeline figure, architecture overview, datapath picture, or data/control-flow diagram. Do not use for cycle timing (waveform) or register bit layouts (register-map).
---

# Architecture diagrams

Create a diagram that explains one design decision or flow. Do not turn the RTL hierarchy into a box inventory.

## Define the figure

Write one line with the reader, the question, the subject, the fixed frame, and explicit omissions. If the source does not establish a name, width, capacity, or relationship, leave it out or mark it unknown; do not invent it.

Read [references/abstraction.md](references/abstraction.md) when choosing the abstraction level or deciding what to remove. Read [references/style.md](references/style.md) before adding a new symbol or manual layout override.

## Build from Python

Copy [examples/pipeline5.py](examples/pipeline5.py) and [scripts/uarch.py](scripts/uarch.py) beside the requested output, then adapt the example. Keep both Python files with the SVG so the figure remains portable and editable.

Use `Figure.pipeline()` with `frame.stage()` for pipeline stages and `Figure.columns()` with `frame.column()` for a left-to-right system flow. Add semantic blocks with `stage.mem()`, `stage.fifo()`, `stage.unit()`, `stage.mux()`, `stage.control()`, or `stage.io()`. Declare named ports, then connect them with `figure.wire()`, `figure.bus()`, or `figure.ctrl()`. Use `block.port("literal-name")` when punctuation or an existing block attribute prevents dotted port access.

Use `.accent()` on one block for the subject. If the subject is a path, keep and label only the edges needed to explain it. Use `.stack(count)` for identical instances. Set `handshake=True` on a bus only when backpressure is relevant to the question.

Do not put coordinates in ordinary figure code. Use `block.at(column, row)` or `edge.via((column, row), ...)` only when the automatic orthogonal layout obscures the answer. A forward edge that skips an occupied stage needs explicit `via()` waypoints. Within one stage, connect adjacent blocks through facing bottom/top ports or add explicit waypoints. These rules stop hidden wires through intermediate blocks. `Figure.lint()` reports every manual override as maintenance cost.

Call `Figure.to_dict()` when reviewing semantic changes. Call only `Figure.render()` for output; it runs lint, layout, and SVG generation in order.

```bash
uv run --with drawsvg --with loguru python uarch-diagram/examples/pipeline5.py --out /tmp/pipeline5
```

Add `--with cairosvg` and `--png` only when a raster review copy is useful and the native Cairo library is installed. The helper never installs dependencies; generated assets use the chosen output basename.

## Review and deliver

Open the rendered output and check: one clear question, one abstraction level, readable names, data flowing left to right, feedback below the main path, control dashed, buses labeled with verified widths, no wire crossing a block, and no unexplained color.

Deliver the Python source, SVG, optional PNG, and a short caption that states the answer and omissions. Treat the supplied specification or RTL as the source of truth, not the generated figure.
