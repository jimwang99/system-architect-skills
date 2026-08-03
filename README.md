# AI agent skills for system architects

A set of skills for silicon system architects, from architecture to RTL in software hardware co-design.

## Skills

### Research & knowledge extraction

- **[academia-research](academia-research/SKILL.md)** — Research an academic topic or survey a research field using only Claude Code's built-in web search. Explores the field, optionally clarifies scope with you, fans out parallel subagents per sub-topic, and synthesizes everything into one structured report with a TL;DR, followed by interactive Q&A.
- **[extract-architecture-knowledge-from-source](extract-architecture-knowledge-from-source/SKILL.md)** — Mine a reference codebase into a buildable spec: a doc set from which a fresh session with no repo access can reimplement the design, possibly in another language or stack. Enforces traceability (`file:line` citations), ASCII block diagrams, quantitative behavior as tables, and a separation of the essential design from repo-specific choices.
- **[extract-architecture-knowledge-from-paper](extract-architecture-knowledge-from-paper/SKILL.md)** — Same goal, but the reference is an academic paper instead of code. Treats the paper as lossy: builds a claims ledger from a page-by-page read, closes gaps via artifact code, cross-papers, or your decisions (never silent invention), and verifies quantitative claims with executable models (SimPy, escalating to SystemC) before the docs count as done.

### Specification

- **[write-hardware-spec](write-hardware-spec/SKILL.md)** — Write the single source of truth for an RTL block before any implementation: interfaces, protocols, timing, reset, FSM/pipeline behavior, and a traceable test plan (T-xx IDs). Gated workflow with brainstorming up front and review gates before handing off to RTL and testbench implementation.

### Implementation

- **[write-hardware-rtl](write-hardware-rtl/SKILL.md)** — Write synthesizable SystemVerilog in lowRISC style for Verilator simulation. Every module gets runtime-configurable logging (plusargs-based verbosity), assertions at its boundaries, and coverage points — because AI agents debug with text, not waveforms.
- **[write-hardware-test-bench](write-hardware-test-bench/SKILL.md)** — Write SystemC testbenches that drive Verilator-compiled RTL. Covers structure (separate Driver/Monitor/ResetGen/Scoreboard modules), ready/valid and multi-channel protocol handling, and a verified working template with build script.

### Debug

- **[debug-hardware-with-logging](debug-hardware-with-logging/SKILL.md)** — Debug RTL simulation failures without a waveform viewer. Instead of hand-tracing logic or guessing fixes from code reading, add structured logging at the signals in question, rerun the simulation, and read what actually happened — narrowing from assertion hits to the failing time window to the root cause.

## How they fit together

```
academia-research ──┐
extract-from-paper ─┼──> write-hardware-spec ──> write-hardware-rtl ──────┐
extract-from-source ┘            │                                        ├──> debug-hardware-with-logging
                                 └─────────────> write-hardware-test-bench┘
```

- Research and extraction skills produce the design knowledge and reference docs.
- The spec skill freezes behavior and the test plan before implementation starts.
- RTL and testbench skills implement the spec with the logging/assertion conventions the debug skill relies on.
- The debug skill closes the loop when simulation fails.
