---
name: draw-uarch-diagram
description: Create architecture and microarchitecture block diagrams as Python-authored SVG, especially pipelines, staged datapaths, control feedback, and left-to-right system flows. Use when a user asks for a hardware block diagram, pipeline figure, architecture overview, or data/control-flow diagram. For cycle timing use draw-waveform; for register bit layouts use draw-register-map.
---

# Architecture diagrams

Create a diagram that explains one design decision or flow. Do not turn the RTL hierarchy into a box inventory.

## Define the figure

Write one line with the reader, the question, the subject, the fixed frame, and explicit omissions. If the source does not establish a name, width, capacity, or relationship, leave it out or mark it unknown; do not invent it.

Read [references/abstraction.md](references/abstraction.md) when choosing the abstraction level or deciding what to remove. Read [references/style.md](references/style.md) before adding a new symbol or manual layout override.

## Build from Python

Copy [scripts/uarch.py](scripts/uarch.py) and [examples/pipeline5.py](examples/pipeline5.py) from this skill directory to the output directory, rename the example after the figure, then adapt it. Keep both Python files with the SVG so the figure remains portable and editable.

Use `Figure.pipeline()` with `frame.stage()` for pipeline stages and `Figure.columns()` with `frame.column()` for a left-to-right system flow. Add semantic blocks with `stage.mem()`, `stage.fifo()`, `stage.unit()`, `stage.mux()`, `stage.control()`, or `stage.io()`. Declare named ports, then connect them with `figure.wire()`, `figure.bus()`, or `figure.ctrl()`. Use `block.port("literal-name")` when punctuation or an existing block attribute prevents dotted port access.

Use `.accent()` on one block for the subject. If the subject is a path, keep and label only the edges needed to explain it. Use `.stack(count)` for identical instances. Set `handshake=True` on a bus only when backpressure is relevant to the question.

Let the automatic orthogonal layout place blocks and route edges; use `block.at(column, row)` or `edge.via((column, row), ...)` only when the automatic result obscures the answer. Lint errors force two cases: a forward edge that skips an occupied stage needs explicit `via()` waypoints, and blocks within one stage connect through facing bottom/top ports or explicit waypoints. Both rules stop hidden wires through intermediate blocks. `Figure.lint()` reports every manual override as maintenance cost.

Call only `Figure.render()` for output; it runs lint, layout, and SVG generation in order. Call `Figure.to_dict()` to inspect the semantic model when reviewing changes.

```bash
uv run --with drawsvg --with loguru python <figure>.py --out <figure>
```

Add `--with cairosvg` and `--png` only when a raster review copy is useful and the native Cairo library is installed.

## Review and deliver

Open the rendered output and check: one clear question, one abstraction level, readable names, data flowing left to right, feedback below the main path, control dashed, buses labeled with verified widths, no wire crossing a block, and no unexplained color.

Deliver the Python source, SVG, optional PNG, and a short caption that states the answer and omissions. Treat the supplied specification or RTL as the source of truth, not the generated figure.
