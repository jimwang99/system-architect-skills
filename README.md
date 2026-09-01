# AI agent skills for system architects

A set of skills for silicon system architects, from architecture to RTL in software hardware co-design.

## Skills

### Research & knowledge extraction

- **[academia-research](academia-research/SKILL.md)** — Answer a focused academic question or compare a body of work from primary sources. Produces a concise Markdown report with claim-level citations, comparable quantitative evidence, limits, and open questions.
- **[extract-architecture-knowledge-from-source](extract-architecture-knowledge-from-source/SKILL.md)** — Turn a reference codebase into standalone documentation for reimplementation without later source access. Records source identity, traceable evidence, behavior, interfaces, algorithms, and verified gaps.
- **[extract-architecture-knowledge-from-paper](extract-architecture-knowledge-from-paper/SKILL.md)** — Turn a paper and its accessible artifacts into standalone, implementation-ready architecture documentation. Separates stated facts, supported inferences, missing details, and user decisions.

### Problem framing

- **[fang](fang/SKILL.md)** — Turn an idea into an agreed problem brief before solution work. Drafts from available evidence, asks one material question at a time, and requires full-document confirmation before alignment.

### Specification

- **[write-hardware-spec](write-hardware-spec/SKILL.md)** — Create, update, review, or freeze the architecture and microarchitecture contract for an RTL block. Covers interfaces, protocols, timing, reset, state, pipelines, traceable verification, and explicit review gates.

### Implementation

- **[write-hardware-rtl](write-hardware-rtl/SKILL.md)** — Write or review synthesizable SystemVerilog for Verilator simulation. Preserves repository conventions and emphasizes exact widths, reset and protocol safety, useful observability, and project-native verification.
- **[write-hardware-test-bench](write-hardware-test-bench/SKILL.md)** — Write SystemC testbenches for Verilator `--sc` models. Scales the harness to the design and covers protocol-derived timing, scoreboards, negative windows, completion, diagnostics, and project integration.

### Debug

- **[debug-hardware-with-logging](debug-hardware-with-logging/SKILL.md)** — Diagnose RTL simulation failures without a waveform viewer. Reproduces the failure, adds selective text evidence, finds the first bad event, tests a concrete hypothesis, and reports the root cause without silently implementing a fix.

## How they fit together

```mermaid
flowchart LR
    Fang[fang] --> Spec[write-hardware-spec]
    Research[academia-research] --> Spec
    Paper[extract from paper] --> Spec
    Source[extract from source] --> Spec
    Spec --> RTL[write-hardware-rtl]
    Spec --> TB[write-hardware-test-bench]
    RTL --> Debug[debug-hardware-with-logging]
    TB --> Debug
```

- Research and extraction skills produce the design knowledge and reference docs.
- FANG confirms the problem before solution work when framing is still unclear.
- The spec skill defines and reviews behavior and verification intent before implementation starts.
- RTL and testbench skills implement the spec with the logging/assertion conventions the debug skill relies on.
- The debug skill closes the loop when simulation fails.
