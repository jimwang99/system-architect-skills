---
name: draw-waveform
description: Create digital timing diagrams from WaveJSON, including valid-ready handshakes, protocol transactions, clock relationships, reset sequences, pipeline occupancy, and latency. Use when a user asks for a waveform, timing diagram, cycle view, sampling edge, stall, or handshake illustration. For block diagrams use draw-uarch-diagram; for register bit layouts use draw-register-map.
---

# Hardware timing diagrams

Make each waveform answer one timing question. Do not copy a full testbench trace into documentation.

## Plan the waveform

State the question, signals in display order, cycle range, transaction count, and the one causal arrow or latency span that answers the question. Use names and timing only from the supplied specification, RTL, trace, or user confirmation.

Prefer one transaction, or two when back-to-back behavior is the point. Keep only signals needed for the answer, group them by interface, and draw a clock once at the top. Represent a bus as one lane with `data` labels; never expand it bit by bit. Use `x` outside a valid window and `z` only for high impedance. Use a pipeline-occupancy view instead of raw signals when the question is about stalls, bubbles, or flushes.

Read [references/wavejson.md](references/wavejson.md) for exact WaveJSON symbols and arrow syntax. Start from [examples/valid_ready_write.json5](examples/valid_ready_write.json5).

## Render

The helper finds an existing renderer through `WAVEDROM_BIN`, the project `node_modules`, or a `wavedrom`/`wavedrom-cli` executable on PATH. When none exists, install WaveDrom in the current project only when the user authorizes dependency installation:

```bash
npm install --save-dev wavedrom
```

Render SVG with the helper from this skill directory:

```bash
bash <skill-directory>/scripts/render.sh timing.json5 timing
```

For a PNG review copy, install the native Cairo library, then run the helper in a uv-managed environment:

```bash
uv run --with cairosvg bash <skill-directory>/scripts/render.sh timing.json5 timing --png
```

## Review and deliver

Open the render and check that transitions align with the intended sampling edge, bus labels fit, cycle numbers support the latency claim, unknown windows are explicit, and each arrow explains a real causal relationship. Replace long waits with a WaveDrom gap only when elapsed idle cycles are irrelevant.

Deliver the `.json5` source, `.svg`, optional `.png`, and a short caption with timing assumptions. If the specification leaves an edge, latency, or ready/valid rule unknown, report the gap instead of drawing a guess.
