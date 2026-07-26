#!/usr/bin/env python3
"""Validate a docs/learnings/ALI-NNN.md file against spec 06's grammar.

Spec: docs/specs/workflow/06-act-learn-improve-integration.md.
Stdlib only, Python 3.9+. Exit 0 pass; 1 with "path:line: message" per
violation on stderr; 2 on usage error or unreadable file.
"""
import os
import re
import sys

FILENAME = re.compile(r"^ALI-([0-9]{3})\.md$")
H1 = re.compile(r"^# ALI-([0-9]{3}): (.+)$")
HEADER = re.compile(r"^(Date|Phase|Status): ?(.*)$")
WHAT = re.compile(r"^\*\*What happened:\*\* ?(.*)$")
L_HEAD = re.compile(r"^## L([0-9]+): (.+)$")
KEY = re.compile(r"^- \*\*(What we assumed|What is actually true|Evidence|Why the assumption was wrong|Class of error|Improvement items):\*\* ?(.*)$")
ITEM = re.compile(r"^\s+- \*\*(P[0-2]) — ([^:]+):\*\* ?(.*)$")
PHASES = {"design", "implementation", "debugging", "testing"}
STATUSES = {"draft", "approved"}
KEY_ORDER = ["What we assumed", "What is actually true", "Evidence",
             "Why the assumption was wrong", "Class of error", "Improvement items"]
PLACEHOLDERS = {"tbd", "todo"}


def is_placeholder(v):
    return v.strip().lower() in PLACEHOLDERS


def logical_lines(text):
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
    fname = FILENAME.match(name)
    file_num = None
    if not fname or fname.group(1) == "000":
        errs.append((1, "filename must match ALI-NNN.md (NNN 001-999)"))
    else:
        file_num = fname.group(1)
    with open(path, encoding="utf-8") as fh:
        lines = list(logical_lines(fh.read()))
    content = [(n, l) for n, l, fenced in lines if not fenced]

    first = next(((n, l) for n, l in content if l.strip()), None)
    h1 = H1.match(first[1]) if first else None
    if not first or not h1:
        errs.append((first[0] if first else 1, "first content line must be '# ALI-NNN: <title>'"))
    elif file_num and h1.group(1) != file_num:
        errs.append((first[0], "H1 number ALI-%s does not match filename ALI-%s" % (h1.group(1), file_num)))

    what_line = next((n for n, l in content if WHAT.match(l)), None)
    headers = {}
    order = []
    for n, l in content:
        m = HEADER.match(l)
        if not m:
            continue
        if what_line is not None and n > what_line:
            continue
        key, val = m.group(1), m.group(2)
        if key in headers:
            errs.append((n, "duplicate header '%s'" % key))
            continue
        headers[key] = (val, n)
        order.append(key)
    for req in ("Date", "Phase", "Status"):
        if req not in headers:
            errs.append((1, "missing header '%s' before **What happened:**" % req))
    if order != [k for k in ("Date", "Phase", "Status") if k in headers]:
        errs.append((headers[order[0]][1], "headers must appear in order Date, Phase, Status"))
    if "Date" in headers and not headers["Date"][0].strip():
        errs.append((headers["Date"][1], "Date is empty"))
    if "Phase" in headers and headers["Phase"][0] not in PHASES:
        errs.append((headers["Phase"][1], "Phase must be one of design|implementation|debugging|testing"))
    if "Status" in headers and headers["Status"][0] not in STATUSES:
        errs.append((headers["Status"][1], "Status must be draft or approved"))

    if what_line is None:
        errs.append((1, "missing '**What happened:**' line"))
    else:
        val = WHAT.match(dict(content)[what_line]).group(1)
        if not val.strip():
            errs.append((what_line, "What happened is empty"))
        elif is_placeholder(val):
            errs.append((what_line, "What happened is a placeholder"))

    sections = []
    cur = None
    for n, l in content:
        lh = L_HEAD.match(l)
        if lh:
            cur = {"num": int(lh.group(1)), "line": n, "keys": [], "items": [], "last": None}
            sections.append(cur)
            continue
        if cur is None:
            continue
        km = KEY.match(l)
        if km:
            cur["keys"].append((km.group(1), km.group(2), n))
            cur["last"] = km.group(1)
            continue
        im = ITEM.match(l)
        if im and cur["last"] == "Improvement items":
            cur["items"].append((im.group(1), im.group(2), im.group(3), n))

    if not sections:
        errs.append((1, "at least one '## L<N>:' section required"))
    nums = [s["num"] for s in sections]
    if nums != list(range(1, len(nums) + 1)):
        errs.append((sections[0]["line"] if sections else 1, "L-sections must be ascending and contiguous from L1"))

    for s in sections:
        seen = [k for k, v, n in s["keys"]]
        for req in KEY_ORDER:
            if seen.count(req) == 0:
                errs.append((s["line"], "L%d missing key '%s'" % (s["num"], req)))
            elif seen.count(req) > 1:
                dup = [n for k, v, n in s["keys"] if k == req][1]
                errs.append((dup, "L%d duplicate key '%s'" % (s["num"], req)))
        present = [k for k in seen if k in KEY_ORDER]
        expected = [k for k in KEY_ORDER if k in present]
        if present != expected:
            errs.append((s["keys"][0][2], "L%d keys out of order" % s["num"]))
        for k, v, n in s["keys"]:
            if k == "Improvement items":
                continue
            if not v.strip():
                errs.append((n, "'%s' is empty" % k))
            elif k != "Evidence" and is_placeholder(v):
                errs.append((n, "'%s' is a placeholder" % k))
        if any(k == "Improvement items" for k, v, n in s["keys"]):
            if not s["items"]:
                item_line = next(n for k, v, n in s["keys"] if k == "Improvement items")
                errs.append((item_line, "L%d Improvement items has no '- **P<n> — <class>:**' bullets" % s["num"]))
            for pri, cls, tail, n in s["items"]:
                if not cls.strip() or not tail.strip():
                    errs.append((n, "improvement item needs a target class and a non-empty tail"))
    return errs


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: validate_learning.py <path>\n")
        return 2
    try:
        errs = validate(argv[1])
    except (OSError, UnicodeDecodeError) as e:
        sys.stderr.write("%s: unreadable: %s\n" % (argv[1], e))
        return 2
    for n, msg in sorted(errs):
        sys.stderr.write("%s:%d: %s\n" % (argv[1], n, msg))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
