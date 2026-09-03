# Figure extraction

A figure is quoted evidence: copy it exactly, credit it, and point to where it lives in the source.

## From a PDF

The helper finds a figure by its caption label and renders that page region, so vector art, raster images, and multi-panel figures all come out the same way. PyMuPDF ships no wheel for free-threaded CPython, so pin a stable interpreter:

```bash
uv run --python 3.12 --with pymupdf --with loguru python <skill-directory>/scripts/extract_figures.py list paper.pdf
uv run --python 3.12 --with pymupdf --with loguru python <skill-directory>/scripts/extract_figures.py extract paper.pdf --figure 3 --out figures/vaswani2017-fig3.png
```

`list` prints the page and caption of every `Figure N`, `Fig. N`, and `Figure N.M` label. It also shows whether the PDF has a text layer: a scanned PDF lists nothing. `extract` renders at 200 dpi; use `--dpi 300` for dense plots.

When the caption is found but no graphics sit beside it, or the crop cuts off part of the figure, render by region instead. Render the whole page with `--page N`, view it, and convert pixel positions to points (pixels × 72 ÷ dpi, origin at the top-left). Then pass `--page N --clip x0 y0 x1 y1`.

## From a web page

Download the original file, not a thumbnail. In the page HTML, take the image inside the `<figure>` element, prefer the largest `srcset` candidate, and strip resize parameters such as `?w=600` from the URL. Keep SVG as SVG. Fetch with `curl -L -o <path> <url>`; when the response is HTML or a 403, retry with a browser `User-Agent` header.

A figure drawn by JavaScript, such as a canvas or an interactive plot, has no file to download. Capture it with a browser screenshot of that element and say in the caption that it is a screenshot taken on that date.

## Markdown form

```markdown
![Transformer encoder-decoder stack](figures/vaswani2017-fig1.png)

*Figure 1 of Vaswani et al. (2017), p. 3, arXiv:1706.03762.*
```

Alt text says what the image shows in a few words. The caption line carries the figure label, the source, and the page or section; the References section carries the full citation. Use a relative path so the report and its folder move together.

Figures stay under the source's copyright. Keep any license the source states, and tell the user when a report will leave the team so they can check reuse rights.

## Check

View each saved image before citing it. The crop must hold the whole figure, including axis labels and legend, and no neighboring heading or paragraph. A crop that grew into surrounding text needs `--page --clip` with a tighter box.
