#!/usr/bin/env python3
"""Cross-artifact coverage check: every live REQ in exactly one milestone.

Spec: docs/specs/workflow/04-prd-to-milestones.md. Stdlib only, Python 3.9+.
Exit 0 pass; 1 with "path:line: message" per violation; 2 on usage error,
unreadable input, a ROADMAP failing validate_roadmap, or a PRD failing
REQ extraction (the session contract gates validate_prd/validate_roadmap
first, so malformed inputs are environment errors here).
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate_roadmap import parse, validate, CITATION  # noqa: E402

PRD_FILENAME = re.compile(r"^prd-([0-9]{3})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
REQ_HEAD = re.compile(r"^### (REQ-[0-9]{3}) — .+$")
RETIRED = re.compile(r"^- Retired: (REQ-[0-9]{3}(?:, REQ-[0-9]{3})*)$")


def extract_prd(path):
    """Return (prd_id, {req_id: line}, retired_set). Raises ValueError if nothing extractable."""
    name = os.path.basename(path)
    m = PRD_FILENAME.match(name)
    if not m or m.group(1) == "000":
        raise ValueError("filename does not match prd-NNN-<slug>.md")
    live, retired = {}, set()
    fence = False
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh.read().split("\n"), 1):
            if line.strip().startswith("```"):
                fence = not fence
                continue
            if fence:
                continue
            h = REQ_HEAD.match(line)
            if h:
                live[h.group(1)] = n
                continue
            r = RETIRED.match(line)
            if r:
                retired.update(t.strip() for t in r.group(1).split(","))
    if not live and not retired:
        raise ValueError("no REQ headings or Retired line found")
    return "PRD-" + m.group(1), live, retired


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: check_coverage.py <path-to-ROADMAP.md>\n")
        return 2
    roadmap = argv[1]
    try:
        road_errs = validate(roadmap)
    except (OSError, UnicodeDecodeError) as e:
        sys.stderr.write("%s: unreadable: %s\n" % (roadmap, e))
        return 2
    if road_errs:
        sys.stderr.write("%s: fails validate_roadmap; fix it first:\n" % roadmap)
        for e in road_errs:
            sys.stderr.write(e + "\n")
        return 2

    prd_dir = os.path.join(os.path.dirname(os.path.abspath(roadmap)), "docs", "prd")
    prds = {}   # "PRD-001" -> (path, {"REQ-001": line}, retired)
    if os.path.isdir(prd_dir):
        for name in sorted(os.listdir(prd_dir)):
            if not name.startswith("prd-"):
                continue
            path = os.path.join(prd_dir, name)
            try:
                pid, live, retired = extract_prd(path)
            except ValueError as e:
                sys.stderr.write("%s: %s\n" % (path, e))
                return 2
            prds[pid] = (path, live, retired)

    with open(roadmap, encoding="utf-8") as fh:
        _, milestones, _ = parse(fh.read().splitlines())

    errs = []
    cited = {}
    for m in milestones:
        val, n = m.keys.get("Covers", ("", m.line))
        for c in CITATION.finditer(val):
            pid, rid = "PRD-" + c.group(1), "REQ-" + c.group(2)
            cited[(pid, rid)] = n
            if pid not in prds:
                errs.append((roadmap, n, "milestone %s cites nonexistent PRD %s" % (m.id, pid)))
                continue
            path, live, retired = prds[pid]
            if rid in retired:
                errs.append((roadmap, n, "milestone %s cites retired %s %s" % (m.id, pid, rid)))
            elif rid not in live:
                errs.append((roadmap, n, "milestone %s cites nonexistent REQ %s %s" % (m.id, pid, rid)))

    for pid, (path, live, retired) in sorted(prds.items()):
        for rid, line in sorted(live.items()):
            if (pid, rid) not in cited:
                errs.append((path, line, "%s %s is not covered by any milestone" % (pid, rid)))

    for path, n, msg in errs:
        sys.stderr.write("%s:%d: %s\n" % (path, n, msg))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
