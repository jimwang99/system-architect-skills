import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import pymupdf

SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))

from extract_figures import CAPTION_RE, find_captions, find_figure_region  # noqa: E402

DRAWING = pymupdf.Rect(150, 200, 450, 380)
RASTER = pymupdf.Rect(100, 100, 300, 250)
TOP_TEXT_BOTTOM = 130
BOTTOM_TEXT_TOP = 450


def _make_paper(path: Path) -> None:
    """Two pages: a vector figure with body text around it, then a raster figure."""
    doc = pymupdf.open()
    page = doc.new_page(width=612, height=792)
    page.insert_textbox(
        pymupdf.Rect(72, 72, 540, TOP_TEXT_BOTTOM),
        "Figure 1 shows the block diagram of the design. " * 3,
        fontsize=10,
    )
    shape = page.new_shape()
    shape.draw_rect(DRAWING)
    shape.draw_line((DRAWING.x0, 290), (DRAWING.x1, 290))
    shape.finish(color=(0, 0, 0), width=1)
    shape.commit()
    page.insert_textbox(
        pymupdf.Rect(150, 390, 450, 410),
        "Figure 1: Synthetic block diagram.",
        fontsize=10,
        align=1,
    )
    page.insert_textbox(
        pymupdf.Rect(72, BOTTOM_TEXT_TOP, 540, 520),
        "More body text below the figure. " * 5,
        fontsize=10,
    )

    page = doc.new_page(width=612, height=792)
    pixmap = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 40, 30), False)
    pixmap.clear_with(128)
    page.insert_image(RASTER, pixmap=pixmap)
    page.insert_textbox(
        pymupdf.Rect(100, 260, 300, 280), "Fig. 2. Raster panel.", fontsize=10
    )
    doc.save(path)


class CaptionPatternTests(unittest.TestCase):
    def test_chapter_style_labels_and_body_references(self) -> None:
        self.assertEqual(CAPTION_RE.match("Figure 3.2: Latency").group("label"), "3.2")
        self.assertEqual(CAPTION_RE.match("Fig. 3. Latency").group("label"), "3")
        self.assertEqual(CAPTION_RE.match("FIGURE S1 - Extra").group("label"), "S1")
        self.assertIsNone(CAPTION_RE.match("Figure 3.3 charts the throughput"))
        self.assertIsNone(CAPTION_RE.match("Figure 1 shows the block diagram"))


class FigureRegionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.directory = tempfile.TemporaryDirectory()
        cls.pdf = Path(cls.directory.name) / "paper.pdf"
        _make_paper(cls.pdf)
        cls.doc = pymupdf.open(cls.pdf)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.doc.close()
        cls.directory.cleanup()

    def test_list_reports_captions_only(self) -> None:
        found = [(c.page_index, c.label) for c in find_captions(self.doc)]
        self.assertEqual(found, [(0, "1"), (1, "2")])

    def test_vector_figure_region_excludes_body_text(self) -> None:
        page_index, region = find_figure_region(self.doc, "1")
        self.assertEqual(page_index, 0)
        self.assertTrue(region.contains(DRAWING))
        self.assertGreater(region.y0, TOP_TEXT_BOTTOM)
        self.assertLess(region.y1, BOTTOM_TEXT_TOP)

    def test_raster_figure_region_covers_image(self) -> None:
        page_index, region = find_figure_region(self.doc, "2")
        self.assertEqual(page_index, 1)
        self.assertTrue(region.contains(RASTER))

    def test_missing_figure_fails_without_output(self) -> None:
        script = SKILL_DIR / "scripts" / "extract_figures.py"
        out = Path(self.directory.name) / "missing.png"
        result = subprocess.run(
            [sys.executable, str(script), "extract", str(self.pdf), "--figure", "9", "--out", str(out)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("no caption for figure 9", result.stderr)
        self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
