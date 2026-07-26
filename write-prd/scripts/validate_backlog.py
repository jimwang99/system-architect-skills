#!/usr/bin/env python3
"""Validate a decision-backlog entry against spec 03 (docs/specs/workflow/03-write-prd.md)."""
import os, re, sys

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
H1_RE = re.compile(r"^# (.+)$")
H2_RE = re.compile(r"^## (.+)$")
KEY_RE = re.compile(r"^- ([A-Za-z][A-Za-z ]*): ?(.*)$")
PLACEHOLDERS = {"tbd", "todo"}

def is_placeholder(value):
    return value.strip().lower() in PLACEHOLDERS

def logical_lines(text):
    """Yield (lineno, line, in_fence). Fence-toggling lines are themselves in-fence."""
    fence = False
    for i, line in enumerate(text.split("\n"), 1):
        if line.strip().startswith("```"):
            fence = not fence
            yield i, line, True
            continue
        yield i, line, fence

def validate(path):
    errs = []
    name = os.path.basename(path)
    stem = name[:-3] if name.endswith(".md") else name
    if not name.endswith(".md") or not SLUG_RE.match(stem):
        errs.append((1, "filename is not a legal slug ending .md: %s" % name))
    with open(path, encoding="utf-8") as f:
        text = f.read()
    lines = list(logical_lines(text))

    h1s = [(n, l) for n, l, fenced in lines if not fenced and H1_RE.match(l)]
    h2s = [(n, H2_RE.match(l).group(1)) for n, l, fenced in lines if not fenced and H2_RE.match(l)]
    first_content = next((n for n, l, fenced in lines if l.strip()), None)
    if not h1s:
        errs.append((1, "missing H1 question"))
    else:
        if len(h1s) > 1:
            errs.append((h1s[1][0], "more than one H1"))
        if first_content != h1s[0][0]:
            errs.append((h1s[0][0], "H1 is not the first content line"))
        if not H1_RE.match(h1s[0][1]).group(1).strip():
            errs.append((h1s[0][0], "H1 question is empty"))

    h1_line = h1s[0][0] if h1s else 0
    first_h2 = h2s[0][0] if h2s else len(lines) + 1

    meta = {}
    for n, l, fenced in lines:
        if fenced:
            continue
        m = KEY_RE.match(l)
        if not m or m.group(1) not in ("Type", "Origin"):
            continue
        key, val = m.group(1), m.group(2)
        meta.setdefault(key, []).append((n, val))
        if not (h1_line < n < first_h2):
            errs.append((n, "%s must appear between the H1 and the first section" % key))
    for key in ("Type", "Origin"):
        hits = meta.get(key, [])
        if not hits:
            errs.append((1, "missing required key: %s" % key))
        elif len(hits) > 1:
            errs.append((hits[1][0], "duplicate key: %s" % key))
    if meta.get("Type"):
        n, val = meta["Type"][0]
        if val.strip() not in ("product", "architecture"):
            errs.append((n, "Type must be product or architecture"))
    if meta.get("Origin"):
        n, val = meta["Origin"][0]
        if not val.strip():
            errs.append((n, "Origin is empty"))
        elif is_placeholder(val):
            errs.append((n, "Origin is a placeholder"))

    ctx = [n for n, title in h2s if title.strip() == "Context"]
    if not ctx:
        errs.append((1, "missing ## Context section"))
    else:
        start = ctx[0]
        end = min([n for n, _ in h2s if n > start] or [len(lines) + 1])
        body = [l for n, l, fenced in lines if start < n < end and l.strip()]
        if not body:
            errs.append((start, "Context section is empty"))
        elif is_placeholder("\n".join(body)):
            errs.append((start, "Context content is a placeholder"))
    return errs

def main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: validate_backlog.py <path>\n")
        return 2
    path = argv[1]
    try:
        errs = validate(path)
    except (OSError, UnicodeDecodeError) as e:
        sys.stderr.write("%s: unreadable: %s\n" % (path, e))
        return 2
    for n, msg in sorted(errs):
        sys.stderr.write("%s:%d: %s\n" % (path, n, msg))
    return 1 if errs else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
