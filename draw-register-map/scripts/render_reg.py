#!/usr/bin/env python3
"""Render one validated bit layout and derive its Markdown field table."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from math import ceil
from pathlib import Path
from typing import Any

from loguru import logger

PASSED_KEYS = {"name", "bits", "attr", "type", "rotate", "overline"}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--lanes", type=int)
    parser.add_argument("--bits", type=int)
    parser.add_argument("--hspace", type=int)
    parser.add_argument("--vspace", type=int)
    parser.add_argument("--fontsize", type=int)
    parser.add_argument(
        "--offset", type=int, help="starting bit number for a multi-word format"
    )
    parser.add_argument("--compact", action="store_true")
    parser.add_argument("--png", action="store_true")
    parser.add_argument("--out", type=Path)
    return parser


def _bit_field_binary() -> str:
    configured = os.environ.get("BIT_FIELD_BIN")
    candidates = [
        configured,
        str(Path.cwd() / "node_modules" / ".bin" / "bitfield"),
        shutil.which("bitfield"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file() and os.access(candidate, os.X_OK):
            return candidate
    raise RuntimeError(
        "bit-field CLI not found; install the `bit-field` npm package in this project with `npm install --save-dev bit-field`"
    )


def _load(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    source = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(source, list):
        metadata: dict[str, Any] = {}
        fields = source
    elif isinstance(source, dict) and isinstance(source.get("fields"), list):
        metadata = source
        fields = source["fields"]
    else:
        raise ValueError(
            "input must be a field array or an object containing a fields array"
        )
    if not fields:
        raise ValueError("fields must not be empty")
    for index, item in enumerate(fields):
        if not isinstance(item, dict):
            raise ValueError(f"field {index} must be an object")
        bits = item.get("bits")
        if isinstance(bits, bool) or not isinstance(bits, int) or bits < 1:
            raise ValueError(f"field {index} needs a positive integer bits value")
    return metadata, fields


def _markdown_text(value: object) -> str:
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("|", "\\|")
        .replace("$", "\\$")
        .replace("\n", "<br>")
    )


def _field_table(
    metadata: dict[str, Any], fields: list[dict[str, Any]], bit_offset: int = 0
) -> str:
    lines: list[str] = []
    if metadata:
        heading = f"### {_markdown_text(metadata.get('name', 'Register'))}"
        if "offset" in metadata:
            heading += f" — offset `{_markdown_text(metadata['offset'])}`"
        lines.extend([heading, ""])
        if metadata.get("desc"):
            lines.extend([_markdown_text(metadata["desc"]), ""])
        if "reset" in metadata:
            lines.extend([f"Reset value: `{_markdown_text(metadata['reset'])}`", ""])
    register_table = bool(metadata) and metadata.get("kind", "register") == "register"
    for item in fields:
        if register_table and "attr" in item:
            raise ValueError(
                "register fields use access/reset; attr is reserved for generic formats"
            )
        if not register_table and ("access" in item or "reset" in item):
            raise ValueError(
                "generic-format fields use attr; access/reset require a register metadata object"
            )
    if register_table:
        lines.extend(
            [
                "| Bits | Field | Access | Reset | Description |",
                "|---|---|---|---|---|",
            ]
        )
    else:
        lines.extend(
            ["| Bits | Field | Attributes | Description |", "|---|---|---|---|"]
        )
    low = bit_offset
    rows: list[str] = []
    for item in fields:
        high = low + item["bits"] - 1
        bit_range = f"[{high}]" if high == low else f"[{high}:{low}]"
        name = item.get("name", "Reserved")
        if register_table:
            row = "| {} | {} | {} | {} | {} |".format(
                bit_range,
                _markdown_text(name),
                _markdown_text(item.get("access", "")),
                _markdown_text(item.get("reset", "")),
                _markdown_text(item.get("desc", "")),
            )
        else:
            attribute = item.get("attr", "")
            if isinstance(attribute, list):
                attribute = "<br>".join(_markdown_text(value) for value in attribute)
            else:
                attribute = _markdown_text(attribute)
            row = "| {} | {} | {} | {} |".format(
                bit_range,
                _markdown_text(name),
                attribute,
                _markdown_text(item.get("desc", "")),
            )
        rows.append(row)
        low = high + 1
    lines.extend(reversed(rows))
    return "\n".join(lines) + "\n"


def _render_svg(
    binary: str,
    fields: list[dict[str, Any]],
    width: int,
    lanes: int,
    args: argparse.Namespace,
) -> str:
    clean = []
    for item in fields:
        rendered = {key: value for key, value in item.items() if key in PASSED_KEYS}
        if "access" in item or "reset" in item:
            if "attr" in item:
                raise ValueError(
                    "use access/reset for register fields or attr for generic formats, not both"
                )
            attributes = [str(item.get("access", ""))]
            if "reset" in item:
                attributes.append(str(item["reset"]))
            rendered["attr"] = attributes
        clean.append(rendered)
    with tempfile.NamedTemporaryFile(
        "w", suffix=".json", encoding="utf-8"
    ) as temporary:
        json.dump(clean, temporary)
        temporary.flush()
        command = [
            binary,
            "-i",
            temporary.name,
            "--lanes",
            str(lanes),
            "--bits",
            str(width),
            "--hspace",
            str(args.hspace or _default_hspace(fields)),
        ]
        for option, value in (
            ("--vspace", args.vspace),
            ("--fontsize", args.fontsize),
            ("--offset", args.offset),
        ):
            if value is not None:
                command.extend([option, str(value)])
        if args.compact:
            command.append("--compact")
        result = subprocess.run(command, check=True, capture_output=True, text=True)
    if not result.stdout.strip():
        raise RuntimeError("bit-field returned an empty SVG")
    return result.stdout


def _default_lanes(width: int, fields: list[dict[str, Any]]) -> int:
    crowded = any(item.get("name") and item["bits"] <= 2 for item in fields)
    bits_per_lane = 16 if crowded else 32
    return ceil(width / bits_per_lane)


def _default_hspace(fields: list[dict[str, Any]]) -> int:
    return (
        800 if any(item.get("name") and item["bits"] <= 2 for item in fields) else 640
    )


def main() -> None:
    args = _parser().parse_args()
    metadata, fields = _load(args.input)
    field_width = sum(item["bits"] for item in fields)
    if args.bits is not None:
        width = args.bits
    elif "width" in metadata:
        width = metadata["width"]
    else:
        width = field_width
    if isinstance(width, bool) or not isinstance(width, int) or width < 1:
        raise ValueError("register width must be a positive integer")
    if field_width != width:
        raise ValueError(
            f"field widths sum to {field_width}, expected {width}; add an explicit reserved field for every gap"
        )
    lanes = args.lanes if args.lanes is not None else _default_lanes(width, fields)
    if lanes < 1:
        raise ValueError("lanes must be at least 1")
    if args.offset is not None and args.offset < 0:
        raise ValueError("offset must be non-negative")
    for name in ("hspace", "vspace", "fontsize"):
        value = getattr(args, name)
        if value is not None and value < 1:
            raise ValueError(f"{name} must be at least 1")
    output = args.out or args.input.with_suffix("")
    svg_path = Path(f"{output}.svg")
    markdown_path = Path(f"{output}.md")
    table = _field_table(metadata, fields, args.offset or 0)
    svg = _render_svg(_bit_field_binary(), fields, width, lanes, args)
    output.parent.mkdir(parents=True, exist_ok=True)
    svg_path.write_text(svg, encoding="utf-8")
    markdown_path.write_text(table, encoding="utf-8")
    logger.info("Wrote {} and {}", svg_path, markdown_path)
    if args.png:
        try:
            import cairosvg
        except (ImportError, OSError) as error:
            raise RuntimeError(
                "PNG needs CairoSVG and the native Cairo library; install both or render SVG only"
            ) from error
        png_path = Path(f"{output}.png")
        cairosvg.svg2png(url=str(svg_path), write_to=str(png_path), scale=2)
        logger.info("Wrote {}", png_path)


if __name__ == "__main__":
    main()
