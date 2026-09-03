#!/usr/bin/env python3
"""Cut one numbered figure out of a paper PDF as a PNG for a Markdown report.

Vector figures have no embedded image to copy, so the figure is located by its
caption and the page region beside it is rendered instead.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import pymupdf
from loguru import logger

# A caption starts a text block with the label and a separator ("Figure 3:",
# "Fig. 3.", "Figure 3.1:", "FIGURE S1 -"). Body text such as "Figure 3 shows"
# has a word after the label, so it does not match.
CAPTION_RE = re.compile(
    r"^\s*(?:Figure|Fig\.?|FIGURE|FIG\.?)\s*(?P<label>[A-Z]?\d+(?:\.\d+)?)\s*(?:[:–—|-]|\.(?!\d)|\n|$)"
)

# Distances are in PDF points (1/72 inch).
CAPTION_GAP = 60.0  # largest gap between caption and the nearest graphic
CHAIN_GAP = 40.0  # largest gap between stacked graphics that belong together
TEXT_MARGIN = 12.0  # labels this close to the graphics belong to the figure
PADDING = 6.0
RULE_THICKNESS = 2.0  # thinner drawings are header or footnote rules, not art


@dataclass
class Caption:
    page_index: int
    label: str
    rect: pymupdf.Rect
    text: str


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)

    listing = commands.add_parser("list", help="print every figure caption found")
    listing.add_argument("pdf", type=Path)

    extract = commands.add_parser("extract", help="render one figure to PNG")
    extract.add_argument("pdf", type=Path)
    extract.add_argument("--out", type=Path, required=True, help="PNG path")
    extract.add_argument("--figure", help="figure label, such as 3 or S1")
    extract.add_argument("--page", type=int, help="1-based page number")
    extract.add_argument(
        "--clip",
        type=float,
        nargs=4,
        metavar=("X0", "Y0", "X1", "Y1"),
        help="region in PDF points; needs --page",
    )
    extract.add_argument("--dpi", type=int, default=200)
    return parser


def find_captions(doc: pymupdf.Document) -> list[Caption]:
    captions: list[Caption] = []
    for page in doc:
        for block in page.get_text("blocks"):
            x0, y0, x1, y1, text, _, block_type = block
            if block_type != 0:
                continue
            match = CAPTION_RE.match(text)
            if match:
                captions.append(
                    Caption(
                        page.number,
                        match.group("label"),
                        pymupdf.Rect(x0, y0, x1, y1),
                        " ".join(text.split()),
                    )
                )
    return captions


def _graphic_rects(page: pymupdf.Page) -> list[pymupdf.Rect]:
    rects = [pymupdf.Rect(info["bbox"]) for info in page.get_image_info()]
    for rect in page.cluster_drawings():
        if rect.height >= RULE_THICKNESS and rect.width >= RULE_THICKNESS:
            rects.append(rect)
    return [rect for rect in rects if not rect.is_empty]


def _overlaps_horizontally(a: pymupdf.Rect, b: pymupdf.Rect) -> bool:
    return min(a.x1, b.x1) > max(a.x0, b.x0)


def _chain(
    caption: pymupdf.Rect, rects: list[pymupdf.Rect], above: bool
) -> pymupdf.Rect | None:
    """Union the graphics stacked next to the caption on one side of it."""
    if above:
        near = [r for r in rects if r.y1 <= caption.y0 + PADDING]
        near.sort(key=lambda r: r.y1, reverse=True)
    else:
        near = [r for r in rects if r.y0 >= caption.y1 - PADDING]
        near.sort(key=lambda r: r.y0)
    near = [r for r in near if _overlaps_horizontally(r, caption)]
    if not near:
        return None
    first = near[0]
    gap = caption.y0 - first.y1 if above else first.y0 - caption.y1
    if gap > CAPTION_GAP:
        return None
    region = pymupdf.Rect(first)
    for rect in near[1:]:
        gap = region.y0 - rect.y1 if above else rect.y0 - region.y1
        if gap > CHAIN_GAP:
            break
        region |= rect
    return region


def _fraction_inside(rect: pymupdf.Rect, container: pymupdf.Rect) -> float:
    inside = pymupdf.Rect(rect) & container
    return 0.0 if inside.is_empty else inside.get_area() / rect.get_area()


def _text_blocks(page: pymupdf.Page) -> list[tuple[pymupdf.Rect, float]]:
    """Return every text block with its largest font size."""
    blocks: list[tuple[pymupdf.Rect, float]] = []
    for block in page.get_text("dict")["blocks"]:
        if block["type"] != 0:
            continue
        sizes = [span["size"] for line in block["lines"] for span in line["spans"]]
        blocks.append((pymupdf.Rect(block["bbox"]), max(sizes, default=0.0)))
    return blocks


def _body_font_size(doc: pymupdf.Document) -> float:
    """The font size carrying most characters in the document, so the body text size.

    Measured over the whole document because one page full of tick labels
    would otherwise make the body text look like a heading.
    """
    weight: dict[float, int] = {}
    for page in doc:
        for block in page.get_text("dict")["blocks"]:
            if block["type"] != 0:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    size = round(span["size"], 1)
                    weight[size] = weight.get(size, 0) + len(span["text"])
    return max(weight, key=weight.get) if weight else 0.0


def _absorb_labels(
    page: pymupdf.Page, region: pymupdf.Rect, caption: pymupdf.Rect, body_size: float
) -> tuple[pymupdf.Rect, list[pymupdf.Rect]]:
    """Grow the region over axis labels and legends that sit just outside the art.

    Headings and paragraphs also sit close to a figure. Headings are larger
    than body text and paragraphs span the column, so a block is taken only
    when it is no larger than body text and either narrow or over the art.
    Returns the grown region and the text blocks that were kept out.
    """
    halo = pymupdf.Rect(region) + (-TEXT_MARGIN, -TEXT_MARGIN, TEXT_MARGIN, TEXT_MARGIN)
    grown = pymupdf.Rect(region)
    kept_out: list[pymupdf.Rect] = []
    for rect, size in _text_blocks(page):
        if rect.is_empty or rect.intersects(caption):
            continue
        narrow = rect.width < 0.6 * region.width
        if (
            size <= body_size + 0.5
            and _fraction_inside(rect, halo) >= 0.5
            and (narrow or _fraction_inside(rect, region) >= 0.5)
        ):
            grown |= rect
        else:
            kept_out.append(rect)
    return grown, kept_out


def _pad(region: pymupdf.Rect, kept_out: list[pymupdf.Rect]) -> pymupdf.Rect:
    """Pad the crop, but stop short of text that was kept out of the figure."""
    padded = pymupdf.Rect(region) + (-PADDING, -PADDING, PADDING, PADDING)
    for rect in kept_out:
        if (pymupdf.Rect(rect) & padded).is_empty:
            continue
        # Text boxes include descender space, so a heading can overlap the art
        # edge by a fraction of a point; decide the side by the box center and
        # never cut into the art itself.
        center = (rect.y0 + rect.y1) / 2
        if center < region.y0:
            padded.y0 = max(padded.y0, min(rect.y1, region.y0))
        elif center > region.y1:
            padded.y1 = min(padded.y1, max(rect.y0, region.y1))
    return padded


def find_figure_region(
    doc: pymupdf.Document, label: str
) -> tuple[int, pymupdf.Rect]:
    """Return the page index and the clip rectangle for the figure with this label."""
    matches = [c for c in find_captions(doc) if c.label == label]
    if not matches:
        raise LookupError(f"no caption for figure {label}; run `list` to see labels")
    body_size = _body_font_size(doc)
    for caption in matches:
        page = doc[caption.page_index]
        rects = _graphic_rects(page)
        for above in (True, False):
            region = _chain(caption.rect, rects, above)
            if region is None:
                continue
            region, kept_out = _absorb_labels(page, region, caption.rect, body_size)
            region |= caption.rect
            region = _pad(region, kept_out) & page.rect
            logger.info(
                "figure {} on page {} ({} the caption): {}",
                label,
                caption.page_index + 1,
                "above" if above else "below",
                caption.text[:80],
            )
            return caption.page_index, region
    pages = ", ".join(str(c.page_index + 1) for c in matches)
    raise LookupError(
        f"caption for figure {label} found on page {pages} but no graphics next to it; "
        "render with --page and --clip instead"
    )


def render(doc: pymupdf.Document, page_index: int, clip: pymupdf.Rect | None, dpi: int, out: Path) -> None:
    page = doc[page_index]
    pixmap = page.get_pixmap(clip=clip, dpi=dpi, alpha=False)
    out.parent.mkdir(parents=True, exist_ok=True)
    pixmap.save(out)
    logger.info("wrote {} ({}x{} px)", out, pixmap.width, pixmap.height)


def main() -> None:
    args = _parser().parse_args()
    doc = pymupdf.open(args.pdf)
    if args.command == "list":
        captions = find_captions(doc)
        if not captions:
            logger.warning("no figure captions found; the PDF may be scanned or use unusual labels")
        for caption in captions:
            print(f"page {caption.page_index + 1}\tfigure {caption.label}\t{caption.text[:100]}")
        return

    if args.figure is not None and (args.page is not None or args.clip is not None):
        raise SystemExit("use --figure alone, or --page with optional --clip")
    if args.figure is not None:
        page_index, clip = find_figure_region(doc, args.figure)
    elif args.page is not None:
        if not 1 <= args.page <= doc.page_count:
            raise SystemExit(f"page must be between 1 and {doc.page_count}")
        page_index = args.page - 1
        clip = pymupdf.Rect(*args.clip) if args.clip else None
    else:
        raise SystemExit("give --figure, or --page with optional --clip")
    render(doc, page_index, clip, args.dpi, args.out)


if __name__ == "__main__":
    try:
        main()
    except LookupError as error:
        logger.error(str(error))
        sys.exit(1)
