---
name: draw-register-map
description: Document hardware registers and fixed bit layouts as bit-field SVG diagrams plus matching Markdown tables, including CSRs, MMIO registers, instruction encodings, descriptors, and packet headers. Use when a user asks for a register map, bit-field diagram, field positions, CSR documentation, instruction format, or header layout. Do not use for timing (waveform) or architecture block diagrams (uarch-diagram).
---

# Register maps and bit fields

Optimize for firmware and verification accuracy. A polished wrong reset value or access rule is worse than an explicit unknown.

## Collect source data

For each register, collect its name, byte offset, total width, reset value, and fields from least-significant bit to most-significant bit. For every named field, collect width, access rule, reset value, meaning, encodings, and side effects. Ask for missing semantics or leave them blank; never infer reserved-bit behavior, write side effects, or reset values.

Use one bit-field figure per register or fixed-format word. Represent the top-level register map as an offset-sorted Markdown table. Split a very wide descriptor into architecture-defined words and preserve continuous bit numbering with `--offset`.

Read [references/bitfield.md](references/bitfield.md) for the renderer schema, CLI details, display orientation, and instruction-format example. Start from [examples/dma_ctrl.json](examples/dma_ctrl.json).

## Validate and render

List every field exactly once. Reserved gaps are unnamed entries such as `{"bits": 5}`. For register fields, use explicit `access` and `reset` keys; use `attr` only for encodings and other generic formats. The helper rejects mixed modes, missing coverage, or a sum different from the declared width.

Install the official package in the current project only when the user authorizes dependency installation:

```bash
npm install --save-dev bit-field
```

Render SVG and the matching Markdown table in a uv-managed environment:

```bash
uv run --with loguru python register-map/scripts/render_reg.py DMA_CTRL.json --out DMA_CTRL
```

Add `--with cairosvg` and `--png` only for a raster review copy when the native Cairo library is installed. The helper never installs npm or Python packages and never writes into the user home directory.

## Review and deliver

Open the output and check continuous bit numbers, declared width, field order, readable labels, access/reset coverage, and exact agreement between the figure and table. Treat MSB-left as display orientation; it does not by itself define byte endianness.

Deliver the input JSON, SVG, Markdown field table, optional PNG, and top-level map table when multiple registers are in scope. State display orientation, register width, byte offset, and every unresolved semantic gap in the caption or surrounding text.
