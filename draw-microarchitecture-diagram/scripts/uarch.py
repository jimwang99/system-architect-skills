"""Build reviewable hardware diagrams from a small, declarative Python model."""

from __future__ import annotations

import keyword
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Literal

import drawsvg as draw
from loguru import logger

GRID = 20
FONT = "Inter, Helvetica, Arial, sans-serif"
STROKE = "#273142"
TEXT = "#172033"
MUTED = "#667085"
CONTROL = "#667085"
FILLS = {
    "logic": "#f5f7fa",
    "mem": "#e8f1fb",
    "fifo": "#fff4d6",
    "mux": "#f5f7fa",
    "io": "#ffffff",
    "control": "#f3eefb",
    "bar": "#f5f7fa",
}
ACCENT = "#ffe2c2"

Side = Literal["left", "right", "top", "bottom"]
Kind = Literal["logic", "mem", "fifo", "mux", "io", "control", "bar"]


def _names(value: str | Iterable[str] | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return list(value)


def _attribute_name(name: str) -> str:
    value = re.sub(r"\W+", "_", name).strip("_") or "port"
    if value[0].isdigit():
        value = f"p_{value}"
    if keyword.iskeyword(value):
        value = f"{value}_"
    return value


@dataclass(frozen=True, slots=True)
class LintFinding:
    severity: Literal["error", "warning"]
    message: str


@dataclass(slots=True)
class Port:
    owner: "Block"
    name: str
    side: Side
    anchor: bool = False

    def point(self) -> tuple[float, float]:
        x, y, width, height = self.owner._box
        peers = [
            port
            for port in self.owner._ports.values()
            if port.side == self.side and not port.anchor
        ]
        if self.side == "left":
            if self.anchor or not peers:
                return x, y + height / 2
            top = y + 31 + 13 * len((self.owner.sub or "").splitlines())
            start, end = top + 9, y + height - 7
            position = (
                (start + end) / 2
                if len(peers) == 1
                else start + (end - start) * peers.index(self) / (len(peers) - 1)
            )
            return x, position
        if self.side == "right":
            if self.anchor or not peers:
                return x + width, y + height / 2
            top = y + 31 + 13 * len((self.owner.sub or "").splitlines())
            start, end = top + 9, y + height - 7
            position = (
                (start + end) / 2
                if len(peers) == 1
                else start + (end - start) * peers.index(self) / (len(peers) - 1)
            )
            return x + width, position
        if self.anchor or not peers:
            fraction = 0.5
        else:
            fraction = (peers.index(self) + 1) / (len(peers) + 1)
        if self.side == "top":
            return x + width * fraction, y
        return x + width * fraction, y + height


@dataclass(slots=True)
class Block:
    _id: str
    label: str
    kind: Kind
    stage: "Stage"
    sub: str | None = None
    highlighted: bool = False
    copies: int = 1
    _ports: dict[str, Port] = field(default_factory=dict)
    _aliases: dict[str, str] = field(default_factory=dict)
    _manual_position: tuple[float, float] | None = None
    _box: tuple[float, float, float, float] = (0, 0, 0, 0)

    def __getattr__(self, name: str) -> Port:
        aliases = object.__getattribute__(self, "_aliases")
        if name in aliases:
            return object.__getattribute__(self, "_ports")[aliases[name]]
        raise AttributeError(f"{self.label!r} has no port {name!r}")

    def port(self, name: str) -> Port:
        try:
            return self._ports[name]
        except KeyError as error:
            raise KeyError(
                f"{self.label!r} has no port {name!r}; available: {sorted(self._ports)}"
            ) from error

    def accent(self) -> "Block":
        self.highlighted = True
        return self

    def stack(self, count: int) -> "Block":
        if count < 1:
            raise ValueError("stack count must be at least 1")
        self.copies = count
        return self

    def at(self, column: float, row: float) -> "Block":
        if column < 0 or row < 0:
            raise ValueError("manual block coordinates must be non-negative")
        self._manual_position = (column, row)
        return self

    def _add_port(self, name: str, side: Side, *, anchor: bool = False) -> None:
        if name in self._ports:
            raise ValueError(f"duplicate port {name!r} on {self.label!r}")
        alias = _attribute_name(name)
        if alias in self._aliases:
            raise ValueError(
                f"ports on {self.label!r} map to the same Python attribute {alias!r}"
            )
        self._ports[name] = Port(self, name, side, anchor)
        self._aliases[alias] = name


@dataclass(slots=True)
class Edge:
    source: Port
    destination: Port
    kind: Literal["data", "bus", "control"] = "data"
    label: str | None = None
    width: int | str | None = None
    handshake: bool = False
    back: bool = False
    _waypoints: list[tuple[float, float]] = field(default_factory=list)

    def via(self, *points: tuple[float, float]) -> "Edge":
        if not points:
            raise ValueError("via needs at least one (column, row) point")
        if any(len(point) != 2 or point[0] < 0 or point[1] < 0 for point in points):
            raise ValueError(
                "manual edge waypoints must be non-negative (column, row) pairs"
            )
        self._waypoints = list(points)
        return self


class Stage:
    def __init__(
        self,
        pipeline: "Pipeline",
        stage_id: str,
        label: str,
        group: str | None,
        color: str | None,
    ) -> None:
        self.pipeline = pipeline
        self._id = stage_id
        self.label = label
        self.group = group
        self.color = color
        self.blocks: list[Block] = []
        self._box = (0.0, 0.0, 0.0, 0.0)

    def unit(self, label: str, **options: object) -> Block:
        return self._block("logic", label, **options)

    def mem(self, label: str, **options: object) -> Block:
        return self._block("mem", label, **options)

    def fifo(self, label: str, **options: object) -> Block:
        return self._block("fifo", label, **options)

    def mux(self, label: str, **options: object) -> Block:
        return self._block("mux", label, **options)

    def io(self, label: str, **options: object) -> Block:
        return self._block("io", label, **options)

    def control(self, label: str, **options: object) -> Block:
        return self._block("control", label, **options)

    def bar(self, label: str, **options: object) -> Block:
        return self._block("bar", label, **options)

    def _block(
        self,
        kind: Kind,
        label: str,
        *,
        inputs: str | Iterable[str] | None = None,
        outputs: str | Iterable[str] | None = None,
        top: str | Iterable[str] | None = None,
        bottom: str | Iterable[str] | None = None,
        sub: str | None = None,
    ) -> Block:
        block = Block(f"{self._id}.b{len(self.blocks)}", label, kind, self, sub=sub)
        for anchor, side in (
            ("left", "left"),
            ("right", "right"),
            ("top", "top"),
            ("bottom", "bottom"),
        ):
            block._add_port(anchor, side, anchor=True)
        for names, side in (
            (inputs, "left"),
            (outputs, "right"),
            (top, "top"),
            (bottom, "bottom"),
        ):
            for name in _names(names):
                block._add_port(name, side)
        self.blocks.append(block)
        return block


class Pipeline:
    def __init__(
        self, figure: "Figure", name: str | None, registers: bool, frame_type: str
    ) -> None:
        self.figure = figure
        self.name = name
        self.registers = registers
        self.frame_type = frame_type
        self.stages: list[Stage] = []

    def stage(
        self, label: str, *, group: str | None = None, color: str | None = None
    ) -> Stage:
        if any(stage.label == label for stage in self.stages):
            raise ValueError(f"duplicate stage label {label!r}")
        stage = Stage(self, f"s{len(self.stages)}", label, group, color)
        self.stages.append(stage)
        return stage

    column = stage


class Figure:
    def __init__(
        self,
        title: str,
        *,
        question: str,
        level: str = "microarchitecture",
        omit: Iterable[str] = (),
    ) -> None:
        self.title = title
        self.question = question
        self.level = level
        self.omit = list(omit)
        self._pipeline: Pipeline | None = None
        self._edges: list[Edge] = []

    def pipeline(self, *, name: str | None = None, registers: bool = True) -> Pipeline:
        if self._pipeline is not None:
            raise ValueError("a figure currently supports one layout frame")
        self._pipeline = Pipeline(self, name, registers, "pipeline")
        return self._pipeline

    def columns(self, *, name: str | None = None) -> Pipeline:
        if self._pipeline is not None:
            raise ValueError("a figure currently supports one layout frame")
        self._pipeline = Pipeline(self, name, False, "columns")
        return self._pipeline

    def wire(
        self,
        source: Port,
        destination: Port,
        *,
        label: str | None = None,
        back: bool = False,
    ) -> Edge:
        return self._edge(source, destination, kind="data", label=label, back=back)

    def bus(
        self,
        source: Port,
        destination: Port,
        *,
        width: int | str,
        label: str | None = None,
        handshake: bool = False,
        back: bool = False,
    ) -> Edge:
        return self._edge(
            source,
            destination,
            kind="bus",
            label=label,
            width=width,
            handshake=handshake,
            back=back,
        )

    def ctrl(
        self,
        source: Port,
        destination: Port,
        *,
        label: str | None = None,
        back: bool = False,
    ) -> Edge:
        return self._edge(source, destination, kind="control", label=label, back=back)

    def _edge(self, source: Port, destination: Port, **options: object) -> Edge:
        edge = Edge(source, destination, **options)
        self._edges.append(edge)
        return edge

    def lint(self) -> list[LintFinding]:
        findings: list[LintFinding] = []
        if not self.question.strip():
            findings.append(
                LintFinding("error", "state the one question this figure answers")
            )
        if self._pipeline is None or not self._pipeline.stages:
            findings.append(
                LintFinding(
                    "error", "add a layout frame with at least one stage or column"
                )
            )
            return findings
        blocks = [block for stage in self._pipeline.stages for block in stage.blocks]
        if not blocks:
            findings.append(LintFinding("error", "add at least one block"))
        accent_count = sum(block.highlighted for block in blocks)
        if accent_count > 1:
            findings.append(
                LintFinding(
                    "warning",
                    "more than one block uses the accent; the figure no longer has one clear subject",
                )
            )
        block_ids = {id(block) for block in blocks}
        stage_order = {
            id(stage): index for index, stage in enumerate(self._pipeline.stages)
        }
        for edge in self._edges:
            if (
                id(edge.source.owner) not in block_ids
                or id(edge.destination.owner) not in block_ids
            ):
                findings.append(
                    LintFinding("error", "an edge connects a block outside this figure")
                )
                continue
            source_index = stage_order[id(edge.source.owner.stage)]
            destination_index = stage_order[id(edge.destination.owner.stage)]
            if (
                destination_index == source_index
                and not edge.back
                and not edge._waypoints
            ):
                stage_blocks = edge.source.owner.stage.blocks
                source_block_index = stage_blocks.index(edge.source.owner)
                destination_block_index = stage_blocks.index(edge.destination.owner)
                facing_neighbors = (
                    destination_block_index == source_block_index + 1
                    and edge.source.side == "bottom"
                    and edge.destination.side == "top"
                ) or (
                    destination_block_index == source_block_index - 1
                    and edge.source.side == "top"
                    and edge.destination.side == "bottom"
                )
                if not facing_neighbors:
                    findings.append(
                        LintFinding(
                            "error",
                            f"same-stage edge {edge.source.owner.label} -> {edge.destination.owner.label} needs facing top/bottom ports or explicit via() waypoints",
                        )
                    )
            if destination_index < source_index and not edge.back:
                findings.append(
                    LintFinding(
                        "warning",
                        f"mark backward edge {edge.source.owner.label} -> {edge.destination.owner.label} with back=True",
                    )
                )
            if (
                destination_index > source_index + 1
                and not edge.back
                and not edge._waypoints
                and any(
                    stage.blocks
                    for stage in self._pipeline.stages[
                        source_index + 1 : destination_index
                    ]
                )
            ):
                findings.append(
                    LintFinding(
                        "error",
                        f"edge {edge.source.owner.label} -> {edge.destination.owner.label} skips an occupied stage; add explicit via() waypoints",
                    )
                )
        manual_positions = sum(block._manual_position is not None for block in blocks)
        manual_routes = sum(bool(edge._waypoints) for edge in self._edges)
        if manual_positions or manual_routes:
            findings.append(
                LintFinding(
                    "warning",
                    f"manual layout cost: {manual_positions} positioned block(s), {manual_routes} routed edge(s)",
                )
            )
        if len(blocks) > 16:
            findings.append(
                LintFinding(
                    "warning", "more than 16 blocks may hide the figure's main point"
                )
            )
        return findings

    def to_dict(self) -> dict[str, object]:
        pipeline = self._pipeline
        stages = (
            []
            if pipeline is None
            else [
                {
                    "id": stage._id,
                    "label": stage.label,
                    "group": stage.group,
                    "color": stage.color,
                    "blocks": [
                        {
                            "id": block._id,
                            "label": block.label,
                            "kind": block.kind,
                            "sub": block.sub,
                            "accent": block.highlighted,
                            "copies": block.copies,
                            "ports": [
                                {"name": port.name, "side": port.side}
                                for port in block._ports.values()
                                if not port.anchor
                            ],
                            "at": list(block._manual_position)
                            if block._manual_position
                            else None,
                        }
                        for block in stage.blocks
                    ],
                }
                for stage in pipeline.stages
            ]
        )
        return {
            "title": self.title,
            "question": self.question,
            "level": self.level,
            "omit": self.omit,
            "frame": {
                "type": pipeline.frame_type,
                "name": pipeline.name,
                "registers": pipeline.registers,
            }
            if pipeline
            else None,
            "stages": stages,
            "edges": [
                {
                    "source": f"{edge.source.owner._id}.{edge.source.name}",
                    "destination": f"{edge.destination.owner._id}.{edge.destination.name}",
                    "kind": edge.kind,
                    "label": edge.label,
                    "width": edge.width,
                    "handshake": edge.handshake,
                    "back": edge.back,
                    "via": [list(point) for point in edge._waypoints],
                }
                for edge in self._edges
            ],
        }

    def render(
        self, output: str | Path, *, png: bool = False, strict: bool = False
    ) -> Path:
        findings = self.lint()
        failures = [
            finding for finding in findings if finding.severity == "error" or strict
        ]
        if failures:
            details = "; ".join(
                f"{finding.severity}: {finding.message}" for finding in failures
            )
            raise ValueError(f"diagram lint failed: {details}")
        for finding in findings:
            logger.warning("Diagram lint: {}", finding.message)
        drawing = self._draw()
        path = Path(output)
        svg_path = path if path.suffix.lower() == ".svg" else path.with_suffix(".svg")
        svg_path.parent.mkdir(parents=True, exist_ok=True)
        drawing.save_svg(str(svg_path))
        logger.info("Wrote {}", svg_path)
        if png:
            try:
                import cairosvg
            except (ImportError, OSError) as error:
                raise RuntimeError(
                    "PNG needs CairoSVG and the native Cairo library; install both or render SVG only"
                ) from error
            png_path = svg_path.with_suffix(".png")
            cairosvg.svg2png(url=str(svg_path), write_to=str(png_path), scale=2)
            logger.info("Wrote {}", png_path)
        return svg_path

    def _draw(self) -> draw.Drawing:
        assert self._pipeline is not None
        width, height = self._layout()
        canvas = draw.Drawing(width, height, origin=(0, 0), display_inline=False)
        canvas.append(draw.Rectangle(0, 0, width, height, fill="#ffffff"))
        canvas.append(
            draw.Text(
                self.title, 20, 28, 34, font_family=FONT, font_weight="bold", fill=TEXT
            )
        )
        canvas.append(
            draw.Text(self.question, 12, 28, 56, font_family=FONT, fill=MUTED)
        )
        if self.omit:
            canvas.append(
                draw.Text(
                    f"Omitted: {', '.join(self.omit)}",
                    10,
                    28,
                    75,
                    font_family=FONT,
                    fill=MUTED,
                )
            )
        self._draw_groups(canvas)
        for stage in self._pipeline.stages:
            self._draw_stage(canvas, stage)
        if self._pipeline.registers:
            self._draw_registers(canvas)
        for index, edge in enumerate(self._edges):
            self._draw_edge(canvas, edge, index)
        for stage in self._pipeline.stages:
            for block in stage.blocks:
                self._draw_block(canvas, block)
        return canvas

    def _layout(self) -> tuple[int, int]:
        assert self._pipeline is not None
        stage_top = 108
        stage_gap = 28
        left = 28
        widths: list[float] = []
        heights: list[float] = []
        for stage in self._pipeline.stages:
            sizes = [self._block_size(block) for block in stage.blocks]
            shadows = [(block.copies - 1) * 5 for block in stage.blocks]
            block_widths = [size[0] + shadow for size, shadow in zip(sizes, shadows)]
            block_heights = [size[1] + shadow for size, shadow in zip(sizes, shadows)]
            widths.append(max([176, *(width + 30 for width in block_widths)]))
            heights.append(
                48 + sum(block_heights) + max(0, len(stage.blocks) - 1) * 18 + 24
            )
        stage_height = max([170, *heights])
        x = left
        for stage, stage_width in zip(self._pipeline.stages, widths):
            stage._box = (x, stage_top, stage_width, stage_height)
            y = stage_top + 48
            for block in stage.blocks:
                width, height = self._block_size(block)
                if block._manual_position is None:
                    block_x = x + (stage_width - width) / 2
                    block_y = y
                else:
                    block_x, block_y = (
                        coordinate * GRID for coordinate in block._manual_position
                    )
                block._box = (block_x, block_y, width, height)
                y += height + (block.copies - 1) * 5 + 18
            x += stage_width + stage_gap
        frame_right = x - stage_gap + left
        content_right, content_bottom = self._content_extents()
        feedback_channels = sum(
            edge.back or self._is_backward(edge) for edge in self._edges
        )
        height = content_bottom + 48 + feedback_channels * 16
        return int(max(frame_right, content_right + 28)), int(max(height, 320))

    def _content_extents(self) -> tuple[float, float]:
        assert self._pipeline is not None
        right = max(stage._box[0] + stage._box[2] for stage in self._pipeline.stages)
        bottom = max(stage._box[1] + stage._box[3] for stage in self._pipeline.stages)
        for stage in self._pipeline.stages:
            for block in stage.blocks:
                x, y, width, height = block._box
                shadow = (block.copies - 1) * 5
                right = max(right, x + width + shadow)
                bottom = max(bottom, y + height + shadow)
        for edge in self._edges:
            for column, row in edge._waypoints:
                right = max(right, column * GRID)
                bottom = max(bottom, row * GRID)
        return right, bottom

    @staticmethod
    def _block_size(block: Block) -> tuple[float, float]:
        subtitle_lines = (block.sub or "").splitlines()
        named_ports = [port for port in block._ports.values() if not port.anchor]
        left_length = max(
            [0, *(len(port.name) for port in named_ports if port.side == "left")]
        )
        right_length = max(
            [0, *(len(port.name) for port in named_ports if port.side == "right")]
        )
        text_length = max([len(block.label), *(len(line) for line in subtitle_lines)])
        width = min(
            280,
            max(150, text_length * 7.4 + 34, (left_length + right_length) * 5.3 + 100),
        )
        port_rows = max(
            [
                0,
                *(
                    sum(port.side == side for port in named_ports)
                    for side in ("left", "right")
                ),
            ]
        )
        header_height = 35 + len(subtitle_lines) * 13
        height = max(64, header_height + max(18, port_rows * 20))
        return width, height

    def _draw_groups(self, canvas: draw.Drawing) -> None:
        assert self._pipeline is not None
        runs: list[tuple[str, list[Stage]]] = []
        for stage in self._pipeline.stages:
            if stage.group and runs and runs[-1][0] == stage.group:
                runs[-1][1].append(stage)
            elif stage.group:
                runs.append((stage.group, [stage]))
        for label, stages in runs:
            x = stages[0]._box[0]
            right = stages[-1]._box[0] + stages[-1]._box[2]
            canvas.append(draw.Line(x, 96, right, 96, stroke=MUTED, stroke_width=1.2))
            canvas.append(
                draw.Text(
                    label,
                    10,
                    (x + right) / 2,
                    91,
                    font_family=FONT,
                    text_anchor="middle",
                    fill=MUTED,
                    font_weight="bold",
                )
            )

    def _draw_stage(self, canvas: draw.Drawing, stage: Stage) -> None:
        x, y, width, height = stage._box
        canvas.append(
            draw.Rectangle(
                x,
                y,
                width,
                height,
                rx=8,
                fill=stage.color or "#f8fafc",
                stroke="#c8d0dc",
                stroke_width=1.2,
            )
        )
        canvas.append(
            draw.Line(x, y + 34, x + width, y + 34, stroke="#d7dde6", stroke_width=1)
        )
        canvas.append(
            draw.Text(
                stage.label,
                12,
                x + width / 2,
                y + 22,
                font_family=FONT,
                text_anchor="middle",
                fill=TEXT,
                font_weight="bold",
            )
        )

    def _draw_registers(self, canvas: draw.Drawing) -> None:
        assert self._pipeline is not None
        for left, right in zip(self._pipeline.stages, self._pipeline.stages[1:]):
            x = (left._box[0] + left._box[2] + right._box[0]) / 2
            y = left._box[1] + 44
            height = left._box[3] - 54
            canvas.append(
                draw.Rectangle(
                    x - 4, y, 8, height, fill="#ffffff", stroke=STROKE, stroke_width=1
                )
            )
            canvas.append(
                draw.Lines(
                    x - 4,
                    y + height - 9,
                    x + 1,
                    y + height - 5,
                    x - 4,
                    y + height - 1,
                    close=True,
                    fill=STROKE,
                )
            )

    def _draw_block(self, canvas: draw.Drawing, block: Block) -> None:
        x, y, width, height = block._box
        fill = ACCENT if block.highlighted else FILLS[block.kind]
        for copy in range(block.copies - 1, 0, -1):
            offset = copy * 5
            canvas.append(
                draw.Rectangle(
                    x + offset,
                    y + offset,
                    width,
                    height,
                    rx=6,
                    fill=fill,
                    stroke=STROKE,
                    stroke_width=1.2,
                )
            )
        shape_options = {"fill": fill, "stroke": STROKE, "stroke_width": 1.4}
        if block.kind == "mux":
            canvas.append(
                draw.Lines(
                    x,
                    y,
                    x + width,
                    y + height * 0.22,
                    x + width,
                    y + height * 0.78,
                    x,
                    y + height,
                    close=True,
                    **shape_options,
                )
            )
        elif block.kind == "fifo":
            canvas.append(
                draw.Rectangle(x, y, width, height, rx=height / 2, **shape_options)
            )
            for fraction in (0.25, 0.5, 0.75):
                canvas.append(
                    draw.Line(
                        x + width * fraction,
                        y + height * 0.72,
                        x + width * fraction,
                        y + height,
                        stroke="#a07618",
                        stroke_width=0.9,
                    )
                )
        elif block.kind == "io":
            tip = min(24, height / 2)
            canvas.append(
                draw.Lines(
                    x,
                    y,
                    x + width - tip,
                    y,
                    x + width,
                    y + height / 2,
                    x + width - tip,
                    y + height,
                    x,
                    y + height,
                    close=True,
                    **shape_options,
                )
            )
        elif block.kind == "control":
            canvas.append(
                draw.Rectangle(x, y, width, height, rx=height / 2, **shape_options)
            )
        else:
            radius = 2 if block.kind in {"mem", "bar"} else 6
            canvas.append(
                draw.Rectangle(x, y, width, height, rx=radius, **shape_options)
            )
            if block.kind == "mem":
                canvas.append(
                    draw.Line(
                        x + 7, y, x + 7, y + height, stroke=STROKE, stroke_width=0.9
                    )
                )
                canvas.append(
                    draw.Line(
                        x + width - 7,
                        y,
                        x + width - 7,
                        y + height,
                        stroke=STROKE,
                        stroke_width=0.9,
                    )
                )
        canvas.append(
            draw.Text(
                block.label,
                12,
                x + width / 2,
                y + 23,
                font_family=FONT,
                text_anchor="middle",
                fill=TEXT,
                font_weight="bold",
            )
        )
        if block.sub:
            lines = block.sub.splitlines()
            start = y + 41
            for index, line in enumerate(lines):
                canvas.append(
                    draw.Text(
                        line,
                        9.5,
                        x + width / 2,
                        start + index * 13,
                        font_family=FONT,
                        text_anchor="middle",
                        fill=MUTED,
                    )
                )
        if block.copies > 1:
            canvas.append(
                draw.Text(
                    f"×{block.copies}",
                    9.5,
                    x + width - 7,
                    y + 13,
                    font_family=FONT,
                    text_anchor="end",
                    fill=MUTED,
                )
            )
        used = {id(edge.source) for edge in self._edges} | {
            id(edge.destination) for edge in self._edges
        }
        for port in block._ports.values():
            if id(port) not in used:
                continue
            px, py = port.point()
            canvas.append(
                draw.Circle(px, py, 2.4, fill="#ffffff", stroke=STROKE, stroke_width=1)
            )
            if not port.anchor:
                offset_x = (
                    6 if port.side == "left" else -6 if port.side == "right" else 0
                )
                anchor = (
                    "start"
                    if port.side == "left"
                    else "end"
                    if port.side == "right"
                    else "middle"
                )
                offset_y = (
                    -5
                    if port.side in {"left", "right"}
                    else 11
                    if port.side == "top"
                    else -5
                )
                canvas.append(
                    draw.Text(
                        port.name,
                        8,
                        px + offset_x,
                        py + offset_y,
                        font_family=FONT,
                        text_anchor=anchor,
                        fill=MUTED,
                    )
                )

    def _draw_edge(self, canvas: draw.Drawing, edge: Edge, index: int) -> None:
        points = self._route(edge, index)
        flat = [coordinate for point in points for coordinate in point]
        stroke_width = 4 if edge.kind == "bus" else 1.7
        dash = "6,4" if edge.kind == "control" else None
        color = CONTROL if edge.kind == "control" else STROKE
        canvas.append(
            draw.Lines(
                *flat,
                fill="none",
                stroke=color,
                stroke_width=stroke_width,
                stroke_dasharray=dash,
                stroke_linejoin="round",
            )
        )
        self._arrow(canvas, points[-2], points[-1], color, stroke_width)
        if edge.handshake:
            self._arrow(canvas, points[1], points[0], color, stroke_width)
        label_parts = [
            part
            for part in (
                edge.label,
                f"{edge.width}b" if edge.width is not None else None,
                "⇄" if edge.handshake else None,
            )
            if part
        ]
        if label_parts:
            label = " · ".join(label_parts)
            (x1, y1), (x2, y2) = max(
                zip(points, points[1:]),
                key=lambda pair: (
                    abs(pair[1][0] - pair[0][0]) + abs(pair[1][1] - pair[0][1])
                ),
            )
            x, y = (x1 + x2) / 2, (y1 + y2) / 2
            label_width = len(label) * 6.4 + 8
            if abs(x2 - x1) >= abs(y2 - y1):
                y -= 7
            else:
                x += label_width / 2 + 7
            canvas.append(
                draw.Rectangle(
                    x - label_width / 2,
                    y - 11,
                    label_width,
                    15,
                    rx=3,
                    fill="#ffffff",
                    fill_opacity=0.92,
                )
            )
            canvas.append(
                draw.Text(
                    label, 9.5, x, y, font_family=FONT, text_anchor="middle", fill=color
                )
            )

    def _route(self, edge: Edge, index: int) -> list[tuple[float, float]]:
        source = edge.source.point()
        destination = edge.destination.point()
        source_stub = self._port_stub(edge.source, source)
        destination_stub = self._port_stub(edge.destination, destination)
        if edge._waypoints:
            requested = [
                source,
                source_stub,
                *((x * GRID, y * GRID) for x, y in edge._waypoints),
                destination_stub,
                destination,
            ]
            return self._orthogonalize(requested)
        if abs(source[0] - destination[0]) < 1 and (
            (
                edge.source.side == "top"
                and edge.destination.side == "bottom"
                and source[1] > destination[1]
            )
            or (
                edge.source.side == "bottom"
                and edge.destination.side == "top"
                and source[1] < destination[1]
            )
        ):
            return [source, destination]
        if edge.back or self._is_backward(edge):
            assert self._pipeline is not None
            _, bottom = self._content_extents()
            feedback_edges = [
                candidate
                for candidate in self._edges
                if candidate.back or self._is_backward(candidate)
            ]
            channel = bottom + 24 + 16 * feedback_edges.index(edge)
            return [
                source,
                source_stub,
                (source_stub[0], channel),
                (destination_stub[0], channel),
                destination_stub,
                destination,
            ]
        source_horizontal = edge.source.side in {"left", "right"}
        destination_horizontal = edge.destination.side in {"left", "right"}
        if source_horizontal and destination_horizontal:
            middle = (source_stub[0] + destination_stub[0]) / 2
            return [
                source,
                source_stub,
                (middle, source_stub[1]),
                (middle, destination_stub[1]),
                destination_stub,
                destination,
            ]
        if not source_horizontal and not destination_horizontal:
            middle = (source_stub[1] + destination_stub[1]) / 2
            return [
                source,
                source_stub,
                (source_stub[0], middle),
                (destination_stub[0], middle),
                destination_stub,
                destination,
            ]
        return [
            source,
            source_stub,
            (destination_stub[0], source_stub[1]),
            destination_stub,
            destination,
        ]

    @staticmethod
    def _port_stub(port: Port, point: tuple[float, float]) -> tuple[float, float]:
        direction = {
            "left": (-14, 0),
            "right": (14, 0),
            "top": (0, -14),
            "bottom": (0, 14),
        }[port.side]
        return point[0] + direction[0], point[1] + direction[1]

    @staticmethod
    def _orthogonalize(
        points: list[tuple[float, float]],
    ) -> list[tuple[float, float]]:
        routed = [points[0]]
        for point in points[1:]:
            previous = routed[-1]
            if point == previous:
                continue
            if point[0] != previous[0] and point[1] != previous[1]:
                routed.append((point[0], previous[1]))
            routed.append(point)
        return routed

    def _is_backward(self, edge: Edge) -> bool:
        assert self._pipeline is not None
        order = {id(stage): index for index, stage in enumerate(self._pipeline.stages)}
        return (
            order[id(edge.destination.owner.stage)] < order[id(edge.source.owner.stage)]
        )

    @staticmethod
    def _arrow(
        canvas: draw.Drawing,
        start: tuple[float, float],
        end: tuple[float, float],
        color: str,
        stroke_width: float,
    ) -> None:
        dx, dy = end[0] - start[0], end[1] - start[1]
        length = (dx * dx + dy * dy) ** 0.5
        if length == 0:
            return
        ux, uy = dx / length, dy / length
        px, py = -uy, ux
        size = 7 + stroke_width
        base_x, base_y = end[0] - ux * size, end[1] - uy * size
        canvas.append(
            draw.Lines(
                end[0],
                end[1],
                base_x + px * size * 0.45,
                base_y + py * size * 0.45,
                base_x - px * size * 0.45,
                base_y - py * size * 0.45,
                close=True,
                fill=color,
            )
        )


__all__ = ["Block", "Edge", "Figure", "LintFinding", "Pipeline", "Port", "Stage"]
