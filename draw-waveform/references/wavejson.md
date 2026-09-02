# WaveJSON reference

Use the [WaveDrom WaveJSON schema reference](https://github.com/wavedrom/schema/blob/master/WaveJSON.md) as the authority for syntax and the [official WaveDrom tutorial](https://wavedrom.com/tutorial.html) for worked examples.

## Wave symbols

| Symbol | Meaning |
|---|---|
| `0`, `1` | Logic low or high |
| `.` | Extend the previous state by one period |
| `x` | Unknown or invalid |
| `z` | High impedance |
| `=` | Bus value using the next `data` entry |
| `2` through `9` | Bus value with a numbered visual class |
| `p`, `P` | Positive clock; uppercase adds an edge marker |
| `n`, `N` | Negative clock; uppercase adds an edge marker |
| `h`, `l` | Constant high or low with clock spacing |
| `H`, `L` | Constant high or low with an edge marker |
| `|` | Visual gap for elided time |

Each wave character occupies one lane period. `period` scales a lane and `phase` shifts it by a fraction of that period.

## Lane form

```json5
{ name: "rdata", wave: "x..=x", data: ["D0"], node: "...a.", period: 1, phase: 0 }
```

Every `=` or numbered bus state consumes the next `data` entry. Letters in `node` mark positions used by root-level `edge` expressions. Empty objects create spacer lanes. An array such as `["Request", lane, lane]` creates a named group; groups may nest.

## Arrows and spans

| Form | Use |
|---|---|
| `a->b label` | Straight causal arrow |
| `a-|>b label` | Orthogonal arrow |
| `a~>b label` | Curved arrow |
| `a<->b label` | Two-ended span |
| `a+b label` | Measurement bracket |

Use `head: {tick: 0}` to show cycle numbers. Increase `config.hscale` when labels do not fit. The official [WaveDrom repository](https://github.com/wavedrom/wavedrom) documents the current renderer and command-line use; the separate [wavedrom-cli repository](https://github.com/wavedrom/cli) documents its `-i`, `-s`, and `-p` interface.
