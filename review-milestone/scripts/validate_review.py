#!/usr/bin/env python3
"""Validate a docs/reviews/milestone-NNN.md review record against spec 08.

Stdlib only, Python 3.9+. Exit 0 pass; 1 with "path:line: message" per
violation; 2 on usage error or unreadable file. A trailing pass without a
Verdict is valid mid-review; Verdict-terminated passes must be complete.
"""
import os
import re
import sys

FILENAME = re.compile(r"^milestone-([0-9]{3})\.md$")
H1 = re.compile(r"^# Review: MS-([0-9]{3}) — (.+)$")
SWEEP = re.compile(r"^## Sweep: ([a-z-]+)$")
VERDICT_HEAD = "## Verdict"
FINDING = re.compile(r"^- F([0-9]+): (.+)$")
DISPO = re.compile(r"^- Disposition: ?(.*)$")
FINDING_DISPO = re.compile(
    r"^(fixed|refuted\(.+\)|fix-feature\(FEAT-[0-9]{3}\)|accepted-known-issue\(.+\)|skipped\(.+\))$")
VERDICT_LINE = re.compile(r"^- Verdict: (accept|remediate)$")
DATE_LINE = re.compile(r"^- Date: ?(.*)$")
ORDER = ["learnings", "adr-audit", "backlog-triage", "integration-review", "three-c", "demo"]


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
    m = FILENAME.match(name)
    file_num = None
    if not m or m.group(1) == "000":
        errs.append((1, "filename must match milestone-NNN.md (NNN 001-999)"))
    else:
        file_num = m.group(1)
    with open(path, encoding="utf-8") as fh:
        content = [(n, l) for n, l, fenced in logical_lines(fh.read()) if not fenced]

    first = next(((n, l) for n, l in content if l.strip()), None)
    h1 = H1.match(first[1]) if first else None
    if not first or not h1:
        errs.append((first[0] if first else 1, "first content line must be '# Review: MS-NNN — <title>'"))
    elif file_num and h1.group(1) != file_num:
        errs.append((first[0], "H1 number MS-%s does not match filename milestone-%s" % (h1.group(1), file_num)))

    # sections: list of dicts {kind: 'sweep'|'verdict', item, line, rows:[(n,l)]}
    sections = []
    cur = None
    for n, l in content:
        sw = SWEEP.match(l)
        if sw:
            cur = {"kind": "sweep", "item": sw.group(1), "line": n, "rows": []}
            sections.append(cur)
            continue
        if l.strip() == VERDICT_HEAD:
            cur = {"kind": "verdict", "item": None, "line": n, "rows": []}
            sections.append(cur)
            continue
        if l.startswith("## "):
            errs.append((n, "unknown section heading in review record"))
            cur = None
            continue
        if cur is not None and l.strip():
            cur["rows"].append((n, l))

    # split into passes at each verdict section
    passes = []
    acc = []
    for s in sections:
        acc.append(s)
        if s["kind"] == "verdict":
            passes.append(acc)
            acc = []
    trailing = acc  # may be empty (file ends at a verdict) or a mid-review pass

    if not passes and not trailing:
        errs.append((1, "no sweep sections found"))

    def check_sweep_section(s):
        pending = None  # line of a finding awaiting its disposition
        last_dispo = None
        for n, l in s["rows"]:
            if FINDING.match(l):
                if pending is not None:
                    errs.append((pending, "finding lacks a Disposition line"))
                pending = n
                last_dispo = None
                continue
            d = DISPO.match(l)
            if d:
                val = d.group(1).strip()
                if not val:
                    errs.append((n, "empty Disposition"))
                elif pending is not None and not FINDING_DISPO.match(val):
                    errs.append((n, "illegal finding disposition '%s'" % val))
                pending = None
                last_dispo = n
        if pending is not None:
            errs.append((pending, "finding lacks a Disposition line"))
        if last_dispo is None or (s["rows"] and not DISPO.match(s["rows"][-1][1])):
            errs.append((s["line"], "sweep section must end with a Disposition line"))
        return [d.group(1).strip() for _, l in s["rows"] for d in [DISPO.match(l)] if d]

    def check_pass(p, is_terminated):
        sweeps = [s for s in p if s["kind"] == "sweep"]
        items = [s["item"] for s in sweeps]
        for it in items:
            if it not in ORDER:
                errs.append((next(s["line"] for s in sweeps if s["item"] == it), "unknown sweep item '%s'" % it))
        known = [it for it in items if it in ORDER]
        expected = [it for it in ORDER if it in known]
        if known != expected:
            errs.append((sweeps[0]["line"] if sweeps else p[0]["line"], "sweep sections out of order"))
        dispos = []
        for s in sweeps:
            dispos.extend(check_sweep_section(s))
        if is_terminated:
            v = p[-1]
            if not sweeps:
                errs.append((v["line"], "Verdict without any sweep sections in this pass"))
            missing = [it for it in ORDER if it not in items]
            if missing and sweeps:
                errs.append((v["line"], "Verdict written but sweep items missing: %s" % ", ".join(missing)))
            vlines = [(n, l) for n, l in v["rows"] if l.startswith("- Verdict:")]
            if len(vlines) != 1 or not VERDICT_LINE.match(vlines[0][1] if vlines else ""):
                errs.append((v["line"], "Verdict section needs exactly one '- Verdict: accept | remediate'"))
                verdict = None
            else:
                verdict = VERDICT_LINE.match(vlines[0][1]).group(1)
            dates = [(n, l) for n, l in v["rows"] if DATE_LINE.match(l)]
            if not dates or not DATE_LINE.match(dates[0][1]).group(1).strip():
                errs.append((v["line"], "Verdict section needs a non-empty '- Date:'"))
            if verdict == "accept" and any(d.startswith("fix-feature(") for d in dispos):
                errs.append((v["line"], "fix-feature dispositions are illegal in an accept verdict"))
        else:
            # mid-review: in-order prefix only
            if known != [it for it in ORDER[:len(known)]]:
                errs.append((sweeps[0]["line"] if sweeps else 1, "mid-review sections must be an in-order prefix of the sweep list"))

    for p in passes:
        check_pass(p, True)
    if trailing:
        if trailing[0]["kind"] != "sweep" or (passes and trailing[0]["item"] != "learnings"):
            errs.append((trailing[0]["line"], "content after a Verdict must begin a new pass at '## Sweep: learnings'"))
        check_pass(trailing, False)
    return errs


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: validate_review.py <path>\n")
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
