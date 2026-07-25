#!/usr/bin/env python3
"""Validate a PRD file against spec 03 (docs/specs/workflow/03-write-prd.md)."""
import os, re, sys

SLUG = r"[a-z0-9]+(?:-[a-z0-9]+)*"
FILENAME_RE = re.compile(r"^prd-([0-9]{3})-(%s)\.md$" % SLUG)
H1_RE = re.compile(r"^# (.+)$")
H2_RE = re.compile(r"^## (.+)$")
H3_RE = re.compile(r"^### (.+)$")
REQ_HEAD_RE = re.compile(r"^### (R-[0-9]+) — (.+)$")
KEY_RE = re.compile(r"^- ([A-Za-z][A-Za-z ]*): ?(.*)$")
NESTED_RE = re.compile(r"^  +- (.*)$")
INDENTED_RE = re.compile(r"^\s+\S")
RETIRED_RE = re.compile(r"^- Retired: (R-[0-9]+(?:, R-[0-9]+)*)$")
REQUIRED = ["Purpose", "Users", "Non-goals", "Constraints", "Success criteria", "Requirements"]
PLACEHOLDERS = {"tbd", "todo"}

def is_placeholder(v):
    return v.strip().lower() in PLACEHOLDERS

def rid_value(tok):
    """Return the numeric ID for a legal R-token, else None."""
    digits = tok[2:]
    if len(digits) == 2 and digits != "00":
        return int(digits)
    if len(digits) > 2 and not digits.startswith("0"):
        return int(digits)
    return None

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
    if not FILENAME_RE.match(os.path.basename(path)) or os.path.basename(path).startswith("prd-000-"):
        errs.append((1, "filename must match prd-NNN-<slug>.md (NNN 001-999)"))
    with open(path, encoding="utf-8") as f:
        lines = list(logical_lines(f.read()))
    content = [(n, l) for n, l, fenced in lines if not fenced]

    h1s = [(n, l) for n, l in content if H1_RE.match(l)]
    first_content = next((n for n, l, fenced in lines if l.strip()), None)
    if not h1s:
        errs.append((1, "missing H1 title"))
    else:
        if len(h1s) > 1:
            errs.append((h1s[1][0], "more than one H1"))
        if first_content != h1s[0][0]:
            errs.append((h1s[0][0], "H1 is not the first content line"))

    h2s = [(n, H2_RE.match(l).group(1).strip()) for n, l in content if H2_RE.match(l)]
    titles = [t for _, t in h2s]
    for req in REQUIRED:
        if titles.count(req) == 0:
            errs.append((1, "missing required section: %s" % req))
        elif titles.count(req) > 1:
            errs.append((h2s[[i for i, t in enumerate(titles) if t == req][1]][0], "duplicate section: %s" % req))
    present = [t for t in titles if t in REQUIRED]
    if present != [r for r in REQUIRED if r in titles]:
        errs.append((h2s[0][0] if h2s else 1, "required sections out of order"))
    known_idx = [i for i, t in enumerate(titles) if t in REQUIRED]
    if known_idx and any(i < known_idx[-1] for i, t in enumerate(titles) if t not in REQUIRED):
        n = next(h2s[i][0] for i, t in enumerate(titles) if t not in REQUIRED and i < known_idx[-1])
        errs.append((n, "unknown section before the required six"))

    bounds = {}
    for i, (n, t) in enumerate(h2s):
        end = h2s[i + 1][0] if i + 1 < len(h2s) else len(lines) + 1
        bounds.setdefault(t, (n, end))
    for req in REQUIRED:
        if req not in bounds or req == "Requirements":
            continue
        start, end = bounds[req]
        if not any(l.strip() for n, l, fenced in lines if start < n < end):
            errs.append((start, "section is empty: %s" % req))

    if "Requirements" in bounds:
        errs.extend(check_requirements(lines, bounds["Requirements"]))
    return errs

def check_requirements(lines, span):
    errs = []
    start, end = span
    live, retired = [], []
    seen_tombstone = None
    block = None          # dict(id, n, keys=[(key, val, n)], acc_bullets=[(n, v)])
    blocks = []
    last_key = None
    body = [(n, l, fenced) for n, l, fenced in lines if start < n < end]
    if not any(l.strip() for n, l, fenced in body):
        errs.append((start, "section is empty: Requirements"))
    for n, l, fenced in body:
        if fenced or not l.strip():
            continue
        m = RETIRED_RE.match(l)
        if l.startswith("- Retired:") and not m:
            errs.append((n, "malformed Retired line"))
            continue
        if m:
            if seen_tombstone is not None:
                errs.append((n, "more than one Retired line"))
            elif blocks:
                errs.append((n, "Retired line must precede the first requirement"))
            else:
                seen_tombstone = n
                toks = m.group(1).split(", ")
                vals = []
                for t in toks:
                    v = rid_value(t)
                    if v is None:
                        errs.append((n, "illegal retired ID: %s" % t))
                    else:
                        vals.append(v)
                if vals != sorted(set(vals)):
                    errs.append((n, "Retired list must be ascending without duplicates"))
                retired = vals
            continue
        h3 = H3_RE.match(l)
        if h3:
            m2 = REQ_HEAD_RE.match(l)
            v = rid_value(m2.group(1)) if m2 else None
            if v is None:
                errs.append((n, "requirement heading must match '### R-NN — <title>'"))
                block = {"id": None, "n": n, "keys": [], "acc": []}
            else:
                block = {"id": v, "n": n, "keys": [], "acc": []}
                live.append((n, v))
            blocks.append(block)
            last_key = None
            continue
        km = KEY_RE.match(l)
        if km:
            if block is None:
                errs.append((n, "key line outside any requirement block"))
                continue
            block["keys"].append((km.group(1), km.group(2), n))
            last_key = km.group(1)
            continue
        if INDENTED_RE.match(l):
            if block is None or last_key is None:
                errs.append((n, "indented content without a preceding key"))
            elif last_key == "Acceptance":
                nm = NESTED_RE.match(l)
                if nm is not None:
                    block["acc"].append((n, nm.group(1)))
            continue
        errs.append((n, "Requirements section contains non-requirement content"))

    ids = [v for _, v in live]
    if ids != sorted(ids) or len(ids) != len(set(ids)):
        errs.append((live[0][0] if live else start, "live requirement IDs must be unique and strictly ascending"))
    overlap = set(ids) & set(retired)
    if overlap:
        errs.append((seen_tombstone or start, "retired IDs collide with live IDs: %s" % sorted(overlap)))
    union = sorted(set(ids) | set(retired))
    if union and union != list(range(1, union[-1] + 1)):
        errs.append((start, "live and retired IDs must cover R-01..R-%02d with no gaps" % union[-1]))

    for b in blocks:
        stmts = [(v, n) for k, v, n in b["keys"] if k == "Statement"]
        accs = [(v, n) for k, v, n in b["keys"] if k == "Acceptance"]
        if not stmts:
            errs.append((b["n"], "requirement missing Statement"))
        else:
            if len(stmts) > 1:
                errs.append((stmts[1][1], "duplicate Statement"))
            if not stmts[0][0].strip():
                errs.append((stmts[0][1], "Statement is empty"))
            elif is_placeholder(stmts[0][0]):
                errs.append((stmts[0][1], "Statement is a placeholder"))
        if not accs:
            errs.append((b["n"], "requirement missing Acceptance"))
        else:
            if len(accs) > 1:
                errs.append((accs[1][1], "duplicate Acceptance"))
            if stmts and accs and stmts[0][1] > accs[0][1]:
                errs.append((stmts[0][1], "Statement must precede Acceptance"))
            if not b["acc"]:
                errs.append((accs[0][1], "Acceptance has no nested bullets"))
            for n, v in b["acc"]:
                if not v.strip():
                    errs.append((n, "acceptance bullet is empty"))
                elif is_placeholder(v):
                    errs.append((n, "acceptance bullet is a placeholder"))
    return errs

def main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: validate_prd.py <path>\n")
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
