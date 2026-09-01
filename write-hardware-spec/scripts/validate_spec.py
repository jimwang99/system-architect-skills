#!/usr/bin/env python3
"""Mechanical validation for hardware specification Markdown files."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
MERMAID_FENCE_RE = re.compile(r"^\s*```mermaid\s*$", re.IGNORECASE)
FR_RE = re.compile(r"\bFR-\d{2,}\b")
TR_RE = re.compile(r"\bTR-\d{2,}\b")
FSM_RE = re.compile(r"\bFSM-[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d{2,}\b")
TEST_RE = re.compile(r"\bT-\d{2,}\b")
MARKER_RE = re.compile(
    r"\b(?:TODO|TBD|FIXME)\b|\{\{[^{}\n]+\}\}|"
    r"<(?:INSERT|PLACEHOLDER|TBD|BLOCK(?:\s+NAME)?|MODULE(?:\s+NAME)?|"
    r"SIGNAL(?:\s+NAME)?|NAME|VALUE|DESCRIPTION|TEXT|ID|PATH)[^>\n]*>",
    re.IGNORECASE,
)
FORBIDDEN_DIAGRAM_RES = (
    re.compile(r"```\s*(?:dot|graphviz)\b", re.IGNORECASE),
    re.compile(
        r'\b(?:strict\s+)?(?:di)?graph(?:\s+(?:[A-Za-z_]\w*|"[^"]+"))?\s*\{',
        re.IGNORECASE,
    ),
    re.compile(r"!\[[^]]*\]\s*(?:\([^)]*\)|\[[^]]*\])"),
    re.compile(r"<img\b", re.IGNORECASE),
)
DIAGRAM_HEADING_TERMS = (
    "diagram",
    "flow chart",
    "flowchart",
    "state sketch",
    "fsm sketch",
    "control flow",
    "data flow",
)
VAGUE_TIMING_RE = re.compile(
    r"\b(?:low latency|high throughput|fast|quick)\b", re.IGNORECASE
)

MERGED_REQUIRED = (
    "purpose",
    "parameters",
    "interfaces",
    "functional requirements",
    "timing requirements",
    "reset-visible behavior",
    "non-goals",
    "block diagram",
    "implementation detail",
    "sub-block decomposition",
    "internal signals and storage",
    "reset behavior",
    "critical timing paths",
    "requirement mapping",
    "test plan",
)
ARCH_REQUIRED = (
    "purpose",
    "parameters",
    "interfaces",
    "functional requirements",
    "timing requirements",
    "reset-visible behavior",
    "non-goals",
    "block diagram",
)
UARCH_REQUIRED = (
    "block diagram",
    "sub-block decomposition",
    "internal signals and storage",
    "reset behavior",
    "critical timing paths",
    "requirement mapping",
    "test plan",
)


@dataclass(frozen=True, order=True)
class Diagnostic:
    path: str
    line: int
    code: str
    message: str


@dataclass(frozen=True)
class Report:
    files: tuple[str, ...]
    diagnostics: tuple[Diagnostic, ...]

    @property
    def ok(self) -> bool:
        return not self.diagnostics


@dataclass(frozen=True)
class Heading:
    level: int
    title: str
    normalized: str
    line: int
    end_line: int


@dataclass(frozen=True)
class Document:
    path: Path
    lines: tuple[str, ...]
    headings: tuple[Heading, ...]


def _normalize_heading(title: str) -> str:
    cleaned = re.sub(r"[`*_]", "", title)
    return re.sub(r"\s+", " ", cleaned).strip().lower()


def _read_document(path: Path) -> Document:
    lines = tuple(path.read_text().splitlines())
    raw: list[tuple[int, int, str]] = []
    for line_number, line in enumerate(lines, start=1):
        match = HEADING_RE.match(line)
        if match:
            raw.append((line_number, len(match.group(1)), match.group(2).strip()))

    headings: list[Heading] = []
    for index, (line_number, level, title) in enumerate(raw):
        end_line = len(lines)
        for next_line, next_level, _ in raw[index + 1 :]:
            if next_level <= level:
                end_line = next_line - 1
                break
        headings.append(
            Heading(level, title, _normalize_heading(title), line_number, end_line)
        )
    return Document(path, lines, tuple(headings))


def _section_lines(
    document: Document, predicate: Callable[[Heading], bool]
) -> list[tuple[int, str]]:
    selected: list[tuple[int, str]] = []
    for heading in document.headings:
        if not predicate(heading):
            continue
        for line_number in range(heading.line + 1, heading.end_line + 1):
            selected.append((line_number, document.lines[line_number - 1]))
    return selected


def _definition_pattern(id_pattern: str) -> re.Pattern[str]:
    return re.compile(
        rf"^\s*(?:(?:\d+[.)]|[-*])\s+)?(?:\|\s*)?(?:\*\*|`)?"
        rf"(?P<id>{id_pattern})(?:\*\*|`)?(?=\s*[:|]|\b)"
    )


FR_DEFINITION_RE = _definition_pattern(r"FR-\d{2,}")
TR_DEFINITION_RE = _definition_pattern(r"TR-\d{2,}")
FSM_DEFINITION_RE = _definition_pattern(
    r"FSM-[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d{2,}"
)
TEST_DEFINITION_RE = _definition_pattern(r"T-\d{2,}")


def _discover(target: Path) -> tuple[list[Path], list[Diagnostic]]:
    if not target.exists():
        return [], [
            Diagnostic(str(target), 0, "INPUT_NOT_FOUND", "target does not exist")
        ]
    if target.is_file():
        if target.suffix.lower() != ".md":
            return [], [
                Diagnostic(
                    str(target), 0, "NO_MARKDOWN", "target is not a Markdown file"
                )
            ]
        return [target], []
    paths = sorted(path for path in target.rglob("*.md") if path.is_file())
    if not paths:
        return [], [
            Diagnostic(
                str(target), 0, "NO_MARKDOWN", "directory contains no Markdown files"
            )
        ]
    return paths, []


def _infer_format(paths: Sequence[Path]) -> str:
    if any(path.name.endswith(("_arch.md", "_uarch.md")) for path in paths):
        return "split"
    return "merged"


def _missing_sections(
    document: Document, required: Sequence[str]
) -> list[Diagnostic]:
    present = {heading.normalized for heading in document.headings}
    return [
        Diagnostic(
            str(document.path),
            1,
            "MISSING_SECTION",
            f"missing required section: {name}",
        )
        for name in required
        if name not in present
    ]


def _is_transition_row(line: str) -> bool:
    stripped = line.strip()
    if not stripped.startswith("|"):
        return False
    cells = [cell.strip() for cell in stripped.strip("|").split("|")]
    if len(cells) < 3:
        return False
    if all(re.fullmatch(r":?-{3,}:?", cell or "-") for cell in cells):
        return False
    return cells[0].lower() not in {"id", "transition id"}


def _add_definitions(
    destination: dict[str, list[tuple[str, int]]],
    document: Document,
    lines: Sequence[tuple[int, str]],
    pattern: re.Pattern[str],
) -> None:
    for line_number, line in lines:
        match = pattern.match(line)
        if match:
            destination.setdefault(match.group("id"), []).append(
                (str(document.path), line_number)
            )


def _validate_ids(documents: Sequence[Document]) -> list[Diagnostic]:
    definitions: dict[str, list[tuple[str, int]]] = {}
    tests: dict[str, list[tuple[str, int]]] = {}
    test_mappings: dict[str, set[str]] = {}
    mapping_references: list[tuple[str, str, str, int]] = []
    fsm_verification_mappings: set[str] = set()
    fsm_verification_references: set[tuple[str, str, int]] = set()
    diagnostics: list[Diagnostic] = []

    for document in documents:
        _add_definitions(
            definitions,
            document,
            _section_lines(
                document,
                lambda heading: heading.normalized == "functional requirements",
            ),
            FR_DEFINITION_RE,
        )
        _add_definitions(
            definitions,
            document,
            _section_lines(
                document, lambda heading: heading.normalized == "timing requirements"
            ),
            TR_DEFINITION_RE,
        )
        transition_lines = _section_lines(
            document, lambda heading: "transitions" in heading.normalized
        )
        _add_definitions(
            definitions, document, transition_lines, FSM_DEFINITION_RE
        )
        for line_number, line in transition_lines:
            if _is_transition_row(line) and not FSM_DEFINITION_RE.match(line):
                diagnostics.append(
                    Diagnostic(
                        str(document.path),
                        line_number,
                        "FSM_ID_MISSING",
                        "FSM transition row has no stable FSM-<NAME>-<NN> ID",
                    )
                )

        test_lines = _section_lines(
            document, lambda heading: heading.normalized == "test plan"
        )
        for line_number, line in test_lines:
            match = TEST_DEFINITION_RE.match(line)
            if not match:
                continue
            test_id = match.group("id")
            tests.setdefault(test_id, []).append((str(document.path), line_number))
            mapped = (
                set(FR_RE.findall(line))
                | set(TR_RE.findall(line))
                | set(FSM_RE.findall(line))
            )
            test_mappings.setdefault(test_id, set()).update(mapped)
            mapping_references.extend(
                (test_id, mapped_id, str(document.path), line_number)
                for mapped_id in sorted(mapped)
            )
            if not mapped:
                diagnostics.append(
                    Diagnostic(
                        str(document.path),
                        line_number,
                        "TEST_WITHOUT_MAPPING",
                        f"{test_id} does not map to an FR, TR, or FSM transition",
                    )
                )

        verification_lines = _section_lines(
            document,
            lambda heading: "assertion" in heading.normalized
            or "coverage" in heading.normalized,
        )
        for line_number, line in verification_lines:
            for mapped_id in FSM_RE.findall(line):
                fsm_verification_mappings.add(mapped_id)
                fsm_verification_references.add(
                    (mapped_id, str(document.path), line_number)
                )

    for identifier, locations in definitions.items():
        if len(locations) > 1:
            for path, line in locations[1:]:
                diagnostics.append(
                    Diagnostic(
                        path,
                        line,
                        "DUPLICATE_DEFINITION",
                        f"duplicate definition: {identifier}",
                    )
                )
    for identifier, locations in tests.items():
        if len(locations) > 1:
            for path, line in locations[1:]:
                diagnostics.append(
                    Diagnostic(
                        path,
                        line,
                        "DUPLICATE_TEST",
                        f"duplicate test definition: {identifier}",
                    )
                )

    for test_id, mapped_id, path, line in mapping_references:
        if mapped_id not in definitions:
            diagnostics.append(
                Diagnostic(
                    path,
                    line,
                    "UNKNOWN_MAPPING",
                    f"{test_id} maps to undefined ID: {mapped_id}",
                )
            )
    for mapped_id, path, line in sorted(fsm_verification_references):
        if mapped_id not in definitions:
            diagnostics.append(
                Diagnostic(
                    path,
                    line,
                    "UNKNOWN_MAPPING",
                    f"assertion or coverage item maps to undefined ID: {mapped_id}",
                )
            )

    covered = set().union(*test_mappings.values()) if test_mappings else set()
    for identifier, locations in definitions.items():
        if identifier.startswith("FSM-"):
            if (
                identifier not in covered
                and identifier not in fsm_verification_mappings
            ):
                path, line = locations[0]
                diagnostics.append(
                    Diagnostic(
                        path,
                        line,
                        "UNCOVERED_TRANSITION",
                        f"no test, assertion, or coverage target maps to {identifier}",
                    )
                )
            continue
        if identifier not in covered:
            path, line = locations[0]
            diagnostics.append(
                Diagnostic(
                    path,
                    line,
                    "UNCOVERED_REQUIREMENT",
                    f"no test maps to {identifier}",
                )
            )
    return diagnostics


def _validate_hygiene(
    documents: Sequence[Document], selected_format: str
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for document in documents:
        for heading in document.headings:
            if not any(term in heading.normalized for term in DIAGRAM_HEADING_TERMS):
                continue
            section = document.lines[heading.line : heading.end_line]
            if not any(MERMAID_FENCE_RE.match(line) for line in section):
                diagnostics.append(
                    Diagnostic(
                        str(document.path),
                        heading.line,
                        "MISSING_MERMAID_DIAGRAM",
                        "diagram section has no Mermaid diagram",
                    )
                )
        for line_number, line in enumerate(document.lines, start=1):
            if MARKER_RE.search(line):
                diagnostics.append(
                    Diagnostic(
                        str(document.path),
                        line_number,
                        "UNRESOLVED_MARKER",
                        "unresolved marker",
                    )
                )
            if any(pattern.search(line) for pattern in FORBIDDEN_DIAGRAM_RES):
                diagnostics.append(
                    Diagnostic(
                        str(document.path),
                        line_number,
                        "FORBIDDEN_DIAGRAM",
                        "block diagrams and flow charts must use Mermaid, not Graphviz or images",
                    )
                )

        timing_lines = _section_lines(
            document, lambda heading: heading.normalized == "timing requirements"
        )
        for line_number, line in timing_lines:
            without_ids = FR_RE.sub(
                "", TR_RE.sub("", FSM_RE.sub("", TEST_RE.sub("", line)))
            )
            if VAGUE_TIMING_RE.search(without_ids) and not re.search(
                r"\d", without_ids
            ):
                diagnostics.append(
                    Diagnostic(
                        str(document.path),
                        line_number,
                        "VAGUE_TIMING",
                        "timing phrase has no numeric quantity",
                    )
                )

    return diagnostics


def validate(target: Path, requested_format: str = "auto") -> Report:
    """Read target specs and return deterministic diagnostics without mutation."""
    paths, diagnostics = _discover(target)
    if not paths:
        return Report((), tuple(sorted(diagnostics)))

    documents = [_read_document(path) for path in paths]
    selected_format = (
        _infer_format(paths) if requested_format == "auto" else requested_format
    )

    if selected_format == "merged":
        for document in documents:
            diagnostics.extend(_missing_sections(document, MERGED_REQUIRED))
    else:
        arch = {
            path.name[: -len("_arch.md")]: path
            for path in paths
            if path.name.endswith("_arch.md")
        }
        uarch = {
            path.name[: -len("_uarch.md")]: path
            for path in paths
            if path.name.endswith("_uarch.md")
        }
        if not arch and not uarch:
            diagnostics.append(
                Diagnostic(
                    str(target),
                    0,
                    "SPLIT_PAIR_MISSING",
                    "split format requires <block>_arch.md and <block>_uarch.md",
                )
            )
        for block in sorted(set(arch) | set(uarch)):
            if block not in arch:
                diagnostics.append(
                    Diagnostic(
                        str(target),
                        0,
                        "SPLIT_PAIR_MISSING",
                        f"missing {block}_arch.md",
                    )
                )
            if block not in uarch:
                diagnostics.append(
                    Diagnostic(
                        str(target),
                        0,
                        "SPLIT_PAIR_MISSING",
                        f"missing {block}_uarch.md",
                    )
                )
        for document in documents:
            if document.path.name.endswith("_arch.md"):
                diagnostics.extend(_missing_sections(document, ARCH_REQUIRED))
            elif document.path.name.endswith("_uarch.md"):
                diagnostics.extend(_missing_sections(document, UARCH_REQUIRED))

    diagnostics.extend(_validate_ids(documents))
    diagnostics.extend(_validate_hygiene(documents, selected_format))
    return Report(
        tuple(str(path) for path in paths),
        tuple(sorted(set(diagnostics))),
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI; return 0 for a clean report and 1 for validation errors."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path)
    parser.add_argument(
        "--format",
        choices=("auto", "merged", "split"),
        default="auto",
        dest="requested_format",
    )
    args = parser.parse_args(argv)
    report = validate(args.target, args.requested_format)
    for diagnostic in report.diagnostics:
        location = diagnostic.path
        if diagnostic.line:
            location += f":{diagnostic.line}"
        print(f"{location}: {diagnostic.code}: {diagnostic.message}")
    print(f"Checked {len(report.files)} Markdown file(s).")
    print(
        "Mechanical validation does not establish semantic hardware correctness; "
        "independent review is still required."
    )
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
