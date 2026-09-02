# `bit-field` reference

Use the official [WaveDrom bit-field repository](https://github.com/wavedrom/bitfield) as the authority for the schema and CLI. The npm package is `bit-field`; an installed local executable is named `bitfield`. Do not substitute the unrelated `bitfield` npm package.

The standalone CLI reads a strict-JSON array. The skill helper also accepts an object with metadata and passes only its `fields` array to the renderer.

## Field object

Fields are listed from least-significant to most-significant.

| Key | Meaning |
|---|---|
| `bits` | Positive field width; required |
| `name` | Display label; omit for a reserved gap |
| `attr` | One string or a list of renderer rows for an encoding or other generic format attribute |
| `type` | Visual class 1 through 9; use only with an explained legend |
| `rotate` | Label angle for narrow fields |
| `overline` | Overline the field name, often for an active-low convention |
| `access` | Helper-only register access rule; the helper also adds it to the rendered rows |
| `reset` | Helper-only register field reset; the helper also adds it to the rendered rows |
| `desc` | Helper-only Markdown description |

Do not encode unverified semantics into `attr` or `desc`.

## Display and CLI

The default diagram places the most-significant bit on the left. That visual convention is independent of byte endianness in memory.

Common CLI controls passed through by the helper are `--lanes`, `--bits`, `--hspace`, `--vspace`, `--fontsize`, `--compact`, and `--offset`. Use one lane when labels fit. Add lanes for crowded fields or architecture-defined words; do not use lane wrapping to hide an unclear format.

The helper accepts this metadata form:

```json
{
  "name": "CTRL",
  "offset": "0x000",
  "width": 32,
  "reset": "0x0000_0000",
  "fields": [
    {"name": "EN", "bits": 1, "access": "RW", "reset": "0", "desc": "Enable."},
    {"bits": 31}
  ]
}
```

## Instruction format example

This RV32I I-type field order is least-significant first:

```json
[
  {"name": "opcode", "bits": 7, "attr": "0010011"},
  {"name": "rd", "bits": 5},
  {"name": "funct3", "bits": 3},
  {"name": "rs1", "bits": 5},
  {"name": "imm[11:0]", "bits": 12}
]
```

The [official RV32I ALU example](https://github.com/wavedrom/bitfield/blob/trunk/test/rv32i-alu.json) provides a primary renderer input example. Integrated WaveDrom register input uses a different root object, such as the official [`{reg: [...]}` example](https://github.com/wavedrom/wavedrom/blob/trunk/test/reg-opivi.json5); do not pass that form to the standalone helper.

For a metadata object that is not a register, set `"kind": "format"`; its Markdown table uses a generic Attributes column and preserves every `attr` row. A bare field array is generic by default. Do not put both `access`/`reset` and `attr` on one field.
